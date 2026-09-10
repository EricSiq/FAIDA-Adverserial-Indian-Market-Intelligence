import pytest
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_get_config_endpoint():
    resp = client.get("/api/config")
    assert resp.status_code == 200
    data = resp.json()
    assert "active_provider" in data
    assert "default_local_model" in data
    # Security check: ensure GROQ_API_KEY is not leaked
    assert "GROQ_API_KEY" not in str(data)

def test_update_config_endpoint():
    resp = client.post("/api/config", json={
        "active_provider": "ollama",
        "default_local_model": "gemma4:e4b"
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_get_history_endpoint():
    resp = client.get("/api/history")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_analyze_validation_empty_query():
    resp = client.post("/api/analyze", json={"query": " ", "tone_level": 3})
    assert resp.status_code == 422 or resp.status_code == 400

def test_analyze_validation_invalid_tone():
    resp = client.post("/api/analyze", json={"query": "Buying Reliance at 2900", "tone_level": 99})
    assert resp.status_code == 422

def test_macro_vix_endpoint():
    resp = client.get("/api/macro/vix")
    assert resp.status_code == 200
    data = resp.json()
    assert "vix_value" in data
    assert "regime" in data
    assert "regime_label" in data
    assert "description" in data
    assert data["regime"] in [
        "LOW_VOLATILITY",
        "NORMAL",
        "ELEVATED",
        "EXTREME_PANIC"
    ]

def test_simulate_endpoint():
    resp = client.post("/api/simulate", json={
        "symbol": "ASIANPAINT",
        "scenario_type": "CRUDE_SURGE"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["symbol"] == "ASIANPAINT"
    assert data["scenario_id"] == "CRUDE_SURGE"
    assert "estimated_impact" in data
    assert "mechanism" in data
    assert "red_team_warning" in data

def test_simulate_endpoint_invalid_scenario():
    resp = client.post("/api/simulate", json={
        "symbol": "ASIANPAINT",
        "scenario_type": "INVALID_SCENARIO"
    })
    assert resp.status_code == 422

def test_simulate_endpoint_invalid_symbol_regex():
    resp = client.post("/api/simulate", json={
        "symbol": "ASIAN; DROP TABLE",
        "scenario_type": "CRUDE_SURGE"
    })
    assert resp.status_code == 422

def test_export_endpoint_not_found():
    resp = client.get("/api/export/non_existent_session_id")
    assert resp.status_code == 404

def test_export_endpoint_invalid_session_format():
    resp = client.get("/api/export/bad;id<script>")
    assert resp.status_code == 400

def test_export_endpoint_success_and_escaping():
    from backend.app import journal

    journal.save_decision(
        session_id="test-session-xss-clean",
        symbol="<script>alert(1)</script>",
        exchange="NSE",
        action="BUY",
        target_price=500.0,
        current_price=480.0,
        friction_score=75,
        tone_level=3,
        headline_verdict="Alert <img src=x onerror=alert(2)>",
        pre_mortem_dict={
            "headline_verdict": "Alert <img src=x onerror=alert(2)>",
            "friction_score": 75,
            "bearish_risks": [{"risk_title": "Risk 1", "severity": "HIGH", "metric_cited": "PE", "argument": "Overvalued"}],
            "educational_takeaways": ["Be disciplined"],
            "invalidation_levels": {"invalidation_price": 450.0, "take_profit_target": 550.0}
        },
        lkb_packet_dict={
            "symbol": "TEST",
            "exchange": "NSE",
            "current_price": 480.0,
            "facts": [
                {"id": "LKB-01", "category": "VALUATION", "metric": "<b onmouseover=alert(3)>P/E</b>", "value": "35.4", "unit": "x", "source": "Screener"}
            ]
        }
    )

    # 1. Test Default Native PDF Export
    resp_pdf = client.get("/api/export/test-session-xss-clean")
    assert resp_pdf.status_code == 200
    assert "application/pdf" in resp_pdf.headers["content-type"]
    assert resp_pdf.content.startswith(b"%PDF")

    # 2. Test Direct /pdf Route
    resp_pdf_direct = client.get("/api/export/test-session-xss-clean/pdf")
    assert resp_pdf_direct.status_code == 200
    assert "application/pdf" in resp_pdf_direct.headers["content-type"]
    assert resp_pdf_direct.content.startswith(b"%PDF")

    # 3. Test HTML View & Security Escaping
    resp_html = client.get("/api/export/test-session-xss-clean?format=html")
    assert resp_html.status_code == 200
    assert "text/html" in resp_html.headers["content-type"]
    html_text = resp_html.text

    # Security check: ensure script tags and event handlers are properly escaped as HTML entities
    assert "<script>alert(1)</script>" not in html_text
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html_text.lower()
    assert "<img src=x onerror=alert(2)>" not in html_text
    assert "&lt;img src=x onerror=alert(2)&gt;" in html_text
    assert "<b onmouseover=alert(3)>" not in html_text
    assert "&lt;b onmouseover=alert(3)&gt;P/E&lt;/b&gt;" in html_text
    # Explainability check: ensure references table exists
    assert "Grounded Evidence Sources &amp; Scraped Verification Links" in html_text or "Grounded Evidence Sources" in html_text




