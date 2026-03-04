from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from app_logic import mental_health_assistant, save_journal_entry

app = FastAPI(title="Saathi MVP API", version="0.1.0")


class AnalysisInput(BaseModel):
    user_statement: Optional[str] = ""
    phq9_responses: Optional[List[str]] = []
    journal_text: Optional[str] = ""


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
def analyze(data: AnalysisInput):
    return mental_health_assistant(
        user_statement=data.user_statement,
        phq9_responses=data.phq9_responses,
        journal_text=data.journal_text,
    )


@app.post("/save_journal")
def save_journal(data: AnalysisInput):
    save_journal_entry(
        user_statement=data.user_statement,
        journal_text=data.journal_text or "",
        emotions=["manual-entry"],
        severity="manual-entry",
    )
    return {"message": "Journal entry saved"}
