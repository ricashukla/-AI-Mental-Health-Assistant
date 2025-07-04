# 🧠 AI Mental Health Assistant

A compassionate AI-powered web application that helps users assess their mental health using PHQ-9 depression screening and emotion analysis through natural language processing. This assistant is designed to promote self-awareness, early mental health detection, and guided self-care.

---

## 🧩 Problem Statement

Mental health issues like depression often go undetected due to stigma, limited access to therapists, or lack of self-awareness. Early detection is key to managing symptoms before they worsen.

The goal of this project is to create a free, accessible AI assistant that:
- Assesses emotional well-being via text and PHQ-9 questionnaires.
- Provides empathetic responses and therapy suggestions.
- Encourages journaling and mental clarity through daily prompts.
- Can potentially escalate to professionals in severe cases.

---

## 💡 Solution Approach

We designed a hybrid interface (text + sliders) that collects user inputs and performs the following:

1. **Emotion Detection** — Extract emotion labels (e.g., sadness, joy, neutral).
2. **PHQ-9 Severity Prediction** — Analyze free-text responses to the 9 PHQ questions and classify the depression severity.
3. **Mental Health Summary** — Generate a summary with therapy suggestions.
4. **Journaling Prompt** — Display a context-aware journaling prompt.
5. **History Logging** — Save daily logs to CSV or Firebase (configurable).

---

## 🛠️ Tech Stack

| Layer | Tech |
|-------|------|
| 👩‍💻 Frontend | Streamlit (Python) |
| ⚙️ Backend | FastAPI |
| 🧠 NLP Models | Sentence-BERT (for PHQ-9), RoBERTa (for emotion) |
| 🧪 ML Classifier | Random Forest |
| 🗃️ History Storage | CSV (Local) |
| 📦 Deployment-ready | Streamlit + Uvicorn |

---

## 📊 Architecture & Pipeline

```text
[ User Input ]
     ↓
[ Streamlit Frontend ]
     ↓
[ FastAPI Backend ]
     ├── Emotion Detection (RoBERTa)
     ├── PHQ-9 Severity Classification (SBERT + RF)
     ├── Therapy Suggestion Engine
     ├── Journaling Prompt Generator
     ↓
[ Results → Streamlit UI + CSV/Firebase Save ]
