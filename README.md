# 🧠 AI Mental Health Assistant (Saathi MVP)

A startup-grade MVP backend + prototype UI for an AI-powered emotional support assistant.

## Current MVP Capabilities

- Text-first assistant flow with emotion detection and PHQ-9 severity estimation.
- Safety layer that flags crisis/self-harm language and returns India helpline escalation guidance.
- Therapeutic response template with empathetic, supportive language.
- Session logging to SQLite (`data/sessions.db`) for analytics, plus optional CSV journaling history.
- FastAPI endpoints that can be connected to STT/TTS layers next.

## API Endpoints

- `GET /health` → service health check with model availability flags.
- `POST /analyze` → emotion, severity, safety, and therapeutic response payload.
- `POST /save_journal` → manually persist journal text to CSV history.

### Example `POST /analyze` payload

```json
{
  "user_statement": "I feel overwhelmed and hopeless today",
  "phq9_responses": [
    "I have trouble sleeping",
    "I feel tired and down"
  ],
  "journal_text": "I need help calming down."
}
```

## Quick Start

```bash
pip install -r requirements.txt
uvicorn main:app --reload
streamlit run app.py
```

## Architecture (MVP)

```mermaid
flowchart TD
    User -->|Text / Voice (future)| STT
    STT --> NLP[Emotion + PHQ + Safety]
    NLP --> RESP[Therapeutic Response Engine]
    RESP --> TTS
    NLP --> DB[(SQLite + CSV Logs)]
```

## Notes

- STT/TTS are intentionally left pluggable so you can add Whisper + Coqui/ElevenLabs without changing core logic.
- If a PHQ model file is unavailable, the app falls back to a lightweight heuristic severity estimator.


### Health check example

```bash
curl http://127.0.0.1:8000/health
```
