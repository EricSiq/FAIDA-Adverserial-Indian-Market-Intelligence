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


def test_export_endpoint_not_found():
    resp = client.get("/api/export/non_existent_session_id")
    assert resp.status_code == 404

