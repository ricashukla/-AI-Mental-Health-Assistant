from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class AnalysisInput(BaseModel):
    user_statement: Optional[str] = ""
    phq9_responses: Optional[List[str]] = []
    journal_text: Optional[str] = ""

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/analyze")
def analyze(data: AnalysisInput):
    from app_logic import mental_health_assistant

    result = mental_health_assistant(
        user_statement=data.user_statement,
        phq9_responses=data.phq9_responses,
        journal_text=data.journal_text
    )
    return result

@app.post("/api/save_journal")
def save_journal(data: AnalysisInput):
    from app_logic import save_journal_entry

    save_journal_entry(
        user_statement=data.user_statement,
        journal_text=data.journal_text or "",
        emotions=["manual-entry"],
        severity="manual-entry"
    )
    return {"message": "Journal entry saved"}
