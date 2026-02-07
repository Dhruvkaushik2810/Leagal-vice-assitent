# Legal Voice Assistant
Legal Voice Assistant is an offline-first, voice-based system that helps users understand basic legal rights, procedures, and next steps through spoken interaction. It uses local legal text (IPC), local speech recognition (Vosk), and a local LLM via Ollama to generate clear, structured guidance. It is for legal awareness and education only and does not replace professional legal advice.

## What This Project Does
- Converts speech to text using Vosk (offline).
- Retrieves the most relevant IPC section from a local Chroma vector database.
- Uses a local LLM (Ollama, default model `mistral`) to generate a structured answer.
- Speaks the answer back using `pyttsx3` (offline).
- Provides a web UI (Flask) and a desktop UI (Tkinter).

## Architecture Flow
1) User speaks or types a question.
2) Vosk converts voice to text (voice mode only).
3) SentenceTransformers embeds the question.
4) Chroma retrieves the most relevant IPC section.
5) Ollama generates a structured answer with the required disclaimer.
6) `pyttsx3` speaks the response (voice mode only).

## Project Structure
- [web_app.py](web_app.py) - Flask web UI and API (`/ask`) for RAG responses.
- [voice_rag_assistant.py](voice_rag_assistant.py) - Full voice loop (STT -> RAG -> TTS).
- [voice_ui.py](voice_ui.py) - Desktop UI launcher for scripts.
- [voice_input.py](voice_input.py) - Standalone Vosk microphone test.
- [load_data.py](load_data.py) - Builds the vector database from IPC text.
- [vector_store.py](vector_store.py) - Retrieves relevant IPC section for a query.
- [generate_answer.py](generate_answer.py) - Generates a final answer using Ollama + retrieved context.
- [data/ipc.txt](data/ipc.txt) - Legal text source.
- [chroma_db/](chroma_db/) - Persistent vector database storage.
- [templates/index.html](templates/index.html) - Web UI.
- [static/](static/) - Web assets.
- [vosk-model-small-en-us-0.15/](vosk-model-small-en-us-0.15/) - Offline speech model.

## Requirements
- Windows 10/11
- Python 3.10+ recommended
- Ollama installed and running
- Vosk English model downloaded

## Installation
1) Create and activate a virtual environment.
2) Install dependencies:
```
pip install -r requirements.txt
```
3) Install and run Ollama, then pull the model:
```
ollama pull mistral
```
4) Place the Vosk model in the project root as:
```
vosk-model-small-en-us-0.15/
```
Download from https://alphacephei.com/vosk/models

## Build the Vector Database
Run once (or whenever you update [data/ipc.txt](data/ipc.txt)):
```
python load_data.py
```
This creates embeddings and stores them under [chroma_db/](chroma_db/).

## Run Options
### Web App (Flask)
```
python web_app.py
```
Open http://127.0.0.1:8000 in your browser.

### Voice Assistant (Full Loop)
```
python voice_rag_assistant.py
```
Speak normally. Say "band karo" or "exit" to stop.

### Desktop UI Launcher (Tkinter)
```
python voice_ui.py
```
This starts a UI to launch tools and the voice assistant.

### Quick CLI Tools
- Vector retrieval only:
```
python vector_store.py
```
- Generate answer from retrieved context:
```
python generate_answer.py
```
- Microphone test (STT only):
```
python voice_input.py
```

## Configuration Notes
- The LLM model name is set to `mistral` in [web_app.py](web_app.py) and [voice_rag_assistant.py](voice_rag_assistant.py).
- SentenceTransformers caches are stored under `.cache/` inside the project.
- Chroma persists data under [chroma_db/](chroma_db/).

## Disclaimer
This project provides educational guidance only. It is not legal advice. Always consult a licensed lawyer for legal advice.
