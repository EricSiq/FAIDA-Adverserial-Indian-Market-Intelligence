import pytest
from backend.scrapers.fred_client import FREDClient
from backend.scrapers.broker_client import BrokerClient

def test_fred_client_fallback_without_key():
    obs = FREDClient.get_series_observation("BRENT_CRUDE", api_key="")
    assert obs["series"] == "BRENT_CRUDE"
    assert obs["source"] == "FRED_BASELINE"
    assert isinstance(obs["value"], float)
    assert obs["value"] > 0

def test_fred_global_macro_snapshot():
    snap = FREDClient.get_global_macro_snapshot(api_key="")
    assert "brent_crude_usd" in snap
    assert "us_10y_yield_pct" in snap
    assert "us_dollar_index" in snap
    assert snap["is_live_api"] is False

def test_broker_client_unconfigured():
    assert BrokerClient.get_quote("RELIANCE") is None
    assert BrokerClient.get_broker_name() in ["upstox", "generic"]
