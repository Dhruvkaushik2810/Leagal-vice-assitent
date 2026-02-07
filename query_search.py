# STEP 4: Query Vector DB to Retrieve Relevant Law

import os
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

# Force all model/cache downloads to stay inside E: drive project
BASE_DIR = Path(__file__).resolve().parent
CACHE_DIR = BASE_DIR / ".cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("HF_HOME", str(CACHE_DIR / "hf"))
os.environ.setdefault("TRANSFORMERS_CACHE", str(CACHE_DIR / "hf"))
os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", str(CACHE_DIR / "sentence-transformers"))

db_path = BASE_DIR / "chroma_db"
client = chromadb.PersistentClient(path=str(db_path))
collection = client.get_or_create_collection(name="legal_laws")

model = SentenceTransformer("all-MiniLM-L6-v2")

query = input("❓ Apna legal question likho: ")

query_embedding = model.encode(query).tolist()

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=1
)

print("\n🔎 Most Relevant Legal Section:\n")
print(results["documents"][0][0])
