import json
import audioop
import time
from pathlib import Path

import pyaudio
import vosk
import webrtcvad
import pyttsx3
import chromadb
from sentence_transformers import SentenceTransformer
import ollama

# ================= PATHS =================
BASE_DIR = Path(__file__).resolve().parent
VOSK_MODEL = BASE_DIR / "vosk-model-small-en-us-0.15"
DB_PATH = BASE_DIR / "chroma_db"

# ================= CHECKS =================
if not VOSK_MODEL.exists():
    raise FileNotFoundError(f"Vosk model not found at {VOSK_MODEL}")

# ================= INIT =================
print("🔧 Initializing components...")

# ---------- AUDIO CONFIG ----------
SAMPLE_RATE = 16000
CHANNELS = 1
FRAME_DURATION_MS = 30
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)
FRAME_BYTES = FRAME_SIZE * 2
MAX_SILENCE_FRAMES = int(0.8 * 1000 / FRAME_DURATION_MS)
MIN_SPEECH_FRAMES = int(0.2 * 1000 / FRAME_DURATION_MS)
START_TIMEOUT_SECONDS = 6
NOISE_MULTIPLIER = 1.3
MIN_NOISE_FLOOR = 200

# Speech-to-Text
stt_model = vosk.Model(str(VOSK_MODEL))
rec = vosk.KaldiRecognizer(stt_model, SAMPLE_RATE)
rec.SetWords(True)

# VAD
vad = webrtcvad.Vad(1)

p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paInt16,
    channels=CHANNELS,
    rate=SAMPLE_RATE,
    input=True,
    frames_per_buffer=FRAME_SIZE
)
stream.start_stream()

def calibrate_noise(seconds: float = 1.0) -> int:
    frames = []
    end_time = time.time() + seconds
    while time.time() < end_time:
        data = stream.read(FRAME_SIZE, exception_on_overflow=False)
        frames.append(data)
    rms_values = [audioop.rms(f, 2) for f in frames]
    base_noise = int(sum(rms_values) / max(1, len(rms_values)))
    return max(MIN_NOISE_FLOOR, int(base_noise * NOISE_MULTIPLIER))

print("🔈 Stay silent for calibration...")
time.sleep(0.3)
noise_threshold = calibrate_noise()

# Text-to-Speech
engine = pyttsx3.init()
engine.setProperty("rate", 170)

# Vector DB
client = chromadb.PersistentClient(path=str(DB_PATH))
collection = client.get_or_create_collection("legal_laws")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# LLM settings
MODEL_NAME = "mistral"
MAX_HISTORY_TURNS = 6
chat_history = []

print("✅ Voice Legal Agent READY")
print(f"🔇 Noise threshold: {noise_threshold}")
print("👉 Bolo | Band karne ke liye 'band karo'\n")

# ================= FUNCTIONS =================
def listen():
    speech_frames = []
    silence_frames = 0
    started = False
    start_time = time.time()

    while True:
        frame = stream.read(FRAME_SIZE, exception_on_overflow=False)
        is_speech = vad.is_speech(frame, SAMPLE_RATE)
        rms = audioop.rms(frame, 2)

        is_loud = rms >= noise_threshold
        if is_speech or is_loud:
            if not started:
                started = True
            speech_frames.append(frame)
            silence_frames = 0
        elif started:
            silence_frames += 1
            if silence_frames >= MAX_SILENCE_FRAMES:
                break
        elif time.time() - start_time > START_TIMEOUT_SECONDS:
            return ""

    if len(speech_frames) < MIN_SPEECH_FRAMES:
        return ""

    rec.Reset()
    for f in speech_frames:
        rec.AcceptWaveform(f)
    return json.loads(rec.FinalResult()).get("text", "").strip()

def speak(text):
    print("🔊 Agent bol raha hai...")
    engine.say(text)
    engine.runAndWait()

def _history_text() -> str:
    if not chat_history:
        return ""
    lines = []
    for item in chat_history[-MAX_HISTORY_TURNS:]:
        role = item.get("role", "user")
        content = item.get("content", "")
        lines.append(f"{role.capitalize()}: {content}")
    return "\n".join(lines)

def rag_answer(query):
    print("🧠 RAG thinking...")
    if len(query.split()) < 4:
        return (
            "Please share more details so I can guide you. "
            "For example: what happened, where, when, who is involved, and what outcome you want."
        )
    q_emb = embedder.encode(query).tolist()
    res = collection.query(query_embeddings=[q_emb], n_results=1)
    context = res["documents"][0][0]

    history = _history_text()

    prompt = f"""
You are an Indian legal assistant.
Use ONLY the context below.
You MUST mention IPC Section number.
Your job is to help the user understand their situation and guide them with next steps.
If details are missing, ask 3 short clarification questions first.
Keep the response simple, structured, and practical.

Format:
1) Summary of the situation in 1-2 lines.
2) Relevant IPC section(s).
3) What the user can do next (3-5 bullet steps).
4) Clarifying questions (if needed).
5) End with the exact disclaimer sentence.

Context:
{context}

Conversation so far:
{history}

Question:
{query}

End with exactly:
This is for educational purposes only. Consult a licensed lawyer for legal advice.
"""

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]
    except Exception as exc:
        err_text = str(exc).lower()
        if "cuda" in err_text or "gpu" in err_text:
            try:
                response = ollama.chat(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    options={"num_gpu": 0}
                )
                return response["message"]["content"]
            except Exception:
                return (
                    "Ollama GPU error. Start Ollama in CPU mode and retry."
                )
        return "LLM error. Please retry."

# ================= MAIN LOOP =================
try:
    while True:
        print("🎧 Listening...")
        query = listen()
        print("🗣️ You said:", query)

        if not query:
            continue

        if "band karo" in query or "exit" in query:
            speak("Theek hai, main band ho raha hoon.")
            break

        answer = rag_answer(query)
        print("\n🧠 Agent Reply:\n", answer)
        speak(answer)
        chat_history.append({"role": "user", "content": query})
        chat_history.append({"role": "assistant", "content": answer})

except KeyboardInterrupt:
    print("\n🛑 Manually stopped")

finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
