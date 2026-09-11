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

def test_screener_cfo_pat_accrual_parsing():
    mock_html = """
    <html>
      <h1>ABC Ltd</h1>
      <ul id="top-ratios">
        <li><span class="name">Stock P/E</span><span class="number">24.5</span></li>
      </ul>
      <section id="cash-flow">
        <table>
          <tr>
            <td>Cash from Operating Activity</td>
            <td>100</td><td>120</td><td>110</td>
          </tr>
        </table>
      </section>
      <section id="profit-loss">
        <table>
          <tr>
            <td>Net Profit</td>
            <td>200</td><td>250</td><td>300</td>
          </tr>
        </table>
      </section>
    </html>
    """
    res = ScreenerClient._parse_html(mock_html, "ABC")
    assert res["symbol"] == "ABC"
    assert "forensics" in res
    assert res["forensics"]["cumulative_3y_cfo"] == 330.0
    assert res["forensics"]["cumulative_3y_pat"] == 750.0
    assert res["forensics"]["cfo_to_pat_ratio"] == 0.44
    assert any("Forensic Accrual Risk" in rf for rf in res["red_flags"])

def test_bse_announcements_parsing():
    from backend.scrapers.bse_client import BSEClient
    sample_table = [
        {
            "NEWSSUB": "Resignation of Statutory Auditor",
            "HEADLINE": "M/s XYZ resigned due to preoccupation",
            "NEWS_DT": "2026-09-10",
            "CATEGORYNAME": "Company Update"
        },
        {
            "NEWSSUB": "Press Release on Q2 Business Highlights",
            "HEADLINE": "Revenue grew by 12% YoY",
            "NEWS_DT": "2026-09-09",
            "CATEGORYNAME": "General"
        }
    ]
    parsed = BSEClient._parse_announcements(sample_table)
    assert len(parsed) == 2
    assert parsed[0]["is_risk_flag"] is True
    assert parsed[1]["is_risk_flag"] is False

