import os
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import settings
from backend.agents.orchestrator import SwarmOrchestrator
from backend.db.journal import DecisionJournal

app = FastAPI(
    title=settings.APP_TITLE,
    description="Offline-First Adversarial Indian Market Intelligence Desktop App",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = SwarmOrchestrator()
journal = DecisionJournal()

class AnalyzeRequest(BaseModel):
    query: str
    tone_level: int = 3
    provider: Optional[str] = None

class ConfigUpdateRequest(BaseModel):
    active_provider: Optional[str] = None
    groq_api_key: Optional[str] = None
    default_local_model: Optional[str] = None

@app.post("/api/analyze")
def analyze_thesis(req: AnalyzeRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    try:
        res = orchestrator.process_investment_query(req.query, tone_level=req.tone_level)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
def get_history(limit: int = 20):
    return journal.list_recent_decisions(limit=limit)

@app.get("/api/history/{session_id}")
def get_decision_details(session_id: str):
    res = journal.get_decision_by_id(session_id)
    if not res:
        raise HTTPException(status_code=404, detail="Decision record not found")
    return res

@app.get("/api/config")
def get_config():
    return {
        "active_provider": settings.ACTIVE_PROVIDER,
        "default_local_model": settings.DEFAULT_LOCAL_MODEL,
        "groq_model": settings.GROQ_MODEL,
        "has_groq_key": bool(settings.GROQ_API_KEY),
        "ollama_url": settings.OLLAMA_BASE_URL
    }

@app.post("/api/config")
def update_config(req: ConfigUpdateRequest):
    if req.active_provider:
        settings.ACTIVE_PROVIDER = req.active_provider
    if req.groq_api_key is not None:
        settings.GROQ_API_KEY = req.groq_api_key
    if req.default_local_model:
        settings.DEFAULT_LOCAL_MODEL = req.default_local_model
    return {"status": "ok", "config": get_config()}

# Mount Static Frontend
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
FRONTEND_DIR.mkdir(exist_ok=True)
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
