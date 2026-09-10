import pytest
from backend.scrapers.nse_client import NSEClient
from backend.scrapers.screener_client import ScreenerClient
from backend.scrapers.yfinance_client import YFinanceClient

def test_nse_symbol_sanitization():
    # Valid symbols
    assert NSEClient._sanitize_symbol("RELIANCE") == "RELIANCE"
    assert NSEClient._sanitize_symbol("tcs.ns") == "TCS"
    assert NSEClient._sanitize_symbol("M&M") == "M&M"
    
    # Dangerous/invalid symbols must be rejected (return None)
    assert NSEClient._sanitize_symbol("../../../etc/passwd") is None
    assert NSEClient._sanitize_symbol("DROP TABLE;--") is None
    assert NSEClient._sanitize_symbol("") is None

def test_screener_symbol_sanitization():
    assert ScreenerClient._sanitize_symbol("INFY") == "INFY"
    assert ScreenerClient._sanitize_symbol("RELIANCE.BO") == "RELIANCE"
    assert ScreenerClient._sanitize_symbol("<script>alert(1)</script>") is None

def test_yfinance_ticker_formatting():
    assert YFinanceClient._format_ticker("RELIANCE", "NSE") == "RELIANCE.NS"
    assert YFinanceClient._format_ticker("TCS", "BSE") == "TCS.BO"
    assert YFinanceClient._format_ticker("INFY.NS", "NSE") == "INFY.NS"
