import joblib
import torch
import os
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import RandomForestClassifier
from transformers import pipeline

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device set to use {device}")

# Load PHQ-9 model (adjusted path to work from backend/models/)
model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models", "phq9_nlp_model.pkl"))
try:
    phq9_text_model = joblib.load(model_path)
except FileNotFoundError:
    raise FileNotFoundError(f"❌ Model file not found at: {model_path}")

# Load sentence embedding model
sentence_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Load emotion detection model
emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=2)

# --- Utility Function: Save journal entry ---
def save_journal_entry(user_statement, journal_text, emotions, severity):
    if not journal_text.strip():
        return

    history_file = "mental_health_history.csv"
    file_exists = os.path.isfile(history_file)

    with open(history_file, mode="a", newline="", encoding="utf-8") as file:
        import csv
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["timestamp", "user_statement", "journal_text", "emotions", "severity"])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_statement,
            journal_text,
            ", ".join(emotions),
            severity
        ])

# --- Main Logic Function ---
def mental_health_assistant(user_statement, phq9_responses, journal_text=None):
    # 1. Emotion Detection
    emotion_outputs = emotion_classifier(user_statement)
    top_emotions = [label["label"] for label in emotion_outputs[0]]

    # 2. PHQ-9 Severity Prediction (if responses given)
    phq9_text = [resp for resp in phq9_responses if resp.strip()]
    if phq9_text:
        embeddings = sentence_model.encode([" ".join(phq9_text)])
        severity = phq9_text_model.predict(embeddings)[0]
    else:
        severity = "Unknown"

    # 3. Activity Suggestion
    suggestions = {
        "Minimal": "Keep up the good work! Maintain healthy habits.",
        "Mild": "Try light mindfulness or short walks to elevate your mood.",
        "Moderate": "Consider guided journaling or a conversation with a friend.",
        "Moderately Severe": "Seek professional help or use CBT exercises.",
        "Severe": "Contact a mental health professional immediately.",
        "Unknown": "Please fill in at least some PHQ-9 responses for a better assessment."
    }

    # 4. Journaling Prompt
    prompts = {
        "Minimal": "What made you feel good recently?",
        "Mild": "Reflect on a time you overcame a challenge. How did you feel?",
        "Moderate": "Write about what's been weighing on your mind lately.",
        "Moderately Severe": "Explore any recurring thoughts you’ve had.",
        "Severe": "Describe your feelings in detail and consider seeking help.",
        "Unknown": "Start by sharing anything on your mind today."
    }

    # 5. Save journal entry
    if journal_text:
        save_journal_entry(user_statement, journal_text, top_emotions, severity)

    return {
        "emotions": top_emotions,
        "phq9_severity": severity,
        "summary": f"The user shows {', '.join(top_emotions)} and a PHQ-9 severity of '{severity}'.",
        "activity": suggestions.get(severity, ""),
        "prompt": prompts.get(severity, "")
    }
