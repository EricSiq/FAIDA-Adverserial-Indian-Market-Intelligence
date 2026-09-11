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

def test_lkb_builder_generation():
    from backend.lkb.builder import LKBBuilder
    builder = LKBBuilder()
    packet = builder.build_equity_packet("TCS", "NSE")
    assert packet.symbol == "TCS"
    assert len(packet.facts) >= 4
    
    metrics = [f.metric for f in packet.facts]
    assert any("India VIX" in m for m in metrics)
    assert any("G-Sec Yield" in m for m in metrics)

def test_lkb_builder_query_targeted_context():
    from backend.lkb.builder import LKBBuilder
    builder = LKBBuilder()
    packet = builder.build_equity_packet("RELIANCE", "NSE", user_query="Selling because crude prices are volatile")
    metrics = [f.metric for f in packet.facts]
    assert any("Brent Crude" in m for m in metrics)
    assert packet.metadata.get("query_context_applied") is True


