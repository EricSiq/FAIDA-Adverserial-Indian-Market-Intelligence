import pytest
from backend.export.pdf_generator import PreMortemPDFGenerator

def test_generate_pdf_basic():
    record = {
        "symbol": "TCS",
        "exchange": "NSE",
        "action": "BUY",
        "target_price": 4200.0,
        "current_price": 3950.0,
        "friction_score": 68,
        "id": "pdf-test-session-01",
        "created_at": "2026-09-10T20:00:00",
        "pre_mortem": {
            "headline_verdict": "MODERATE FRICTION: Premium Multiple vs Historical Average",
            "detected_biases": [
                {
                    "bias_name": "Anchoring Bias",
                    "severity": "HIGH",
                    "psychological_trap": "Anchored to past 52-week peak.",
                    "reframing_advice": "Check trailing multiple vs peer group."
                }
            ],
            "invalidation_levels": {
                "invalidation_price": 3800.0,
                "take_profit_target": 4350.0
            }
        },
        "lkb_packet": {
            "facts": [
                {"id": "LKB-01", "category": "MOMENTUM", "metric": "200 EMA", "value": "3910.0", "unit": "INR", "source": "NSE Bhavcopy"},
                {"id": "LKB-02", "category": "VALUATION", "metric": "P/E Ratio", "value": "29.8", "unit": "x", "source": "Screener.in"}
            ]
        }
    }

    pdf_bytes = PreMortemPDFGenerator.generate(record)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")

def test_generate_pdf_empty_packet_and_biases():
    record = {
        "symbol": "INFY",
        "exchange": "NSE",
        "action": "SELL",
        "current_price": 1850.0,
        "friction_score": 30,
        "id": "pdf-test-empty-02"
    }

    pdf_bytes = PreMortemPDFGenerator.generate(record)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")
