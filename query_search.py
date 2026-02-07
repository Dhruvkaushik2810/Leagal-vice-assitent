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

DB_PATH = BASE_DIR / "chroma_db"
client = chromadb.PersistentClient(path=str(DB_PATH))
collection = client.get_or_create_collection(name="legal_laws")

model = SentenceTransformer("all-MiniLM-L6-v2")

query = input("Enter your legal question: ")
query_embedding = model.encode(query).tolist()

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=1
)

print("\nMost Relevant Legal Section:\n")
print(results["documents"][0][0])
