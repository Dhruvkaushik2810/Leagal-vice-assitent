import json
import audioop
import time
from pathlib import Path

import pyaudio
import vosk
import webrtcvad

# ---------- PATH ----------
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "vosk-model-small-en-us-0.15"

# ---------- AUDIO CONFIG ----------
SAMPLE_RATE = 16000
CHANNELS = 1
FRAME_DURATION_MS = 30  # 10, 20, or 30 for webrtcvad
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)  # samples per frame
FRAME_BYTES = FRAME_SIZE * 2  # 16-bit audio
MAX_SILENCE_FRAMES = int(0.8 * 1000 / FRAME_DURATION_MS)
MIN_SPEECH_FRAMES = int(0.2 * 1000 / FRAME_DURATION_MS)
START_TIMEOUT_SECONDS = 6
NOISE_MULTIPLIER = 1.3
MIN_NOISE_FLOOR = 200

# ---------- LOAD MODEL ----------
model = vosk.Model(str(MODEL_PATH))
rec = vosk.KaldiRecognizer(model, SAMPLE_RATE)
rec.SetWords(True)

# ---------- VAD ----------
vad = webrtcvad.Vad(1)  # 0-3, higher = more aggressive noise filtering

# ---------- MIC ----------
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

print("🎤 English voice input started")
print("👉 Speak clearly | Say 'exit' to stop")
print(f"🔇 Noise threshold: {noise_threshold}\n")

def listen_once() -> str:
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
    result = json.loads(rec.FinalResult()).get("text", "").strip()
    return result

try:
    while True:
        print("🎧 Listening...")
        text = listen_once()

        if not text:
            continue

        print("🗣️ You said:", text)

        if "exit" in text:
            print("🛑 Exiting")
            break

except KeyboardInterrupt:
    print("\n🛑 Stopped")

finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
