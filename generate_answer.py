# Generate Final Answer using Retrieved Context (RAG)

import os
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
import ollama

# ---------- Paths & Cache ----------
BASE_DIR = Path(__file__).resolve().parent
db_path = BASE_DIR / "chroma_db"

# ---------- Load Vector DB ----------
client = chromadb.PersistentClient(path=str(db_path))
collection = client.get_or_create_collection(name="legal_laws")

# ---------- Load Embedding Model ----------
model = SentenceTransformer("all-MiniLM-L6-v2")

# ---------- User Question ----------
query = input("❓ Apna legal question likho: ")

# ---------- Retrieve Context ----------
query_embedding = model.encode(query).tolist()
results = collection.query(query_embeddings=[query_embedding], n_results=1)
context = results["documents"][0][0]

# ---------- Prompt (Legal-Safe) ----------
prompt = f"""
You creat By Dhruv Kaushik,
You are an Indian legal assistant.
Answer ONLY using the context provided.
If the context is insufficient, say you are not sure.
You MUST mention the IPC Section number clearly in your answer.

Context:
{context}

Question:
{query}

Rules:
- Keep the answer simple and clear.
- Do NOT give legal advice.
- Add this disclaimer at the end:
"This is for educational purposes only. Consult a licensed lawyer for legal advice."
"""

# ---------- Generate Answer ----------
response = ollama.chat(
    model="mistral",
    messages=[{"role": "user", "content": prompt}]
)

print("\n🧠 Final Answer:\n")
print(response["message"]["content"])
