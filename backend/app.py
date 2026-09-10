import os
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.config import settings
from backend.agents.orchestrator import SwarmOrchestrator
from backend.agents.simulator_agent import SimulatorAgent
from backend.scrapers.macro_client import MacroClient
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
    query: str = Field(..., min_length=2, max_length=500, description="User investment hypothesis")
    tone_level: int = Field(3, ge=1, le=6, description="Adversarial tone continuum from 1 to 6")
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

class SimulateRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20)
    scenario_type: str = Field(..., description="CRUDE_SURGE, RBI_RATE_HIKE, INR_DEPRECIATION, MARGIN_COMPRESSION")

@app.get("/api/macro/vix")
def get_vix_gauge():
    """Returns India VIX macro weather regime."""
    return MacroClient.get_vix_status()

@app.post("/api/simulate")
def run_scenario_simulation(req: SimulateRequest):
    """Stress-tests a symbol against macro and sector shocks."""
    try:
        res = SimulatorAgent.simulate(req.symbol, req.scenario_type)
        return res.model_dump()
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

@app.get("/api/export/{session_id}")
def export_pre_mortem_one_pager(session_id: str):
    """Generates an institutional-grade, printable HTML Pre-Mortem One-Pager."""
    record = journal.get_decision_by_id(session_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    pm = record.get("pre_mortem") or {}
    lkb = record.get("lkb_packet") or {}
    facts = lkb.get("facts", [])
    biases = pm.get("detected_biases", [])

    facts_rows = "".join([
        f"<tr><td><code>{f.get('id')}</code></td><td>{f.get('category')}</td><td><strong>{f.get('metric')}</strong></td><td>{f.get('value')} {f.get('unit', '')}</td><td>{f.get('source')}</td></tr>"
        for f in facts
    ])

    biases_html = "".join([
        f"<div class='bias-box'><strong>⚠️ {b.get('bias_name')} ({b.get('severity')} Severity)</strong><p><em>Trap:</em> {b.get('psychological_trap')}</p><p><em>Reframing:</em> {b.get('reframing_advice')}</p></div>"
        for b in biases
    ]) if biases else "<p>No prominent cognitive biases detected in user rationale.</p>"

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>FAIDA Pre-Mortem Audit - {record.get('symbol')}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.5; color: #111; max-width: 850px; margin: 40px auto; padding: 20px; }}
  .header {{ display: flex; justify-content: space-between; border-bottom: 2px solid #000; padding-bottom: 12px; margin-bottom: 20px; }}
  .title h1 {{ margin: 0; font-size: 24px; }}
  .meta {{ font-size: 13px; color: #555; }}
  .verdict-box {{ background: #fdf2f2; border-left: 5px solid #dc2626; padding: 15px; margin: 20px 0; }}
  .score {{ font-size: 28px; font-weight: bold; color: #dc2626; }}
  table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 12px; }}
  th, td {{ border: 1px solid #ddd; padding: 8px 10px; text-align: left; }}
  th {{ background: #f4f4f4; }}
  .checklist {{ background: #f8fafc; border: 1px solid #cbd5e1; padding: 15px; margin: 20px 0; }}
  .bias-box {{ background: #fffbeb; border: 1px solid #fef3c7; border-left: 4px solid #f59e0b; padding: 10px; margin: 8px 0; font-size: 13px; }}
  .signature-line {{ margin-top: 30px; display: flex; justify-content: space-between; font-size: 13px; }}
  .footer {{ margin-top: 40px; font-size: 11px; color: #777; border-top: 1px solid #eee; padding-top: 10px; }}
  @media print {{ body {{ margin: 10px; padding: 0; }} .no-print {{ display: none; }} }}
</style>
</head>
<body>
  <div class="no-print" style="margin-bottom: 20px;">
    <button onclick="window.print()" style="padding: 10px 20px; background: #000; color: #fff; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">🖨️ Print / Save as PDF</button>
  </div>
  <div class="header">
    <div class="title">
      <h1>FAIDA Institutional Pre-Mortem Audit</h1>
      <div class="meta">Red-Team Invalidation Report | Indian Capital Markets</div>
    </div>
    <div style="text-align: right;">
      <strong>{record.get('symbol')} ({record.get('exchange', 'NSE')})</strong><br>
      <span>Proposed Action: <strong>{record.get('action')}</strong></span><br>
      <span>Target: ₹{record.get('target_price') or 'Market'} | CMP: ₹{record.get('current_price') or 'N/A'}</span>
    </div>
  </div>

  <div class="verdict-box">
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h3 style="margin: 0 0 5px 0;">{pm.get('headline_verdict', 'Pre-Mortem Verdict')}</h3>
        <p style="margin: 0; font-size: 13px; color: #444;">Session: {session_id} | Date: {record.get('created_at')}</p>
      </div>
      <div class="score">{record.get('friction_score')}/100</div>
    </div>
  </div>

  <h3>1. Grounded Local Knowledge Base (Evidence Snapshot)</h3>
  <table>
    <thead><tr><th>ID</th><th>Category</th><th>Metric</th><th>Ground Value</th><th>Source</th></tr></thead>
    <tbody>{facts_rows}</tbody>
  </table>

  <h3>2. Cognitive Biases & Behavioral Traps Detected</h3>
  {biases_html}

  <h3>3. Invalidation & Stop-Loss Rules</h3>
  <ul>
    <li><strong>Stop-Loss Invalidation Level:</strong> ₹{pm.get('invalidation_levels', {}).get('invalidation_price', 'N/A')} (Exit discipline to avoid asymmetric drawdown).</li>
    <li><strong>Target Invalidation Resistance:</strong> ₹{pm.get('invalidation_levels', {}).get('take_profit_target', 'N/A')}</li>
  </ul>

  <div class="checklist">
    <h4 style="margin: 0 0 10px 0;">Mandatory Pre-Trade Invalidation Checklist</h4>
    <p><input type="checkbox"> Have I verified institutional delivery volume on NSE rather than intraday speculative churn?</p>
    <p><input type="checkbox"> Is my position size under 5% of my overall liquid equity portfolio?</p>
    <p><input type="checkbox"> Have I verified that the promoter has not pledged shares (>10%) on Screener.in?</p>
    <p><input type="checkbox"> Am I making this trade free of FOMO, anchoring to past peaks, or recovery impatience?</p>
    <div class="signature-line">
      <span>Investor Signature: ___________________________</span>
      <span>Execution Date: __________________</span>
    </div>
  </div>

  <div class="footer">
    <strong>SEBI Educational Disclaimer:</strong> FAIDA is an educational research and pre-mortem risk-awareness tool powered by public Indian market data. It does not provide buy/sell advice or SEBI-registered financial advisory services.
  </div>
</body>
</html>"""
    return HTMLResponse(content=html_content)

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
