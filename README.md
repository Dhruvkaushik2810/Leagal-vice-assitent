# Leagal-vice-assitent
Legal Voice Assistant is an offline, voice-based system that helps users understand basic legal rights, procedures, and next steps through spoken interaction. It is designed for legal awareness and education, providing simple, step-by-step guidance without replacing professional legal advice.

## Offline Flow (Step by Step)
1) User bolta hai (voice input)
2) Speech-to-Text se voice → text (Vosk offline)
3) User ka question milta hai
4) Question ke basis par local legal documents se relevant content LangChain se nikala jata hai
5) Relevant law + question ko final answer me organize kiya jata hai
6) Answer generate hota hai
7) Text-to-Speech se answer → voice (pyttsx3 offline)
8) User ko bol ke jawab milta hai

## Folder Structure
- [app/main.py](app/main.py) — main offline assistant (LangChain retrieval)
- [data/docs](data/docs) — aapke legal .txt documents
- [requirements.txt](requirements.txt) — offline libraries

## Setup (E: drive only)
1) Is project ko E: drive me hi rakhein (aap already yahan ho).
2) Python venv ko E: drive me banayein: e:\project\Leagal-vice-assitent\.venv
3) [requirements.txt](requirements.txt) install karein (LangChain + FAISS + sentence-transformers).
4) Vosk offline model download karke E: drive me rakhein. Example path:
	e:\project\Leagal-vice-assitent\models\vosk-model-small-en-us-0.15
	(Model website: https://alphacephei.com/vosk/models)
5) Apne legal documents ko [data/docs](data/docs) me .txt format me add karein.

## Run
Python se run karte waqt model ka path dena zaruri hai:
python app/main.py --model e:\project\Leagal-vice-assitent\models\vosk-model-small-en-us-0.15

## Notes
- Ye project fully offline hai (kisi free API ki zarurat nahi).
- Generative LLM abhi add nahi kiya; abhi retrieval + template answer hai. Chahe to local LLM (llama.cpp) add kar sakte ho.
- Ye educational guidance deta hai, legal advice nahi.
