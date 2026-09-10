import pytest
from backend.lkb.models import LKBFact, LKBFactCategory, LKBPacket, AssetClass

def test_lkb_fact_validation():
    fact = LKBFact(
        id="LKB-01",
        category=LKBFactCategory.TECHNICAL,
        source="NSE_LIVE",
        metric="Current Market Price",
        value=2985.40,
        unit="INR",
        context="Intraday quote"
    )
    assert fact.id == "LKB-01"
    assert fact.category == LKBFactCategory.TECHNICAL
    assert fact.value == 2985.40

def test_lkb_packet_structure():
    packet = LKBPacket(
        session_id="faida-test-1234",
        symbol="RELIANCE",
        exchange="NSE",
        asset_class=AssetClass.EQUITY,
        facts=[
            LKBFact(
                id="LKB-01",
                category=LKBFactCategory.VALUATION,
                source="SCREENER",
                metric="Stock P/E",
                value=28.4,
                unit="x"
            )
        ]
    )
    assert packet.symbol == "RELIANCE"
    assert len(packet.facts) == 1
    assert packet.facts[0].id == "LKB-01"
