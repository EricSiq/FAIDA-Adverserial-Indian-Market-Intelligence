"""
FAIDA: Financial Adversarial Indian Data Agents
Module: backend.app
Description:
    FastAPI Application Server providing REST endpoints for the FAIDA desktop application.
    
    API Surface:
        - POST /api/analyze: Runs the full 5-stage adversarial intelligence pipeline.
        - GET  /api/macro/vix: Real-time India VIX index and market regime indicators.
        - GET  /api/macro/global: Global macro snapshot (Brent crude, US 10Y yield, US Dollar Index).
        - POST /api/simulate: Deterministic macroeconomic and sectoral stress-testing.
        - GET  /api/history: List past audit decisions from DuckDB journal.
        - GET  /api/history/{session_id}: Retrieve full audit record details.
        - GET  /api/export/{session_id}: Institutional-grade PDF and HTML one-pager export.
        - POST /api/cache/clear-expired: Maintenance endpoint to purge stale feature store records.
        - GET/POST /api/config: Live configuration of model providers and API keys.
"""

import os
import re
import html
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.config import settings
from backend.agents.orchestrator import SwarmOrchestrator
from backend.agents.simulator_agent import SimulatorAgent
from backend.scrapers.macro_client import MacroClient
from backend.db.journal import DecisionJournal
from backend.export.pdf_generator import PreMortemPDFGenerator

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
    symbol: str = Field(..., min_length=1, max_length=20, pattern=r"^[A-Za-z0-9&._-]+$")
    scenario_type: str = Field(..., pattern=r"^(CRUDE_SURGE|RBI_RATE_HIKE|INR_DEPRECIATION|MARGIN_COMPRESSION)$")

from backend.scrapers.fred_client import FREDClient

@app.get("/api/macro/vix")
def get_vix_gauge():
    """Returns India VIX macro weather regime."""
    return MacroClient.get_vix_status()

@app.get("/api/macro/global")
def get_global_macro():
    """Returns global macro snapshot: Brent Crude, US 10Y Yield, and DXY."""
    return FREDClient.get_global_macro_snapshot()

@app.post("/api/cache/clear-expired")
def clear_expired_cache():
    """Cleans up stale entries from the DuckDB feature store."""
    from backend.db.feature_store import FeatureStore
    store = FeatureStore()
    purged = store.clear_expired()
    store.close()
    return {"status": "ok", "purged_count": purged}

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
    if not re.match(r"^[a-zA-Z0-9_\-]+$", session_id):
        raise HTTPException(status_code=400, detail="Invalid session_id format")
    res = journal.get_decision_by_id(session_id)
    if not res:
        raise HTTPException(status_code=404, detail="Decision record not found")
    return res

@app.get("/api/export/{session_id}")
def export_pre_mortem_one_pager(session_id: str, format: str = "pdf"):
    """Generates an institutional-grade Pre-Mortem One-Pager as native PDF or clean HTML."""
    if not re.match(r"^[a-zA-Z0-9_\-]+$", session_id):
        raise HTTPException(status_code=400, detail="Invalid session_id format")

    record = journal.get_decision_by_id(session_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    symbol_clean = str(record.get('symbol', 'EQUITY')).upper().replace(".NS", "")

    # Native PDF Generation
    if format.lower() == "pdf":
        try:
            pdf_bytes = PreMortemPDFGenerator.generate(record)
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={"Content-Disposition": f'attachment; filename="FAIDA_PreMortem_{symbol_clean}.pdf"'}
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")

    # Clean Professional HTML View
    pm = record.get("pre_mortem") or {}
    lkb = record.get("lkb_packet") or {}
    facts = lkb.get("facts", [])
    biases = pm.get("detected_biases", [])

    facts_rows = "".join([
        f"<tr><td><code>{html.escape(str(f.get('id', '')))}</code></td><td>{html.escape(str(f.get('category', '')))}</td><td><strong>{html.escape(str(f.get('metric', '')))}</strong></td><td>{html.escape(str(f.get('value', '')))} {html.escape(str(f.get('unit', '')))}</td><td>{html.escape(str(f.get('source', '')))}</td></tr>"
        for f in facts
    ])

    biases_html = "".join([
        f"<div class='bias-box'><strong>[ALERT: {html.escape(str(b.get('bias_name', ''))).upper()}] ({html.escape(str(b.get('severity', '')))} Severity)</strong><p><em>Trap:</em> {html.escape(str(b.get('psychological_trap', '')))}</p><p><em>Reframing Check:</em> {html.escape(str(b.get('reframing_advice', '')))}</p></div>"
        for b in biases
    ]) if biases else "<p>No prominent cognitive biases detected in user rationale.</p>"

    esc_symbol = html.escape(str(record.get('symbol', 'UNKNOWN')))
    esc_exchange = html.escape(str(record.get('exchange', 'NSE')))
    esc_action = html.escape(str(record.get('action', 'BUY')))
    esc_target = html.escape(str(record.get('target_price') or 'Market'))
    esc_cmp = html.escape(str(record.get('current_price') or 'N/A'))
    esc_verdict = html.escape(str(pm.get('headline_verdict', 'Pre-Mortem Invalidation Report')))
    esc_date = html.escape(str(record.get('created_at', '')))
    esc_friction = html.escape(str(record.get('friction_score', '50')))
    esc_session = html.escape(str(session_id))
    esc_invalidation = html.escape(str(pm.get('invalidation_levels', {}).get('invalidation_price', 'N/A')))
    esc_take_profit = html.escape(str(pm.get('invalidation_levels', {}).get('take_profit_target', 'N/A')))

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>FAIDA Pre-Mortem Audit - {esc_symbol}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.45; color: #0f172a; max-width: 850px; margin: 30px auto; padding: 20px; }}
  .header {{ display: flex; justify-content: space-between; border-bottom: 2px solid #0f172a; padding-bottom: 12px; margin-bottom: 18px; }}
  .title h1 {{ margin: 0; font-size: 22px; color: #0f172a; font-weight: 700; }}
  .meta {{ font-size: 12px; color: #64748b; }}
  .verdict-box {{ background: #f8fafc; border: 1px solid #cbd5e1; border-left: 4px solid #dc2626; padding: 12px 16px; margin: 16px 0; }}
  .score {{ font-size: 24px; font-weight: 800; color: #dc2626; }}
  table {{ width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 11.5px; }}
  th, td {{ border: 1px solid #cbd5e1; padding: 6px 10px; text-align: left; }}
  th {{ background: #f1f5f9; color: #1e293b; font-weight: 600; }}
  a {{ color: #0284c7; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .bias-box {{ background: #fffbeb; border: 1px solid #fde68a; border-left: 3.5px solid #d97706; padding: 8px 12px; margin: 8px 0; font-size: 12px; }}
  .invalidation-box {{ background: #f8fafc; border: 1px solid #cbd5e1; padding: 10px 14px; margin: 12px 0; font-size: 12px; }}
  .footer {{ margin-top: 30px; font-size: 10px; color: #64748b; border-top: 1px solid #e2e8f0; padding-top: 8px; }}
  @media print {{ body {{ margin: 10px; padding: 0; }} .no-print {{ display: none; }} }}
</style>
</head>
<body>
  <div class="no-print" style="margin-bottom: 18px; display: flex; justify-content: space-between; align-items: center; background: #0f172a; color: #fff; padding: 10px 16px; border-radius: 4px;">
    <span style="font-size: 12.5px; font-weight: 500;">FAIDA Institutional Pre-Mortem One-Pager</span>
    <div style="display: flex; gap: 8px;">
      <a href="/api/export/{esc_session}?format=pdf" style="background: #2563eb; color: #fff; text-decoration: none; padding: 5px 12px; font-size: 12px; font-weight: 600; border-radius: 3px;">Download Native PDF</a>
      <button onclick="window.print()" style="background: #334155; color: #fff; border: none; padding: 5px 12px; font-size: 12px; font-weight: 600; border-radius: 3px; cursor: pointer;">Print View</button>
    </div>
  </div>

  <div class="header">
    <div class="title">
      <h1>FAIDA Institutional Pre-Mortem Audit</h1>
      <div class="meta">Red-Team Invalidation Report | Indian Capital Markets | Date: {esc_date}</div>
    </div>
    <div style="text-align: right; font-size: 12px;">
      <strong>{esc_symbol} ({esc_exchange})</strong><br>
      <span>Action: <strong>{esc_action}</strong></span><br>
      <span>Target: INR {esc_target} | CMP: INR {esc_cmp}</span>
    </div>
  </div>

  <div class="verdict-box">
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h3 style="margin: 0 0 4px 0; color: #991b1b; font-size: 14px;">{esc_verdict}</h3>
        <p style="margin: 0; font-size: 11.5px; color: #475569;">Session: <code>{esc_session}</code> | Adversarial Stance: Level 4</p>
      </div>
      <div class="score">{esc_friction}/100</div>
    </div>
  </div>

  <h4 style="margin: 16px 0 6px 0; text-transform: uppercase; font-size: 12px; letter-spacing: 0.5px;">1. Grounded Local Knowledge Base (Evidence Snapshot)</h4>
  <table>
    <thead><tr><th>Fact ID</th><th>Category</th><th>Metric</th><th>Ground Value</th><th>Source</th></tr></thead>
    <tbody>{facts_rows}</tbody>
  </table>

  <h4 style="margin: 16px 0 6px 0; text-transform: uppercase; font-size: 12px; letter-spacing: 0.5px;">2. Cognitive Biases & Behavioral Traps Detected</h4>
  {biases_html}

  <h4 style="margin: 16px 0 6px 0; text-transform: uppercase; font-size: 12px; letter-spacing: 0.5px;">3. Invalidation & Stop-Loss Rules</h4>
  <div class="invalidation-box">
    <ul style="margin: 4px 0 0 16px; padding: 0;">
      <li><strong>Stop-Loss Invalidation Level:</strong> INR {esc_invalidation} (Exit discipline to avoid asymmetric drawdown).</li>
      <li><strong>Target Invalidation Resistance:</strong> INR {esc_take_profit}</li>
    </ul>
  </div>

  <h4 style="margin: 16px 0 6px 0; text-transform: uppercase; font-size: 12px; letter-spacing: 0.5px;">4. Grounded Evidence Sources & Scraped Verification Links</h4>
  <table>
    <thead><tr><th>Source Entity</th><th>Scraped Portal / Verification URL</th><th>Extracted Metrics</th><th>Data Cadence</th></tr></thead>
    <tbody>
      <tr>
        <td><strong>National Stock Exchange (NSE)</strong></td>
        <td><a href="https://www.nseindia.com/get-quotes/equity?symbol={esc_symbol}" target="_blank">nseindia.com/get-quotes/equity?symbol={esc_symbol}</a></td>
        <td>Security Deliverables (Delivery %), Turnover, Real-time Quote</td>
        <td>Live Tick / T+0 Close</td>
      </tr>
      <tr>
        <td><strong>Screener.in Financials</strong></td>
        <td><a href="https://www.screener.in/company/{esc_symbol}/consolidated/" target="_blank">screener.in/company/{esc_symbol}/consolidated/</a></td>
        <td>10Y Median P/E, Operating Profit Margin (OPM), Promoter Pledge %</td>
        <td>Quarterly Filings</td>
      </tr>
      <tr>
        <td><strong>Clearing Corporation of India (CCIL)</strong></td>
        <td><a href="https://www.ccilindia.com/" target="_blank">ccilindia.com (Sovereign G-Sec Market)</a></td>
        <td>10-Year Benchmark Sovereign Yield (7.08%)</td>
        <td>Daily Yield Curve</td>
      </tr>
      <tr>
        <td><strong>NSE Indices (India VIX)</strong></td>
        <td><a href="https://www.nseindia.com/market-data/live-equity-market" target="_blank">nseindia.com/market-data/live-equity-market (^INDIAVIX)</a></td>
        <td>Implied Volatility Index (13.8 - Normal Volatility Regime)</td>
        <td>Real-time Options</td>
      </tr>
      <tr>
        <td><strong>Reserve Bank of India (RBI)</strong></td>
        <td><a href="https://www.rbi.org.in/" target="_blank">rbi.org.in (Monetary Policy Committee)</a></td>
        <td>Policy Repo Rate (6.50%), Inflation Projections</td>
        <td>Bi-monthly MPC</td>
      </tr>
    </tbody>
  </table>

  <div class="footer">
    <strong>Regulatory Notice (SEBI Compliance):</strong> FAIDA is strictly an adversarial red-teaming and educational research tool powered by public Indian market data. It does not provide buy/sell recommendations or SEBI-registered financial advisory services.
  </div>
</body>
</html>"""
    return HTMLResponse(content=html_content)

@app.get("/api/export/{session_id}/pdf")
def export_pre_mortem_pdf_direct(session_id: str):
    """Direct alias for downloading the Pre-Mortem PDF."""
    return export_pre_mortem_one_pager(session_id, format="pdf")



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
