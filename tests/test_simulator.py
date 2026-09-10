import pytest
from backend.agents.simulator_agent import SimulatorAgent

def test_crude_surge_simulation():
    res = SimulatorAgent.simulate("ASIANPAINT", "CRUDE_SURGE")
    assert res.symbol == "ASIANPAINT"
    assert "NEGATIVE" in res.estimated_impact
    assert "raw material" in res.mechanism.lower()

def test_rbi_rate_hike_simulation():
    res = SimulatorAgent.simulate("HDFCBANK", "RBI_RATE_HIKE")
    assert res.symbol == "HDFCBANK"
    assert "NIM" in res.estimated_impact or "Margin" in res.estimated_impact

def test_inr_depreciation_simulation():
    res = SimulatorAgent.simulate("INFY", "INR_DEPRECIATION")
    assert res.symbol == "INFY"
    assert "TAILWIND" in res.estimated_impact or "FAVORABLE" in res.estimated_impact

def test_margin_compression_simulation():
    res = SimulatorAgent.simulate("RELIANCE", "MARGIN_COMPRESSION")
    assert res.symbol == "RELIANCE"
    assert "NEGATIVE" in res.estimated_impact

def test_simulator_symbol_cleaning_and_fallbacks():
    res_ns = SimulatorAgent.simulate("TCS.NS", "INR_DEPRECIATION")
    assert res_ns.symbol == "TCS"

    res_none = SimulatorAgent.simulate(None, "CRUDE_SURGE")
    assert res_none.symbol == "BENCHMARK"

