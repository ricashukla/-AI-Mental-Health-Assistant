import csv
import joblib
import os
import sqlite3
from datetime import datetime
from typing import Dict, List

from sentence_transformers import SentenceTransformer
from transformers import pipeline


MODEL_CANDIDATE_PATHS = [
    os.path.join(os.path.dirname(__file__), "phq9_nlp_model.pkl"),
    os.path.join(os.path.dirname(__file__), "models", "phq9_nlp_model.pkl"),
]


def _load_phq_model():
    for candidate in MODEL_CANDIDATE_PATHS:
        if os.path.isfile(candidate):
            return joblib.load(candidate)
    return None


phq9_text_model = _load_phq_model()
try:
    sentence_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
except Exception:
    sentence_model = None

try:
    emotion_classifier = pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base",
        top_k=2,
    )
except Exception:
    emotion_classifier = None

CRISIS_KEYWORDS = {
    "kill myself",
    "want to die",
    "end my life",
    "suicide",
    "self harm",
    "hurt myself",
    "better off dead",
}

HELPLINES_INDIA = [
    "Tele-MANAS (24x7): 14416 or 1-800-891-4416",
    "AASRA (24x7): +91-22-27546669",
]


def _detect_crisis(text: str) -> bool:
    normalized = text.lower()
    return any(keyword in normalized for keyword in CRISIS_KEYWORDS)


def _mood_score(emotions: List[str]) -> int:
    weight = {
        "joy": 80,
        "neutral": 60,
        "surprise": 55,
        "fear": 35,
        "anger": 30,
        "sadness": 20,
        "disgust": 25,
    }
    if not emotions:
        return 50
    values = [weight.get(item.lower(), 50) for item in emotions]
    return round(sum(values) / len(values))


def _predict_severity(phq9_responses: List[str]) -> str:
    phq9_text = [response for response in phq9_responses if response.strip()]
    if not phq9_text:
        return "Unknown"

    if phq9_text_model is not None and sentence_model is not None:
        embeddings = sentence_model.encode([" ".join(phq9_text)])
        return phq9_text_model.predict(embeddings)[0]

    low_text = " ".join(phq9_text).lower()
    if any(term in low_text for term in ["hopeless", "worthless", "can't go on"]):
        return "Moderately Severe"
    if any(term in low_text for term in ["sad", "tired", "sleep"]):
        return "Mild"
    return "Minimal"


def _suggestions_for_severity(severity: str) -> Dict[str, str]:
    suggestions = {
        "Minimal": "Keep up the healthy routines and stay socially connected.",
        "Mild": "Try breathwork, short walks, and a check-in with someone you trust.",
        "Moderate": "Use guided journaling and consider speaking with a counselor.",
        "Moderately Severe": "Please seek professional support and prioritize sleep, food, and safety.",
        "Severe": "Reach out to emergency support and a licensed mental health professional immediately.",
        "Unknown": "Share a few PHQ-9 responses for a better depression severity estimate.",
    }
    prompts = {
        "Minimal": "What is one thing that gave you energy this week?",
        "Mild": "What thought has been repeating today, and what might challenge it?",
        "Moderate": "What feels hardest right now, and what support could reduce the load by 10%?",
        "Moderately Severe": "Write down what you need in the next 24 hours to feel safer.",
        "Severe": "List one person you can contact now and one helpline you can call.",
        "Unknown": "Describe your day in 3 sentences: body, mind, and emotions.",
    }
    return {
        "activity": suggestions.get(severity, suggestions["Unknown"]),
        "prompt": prompts.get(severity, prompts["Unknown"]),
    }


def generate_therapeutic_response(user_text: str, emotions: List[str], crisis: bool) -> str:
    if crisis:
        helplines = " | ".join(HELPLINES_INDIA)
        return (
            "I'm really glad you shared this. Your safety matters most right now. "
            f"Please contact immediate support: {helplines}. "
            "If possible, reach out to a trusted person and stay with them."
        )

    dominant = emotions[0] if emotions else "mixed emotions"
    return (
        f"Thank you for sharing. I can hear {dominant} in what you said. "
        "That sounds difficult, and you're not alone. "
        "Would a brief grounding exercise or a small next step feel helpful right now?"
    )


def save_session_entry(user_statement: str, emotions: List[str], severity: str, response_text: str):
    os.makedirs("data", exist_ok=True)
    db_path = os.path.join("data", "sessions.db")
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_statement TEXT,
                emotions TEXT,
                mood_score INTEGER,
                severity TEXT,
                response_text TEXT
            )
            """
        )
        conn.execute(
            """
            INSERT INTO sessions(timestamp, user_statement, emotions, mood_score, severity, response_text)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                user_statement,
                ", ".join(emotions),
                _mood_score(emotions),
                severity,
                response_text,
            ),
        )


def save_journal_entry(user_statement, journal_text, emotions, severity):
    if not journal_text.strip():
        return

    history_file = "mental_health_history.csv"
    file_exists = os.path.isfile(history_file)

    with open(history_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["timestamp", "user_statement", "journal_text", "emotions", "severity"])

        writer.writerow(
            [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                user_statement,
                journal_text,
                ", ".join(emotions),
                severity,
            ]
        )


def mental_health_assistant(user_statement, phq9_responses, journal_text=None):
    text = user_statement or "I am feeling neutral."
    if emotion_classifier is not None:
        emotion_outputs = emotion_classifier(text)
        top_emotions = [label["label"] for label in emotion_outputs[0]]
    else:
        top_emotions = ["neutral"]

    severity = _predict_severity(phq9_responses)
    guidance = _suggestions_for_severity(severity)
    crisis = _detect_crisis(text) or any(_detect_crisis(item) for item in phq9_responses)
    response_text = generate_therapeutic_response(text, top_emotions, crisis)

    if journal_text:
        save_journal_entry(user_statement, journal_text, top_emotions, severity)

    save_session_entry(user_statement, top_emotions, severity, response_text)

    result = {
        "emotions": top_emotions,
        "mood_score": _mood_score(top_emotions),
        "phq9_severity": severity,
        "summary": f"The user shows {', '.join(top_emotions)} with PHQ-9 severity '{severity}'.",
        "activity": guidance["activity"],
        "prompt": guidance["prompt"],
        "response": response_text,
        "safety": {
            "crisis_detected": crisis,
            "helplines": HELPLINES_INDIA if crisis else [],
        },
    }
    return result
