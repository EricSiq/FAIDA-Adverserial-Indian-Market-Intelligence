import pytest
import tempfile
import os
import time
from unittest.mock import patch

from backend.db.feature_store import FeatureStore
from backend.lkb.builder import LKBBuilder
from backend.lkb.models import LKBPacket, AssetClass

@pytest.fixture
def temp_feature_store():
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_features.duckdb")
    store = FeatureStore(db_path=db_path)
    yield store
    store.close()

def test_feature_store_set_and_get(temp_feature_store):
    store = temp_feature_store
    data = {"last_price": 2500.50, "rsi_14": 42.1}
    success = store.set("RELIANCE", "TECHNICAL", data, ttl_seconds=60)
    assert success is True

    cached = store.get("RELIANCE", "TECHNICAL")
    assert cached is not None
    assert cached["last_price"] == 2500.50
    assert cached["rsi_14"] == 42.1

    # Non-existent symbol returns None
    assert store.get("INFY", "TECHNICAL") is None

def test_feature_store_ttl_expiration(temp_feature_store):
    store = temp_feature_store
    data = {"company_name": "Tata Motors Ltd"}
    store.set("TATAMOTORS", "FUNDAMENTALS", data, ttl_seconds=1)

    # Immediately available
    assert store.get("TATAMOTORS", "FUNDAMENTALS") is not None

    # Wait for TTL to expire
    time.sleep(1.1)
    assert store.get("TATAMOTORS", "FUNDAMENTALS") is None

def test_feature_store_clear_expired_and_clear_all(temp_feature_store):
    store = temp_feature_store
    store.set("HDFCBANK", "QUOTE", {"price": 1600.0}, ttl_seconds=1)
    store.set("ICICIBANK", "QUOTE", {"price": 1050.0}, ttl_seconds=300)

    time.sleep(1.1)
    purged = store.clear_expired()
    assert purged >= 1

    assert store.get("HDFCBANK", "QUOTE") is None
    assert store.get("ICICIBANK", "QUOTE") is not None

    store.clear_all()
    assert store.get("ICICIBANK", "QUOTE") is None

def test_lkb_builder_uses_feature_store_cache():
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_builder_cache.duckdb")
    store = FeatureStore(db_path=db_path)

    builder = LKBBuilder(use_cache=True, feature_store=store)

    dummy_yf = {
        "symbol": "TCS",
        "current_price": 3800.0,
        "fifty_two_week_high": 4200.0,
        "fifty_two_week_low": 3200.0,
        "rsi_14": 55.0,
        "pe_ratio": 28.5
    }

    with patch("backend.scrapers.yfinance_client.YFinanceClient.get_market_summary", return_value=dummy_yf) as mock_yf, \
         patch("backend.scrapers.screener_client.ScreenerClient.get_fundamentals", return_value={}) as mock_scr, \
         patch.object(builder.nse_client, "get_quote", return_value=None) as mock_nse, \
         patch("backend.scrapers.macro_client.MacroClient.get_vix_status", return_value={"vix_value": 14.0, "regime_label": "Normal", "benchmark_10y_yield": 7.05}):

        # First build: misses cache, executes scrapers, saves to cache
        packet1 = builder.build_equity_packet("TCS")
        assert packet1.symbol == "TCS"
        assert mock_yf.call_count == 1

        # Second build: hits cache directly, scraper call count should NOT increase
        packet2 = builder.build_equity_packet("TCS")
        assert packet2.symbol == "TCS"
        assert mock_yf.call_count == 1

        # Third build with force_refresh: should bypass cache and call scrapers again
        packet3 = builder.build_equity_packet("TCS", force_refresh=True)
        assert packet3.symbol == "TCS"
        assert mock_yf.call_count == 2

    store.close()
