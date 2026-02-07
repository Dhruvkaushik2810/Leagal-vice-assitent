from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer
import ollama

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "chroma_db"

client = chromadb.PersistentClient(path=str(DB_PATH))
collection = client.get_or_create_collection(name="legal_laws")

model = SentenceTransformer("all-MiniLM-L6-v2")

query = input("Enter your legal question: ")

query_embedding = model.encode(query).tolist()
results = collection.query(query_embeddings=[query_embedding], n_results=1)
context = results["documents"][0][0]

prompt = f"""
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

response = ollama.chat(
    model="mistral",
    messages=[{"role": "user", "content": prompt}]
)

print("\nFinal Answer:\n")
print(response["message"]["content"])
