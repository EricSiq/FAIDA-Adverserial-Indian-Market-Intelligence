# 02. Data Sources & Scraping Matrix: FAIDA Grounding Engine

## 1. Overview & Free-Access Principles

**FAIDA** (*Financial Adversarial Indian Data Agents*) enforces a strict rule: **No LLM claim without deterministic grounding.** To achieve this without paid enterprise subscriptions (Bloomberg, Refinitiv, or paid broker APIs), FAIDA aggregates data from 100% free, publicly available Indian market endpoints.

Every scraped data point is converted into a normalized entry in the session's **Local Knowledge Base (LKB)**.

---

## 2. Asset Class Data Matrix & LKB Mapping

### A. Indian Equities (NSE & BSE)

| Source Name | Raw Endpoint / Protocol | Data Extracted | LKB Tag Format |
| :--- | :--- | :--- | :--- |
| **NSE India Public API** | `https://www.nseindia.com/api/quote-equity?symbol={SYMBOL}` | LTP, 52W High/Low, Day Range, Delivery Volume %, Total Traded Value | `[NSE: LTP ₹{price}, Delivery {del}%]` |
| **Yahoo Finance** | `yfinance` (`{SYMBOL}.NS` / `{SYMBOL}.BO`) | 1Y OHLCV series, 20/50/200 EMA, RSI(14), Beta, Market Capitalization | `[YF: 200-EMA ₹{val}, RSI {val}]` |
| **Screener.in** | `https://www.screener.in/company/{SYMBOL}/` (HTML Tables) | P/E, PEG, Price-to-Book, ROCE, ROE, Promoter Pledging %, Debt-to-Equity, FCF | `[Screener: P/E {val}, ROCE {val}%]` |
| **BSE India Announcements** | `https://api.bseindia.com/BseWebAPI/api/AnnSubCategoryGetData/...` | Board meetings, Auditor resignations, Credit rating changes, Q-o-Q results | `[BSE: {event_type} on {date}]` |
| **Trendlyne (Public Summary)** | Public valuation summary pages | Institutional holding trends (FII / DII net changes in latest quarter) | `[Trendlyne: FII {change}%]` |

---

### B. Fixed Income & Government Securities (G-Secs, T-Bills, Bonds & SGBs)

| Source Name | Raw Endpoint / Protocol | Data Extracted | LKB Tag Format |
| :--- | :--- | :--- | :--- |
| **CCIL India (Clearing Corp of India)** | `https://www.ccilindia.com/` public yield curve tables | 91-Day T-Bill yield, 5-Year G-Sec yield, 10-Year Benchmark G-Sec yield | `[CCIL: 10Y Yield {yield}%]` |
| **RBI DBIE / Retail Direct** | RBI Data Warehouse public bulletins | Repo rate (current & stance), Sovereign Gold Bond (SGB) issue vs secondary prices | `[RBI: Repo Rate {rate}%]` |
| **NSE Debt Segment** | Daily Debt Market Snapshot | Listed PSU Bonds, Corporate NCD yield spreads over benchmark G-Sec | `[NSE-Debt: Spread {bps} bps]` |
| **FBIL (Financial Benchmarks India)** | Daily published benchmark rates | MIBOR overnight rates and term reference rates | `[FBIL: MIBOR {rate}%]` |

---

### C. Commodities & Currencies (MCX & Forex)

| Source Name | Raw Endpoint / Protocol | Data Extracted | LKB Tag Format |
| :--- | :--- | :--- | :--- |
| **MCX India** | `https://www.mcxindia.com/market-data/` | Gold (10g), Silver (1kg), Crude Oil (bbl), Natural Gas futures prices & daily % change | `[MCX: Crude ₹{price}/bbl ({chg}%)]` |
| **RBI Reference Rate** | RBI Daily FX Bulletin | USD/INR, EUR/INR, GBP/INR spot reference rates | `[RBI-FX: USD/INR ₹{rate}]` |

---

### D. News, Governance & Regulatory Red Flags

| Source Name | Raw Endpoint / Protocol | Data Extracted | LKB Tag Format |
| :--- | :--- | :--- | :--- |
| **Moneycontrol & LiveMint RSS** | `moneycontrol.com/rss/MCtopnews.xml`, LiveMint RSS | Corporate news, sector trends, analyst target downgrades | `[News: "{headline}"]` |
| **SEBI Orders & Press Releases** | `sebi.gov.in` public notifications RSS | Debarment orders, insider trading penalties, forensic audit notices | `[SEBI: Order Ref {ref_id}]` |

---

### E. Global Macro & News Catalyst APIs (FRED & Finnhub)

| Source Name | Raw Endpoint / Protocol | Data Extracted | LKB Tag Format |
| :--- | :--- | :--- | :--- |
| **Federal Reserve Economic Data (FRED)** | `api.stlouisfed.org/fred/series/observations` | Brent Crude (`DCOILBRENTEU`), US 10Y Yield (`DGS10`), Broad US Dollar Index (`DTWEXBGS`) | `[FRED: Brent ${price}, US 10Y {yield}%]` |
| **Finnhub Financial API** | `finnhub.io/api/v1/company-news` & `/news` | Real-time ADR news (INFY, HDB, IBN, WIT, TTM) & global macro catalysts | `[FINNHUB_{SOURCE}: "{headline}"]` |


---

## 3. Local Knowledge Base (LKB) JSON Schema

Before any prompt is sent to the LLM, the FAIDA data ingestion hub aggregates all scraped metrics into a clean, normalized JSON table. This document represents the **ground-truth universe** for that session.

```json
{
  "session_id": "faida-2026-09-10-rel-01",
  "symbol": "RELIANCE",
  "exchange": "NSE",
  "asset_class": "EQUITY",
  "timestamp": "2026-09-10T14:00:00+05:30",
  "facts": [
    {
      "id": "LKB-01",
      "category": "TECHNICAL",
      "source": "NSE_LIVE",
      "metric": "Current Market Price",
      "value": 2985.40,
      "unit": "INR",
      "context": "Day High: 3010.00, Day Low: 2972.10, Change: -0.45%"
    },
    {
      "id": "LKB-02",
      "category": "LIQUIDITY",
      "source": "NSE_BHAVCOPY",
      "metric": "Delivery Percentage",
      "value": 24.2,
      "unit": "%",
      "context": "30-Day Average Delivery: 41.5% (Indicates low institutional conviction)"
    },
    {
      "id": "LKB-03",
      "category": "VALUATION",
      "source": "SCREENER",
      "metric": "Trailing P/E",
      "value": 28.4,
      "unit": "x",
      "context": "5-Year Median P/E: 24.1x (Trading at 17.8% premium to historical median)"
    },
    {
      "id": "LKB-04",
      "category": "GOVERNANCE",
      "source": "SCREENER",
      "metric": "Promoter Pledging",
      "value": 0.0,
      "unit": "%",
      "context": "Total Promoter Holding: 50.3%, 0% pledged"
    },
    {
      "id": "LKB-05",
      "category": "MACRO",
      "source": "CCIL_INDIA",
      "metric": "10-Year Benchmark G-Sec Yield",
      "value": 7.09,
      "unit": "%",
      "context": "Risk-Free Rate baseline for Indian equities"
    },
    {
      "id": "LKB-06",
      "category": "COMMODITY",
      "source": "MCX_INDIA",
      "metric": "Brent/MCX Crude Oil",
      "value": 6420.0,
      "unit": "INR/bbl",
      "context": "Up 2.8% today (pressures gross refining margins for downstream petrochemicals)"
    }
  ]
}
```

---

## 4. The Resilient Scraping Engine: Code Pattern

### Multi-Tier Ingestion Adapter with Automatic Cookie Handshake

```python
import httpx
from typing import Dict, Any, Optional

class FAIDADataHub:
    """Consolidated Ingestion Adapter for Indian Market Public Endpoints."""
    
    NSE_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "*/*",
        "Referer": "https://www.nseindia.com/",
    }
    
    def __init__(self, cache_db_path: str = "faida_cache.duckdb"):
        self.session = httpx.Client(headers=self.NSE_HEADERS, timeout=12.0, follow_redirects=True)
        self.cache_path = cache_db_path
        self._init_nse_cookie()

    def _init_nse_cookie(self):
        """Perform initial handshake to acquire valid session cookies from NSE."""
        try:
            self.session.get("https://www.nseindia.com")
        except Exception as err:
            print(f"[FAIDA-WARN] NSE cookie init failed, fallback ready: {err}")

    def fetch_equity_grounding_packet(self, symbol: str) -> Dict[str, Any]:
        """Fetch quotes, fundamentals, and build the grounded LKB packet."""
        lkb_facts = []
        
        # 1. Real-time quote & Delivery
        quote_data = self._fetch_nse_quote(symbol)
        if quote_data:
            lkb_facts.append(quote_data)
            
        # 2. Screener.in Fundamentals
        fund_data = self._fetch_screener_fundamentals(symbol)
        if fund_data:
            lkb_facts.extend(fund_data)
            
        # 3. Macro & Yield Curve
        macro_data = self._fetch_macro_benchmarks()
        if macro_data:
            lkb_facts.extend(macro_data)
            
        return {"symbol": symbol, "facts": lkb_facts}
```

---

## 5. Local Caching & Rate-Limit Mitigation Strategy

To safeguard against IP blacklisting and ensure 100% offline access to previously analyzed assets:

1. **Equities EOD Fundamentals**: Cached locally for **24 hours**.
2. **Live Quotes & Delivery %**: Cached for **15 minutes** during Indian market hours (09:15 to 15:30 IST); cached indefinitely on weekends/holidays.
3. **Macro Benchmarks & G-Sec Yields**: Cached for **24 hours** (CCIL publishes benchmark curves once per day).
4. **Fallback Circuit Breaker**: If NSE blocks an IP or returns a 403, the engine seamlessly switches to Yahoo Finance (`.NS` / `.BO`) and displays a non-intrusive UI badge: `[Fallback: Yahoo Finance Historical Snapshot Active]`.
