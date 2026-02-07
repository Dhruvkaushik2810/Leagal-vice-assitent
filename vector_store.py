import os
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent
CACHE_DIR = BASE_DIR / ".cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("HF_HOME", str(CACHE_DIR / "hf"))
os.environ.setdefault("TRANSFORMERS_CACHE", str(CACHE_DIR / "hf"))
os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", str(CACHE_DIR / "sentence-transformers"))


def load_legal_data(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def chunk_by_section(text):
    lines = text.split("\n")
    chunks = []
    current_chunk = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("IPC Section"):
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = line
        else:
            current_chunk += " " + line

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


if __name__ == "__main__":
    text = load_legal_data("data/ipc.txt")
    chunks = chunk_by_section(text)

    print(f"Chunks loaded: {len(chunks)}")

    model = SentenceTransformer("all-MiniLM-L6-v2")

    db_path = BASE_DIR / "chroma_db"
    client = chromadb.PersistentClient(path=str(db_path))
    collection = client.get_or_create_collection(name="legal_laws")

    for i, chunk in enumerate(chunks):
        embedding = model.encode(chunk).tolist()

        collection.add(
            documents=[chunk],
            embeddings=[embedding],
            ids=[str(i)]
        )

    print("Embeddings created & stored in Vector DB")
