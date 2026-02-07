import os
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request, session
import chromadb
from sentence_transformers import SentenceTransformer
import ollama

# ================= PATHS =================
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "chroma_db"

# Force all model/cache downloads to stay inside project
CACHE_DIR = BASE_DIR / ".cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("HF_HOME", str(CACHE_DIR / "hf"))
os.environ.setdefault("TRANSFORMERS_CACHE", str(CACHE_DIR / "hf"))
os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", str(CACHE_DIR / "sentence-transformers"))

# ================= APP =================
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "local-demo-secret"

# ================= RAG =================
client = chromadb.PersistentClient(path=str(DB_PATH))
collection = client.get_or_create_collection("legal_laws")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

MODEL_NAME = "mistral"
MAX_HISTORY_TURNS = 6
SESSIONS = {}


def _get_session_id() -> str:
    if "sid" not in session:
        session["sid"] = str(uuid.uuid4())
    return session["sid"]


def _history_text(session_id: str) -> str:
    history = SESSIONS.get(session_id, [])
    if not history:
        return ""
    lines = []
    for item in history[-MAX_HISTORY_TURNS:]:
        role = item.get("role", "user")
        content = item.get("content", "")
        lines.append(f"{role.capitalize()}: {content}")
    return "\n".join(lines)


def rag_answer(query: str, session_id: str) -> str:
    if len(query.split()) < 4:
        return (
            "Please share more details so I can guide you. "
            "For example: what happened, where, when, who is involved, and what outcome you want."
        )

    q_emb = embedder.encode(query).tolist()
    res = collection.query(query_embeddings=[q_emb], n_results=1)
    context = res["documents"][0][0]

    history = _history_text(session_id)

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
                return "Ollama GPU error. Start Ollama in CPU mode and retry."
        return "LLM error. Please retry."


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(force=True)
    query = (data.get("query") or "").strip()
    if not query:
        return jsonify({"answer": "Please enter a question."})

    session_id = _get_session_id()
    answer = rag_answer(query, session_id)

    history = SESSIONS.setdefault(session_id, [])
    history.append({"role": "user", "content": query})
    history.append({"role": "assistant", "content": answer})

    return jsonify({"answer": answer})


if __name__ == "__main__":
    print("Starting server on http://0.0.0.0:8000")
    print("Open this on another device using your PC IP, for example: http://192.168.x.x:8000")
    app.run(host="0.0.0.0", port=8000, debug=False)
