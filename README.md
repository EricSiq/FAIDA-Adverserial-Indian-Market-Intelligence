# FAIDA: Financial Adversarial Indian Data Agents

[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)](#)
[![Stack](https://img.shields.io/badge/Stack-Python%203.11%20%7C%20FastAPI%20%7C%20PyWebView-orange)](#)
[![LLM](https://img.shields.io/badge/LLM-Local%20Ollama%20(gemma4:e4b)%20%7C%20Groq%20Cloud%20API-green)](#)
[![Data](https://img.shields.io/badge/Data%20Sources-NSE%20%7C%20Screener.in%20%7C%20CCIL%20%7C%20FRED%20%7C%20Web%20News-purple)](#)
[![Tests](https://img.shields.io/badge/Tests-55%2F55%20Passing%20(pytest)-brightgreen)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **FAIDA** (*Financial Adversarial Indian Data Agents*): An offline-capable, lightweight desktop application hosting an adversarial swarm of AI agents designed to act as an uncompromising **Red Team / Devil's Advocate** for retail investment decisions in the Indian capital markets (Equities, Bonds, Commodities).

---

## Tech Stack

FAIDA is engineered with a **Python-first, zero-overhead** philosophy. It avoids heavy browser runtimes (Electron/Chromium builds > 400MB) in favor of native OS webviews and local-first execution (< 120MB RAM idle).

| Layer | Technology | Purpose & Implementation Details |
| :--- | :--- | :--- |
| **Desktop Shell** | `PyWebView` | Native OS webview wrapper providing an ultra-lightweight desktop window without Node.js or Rust toolchain dependencies. |
| **API Server & IPC** | `FastAPI` + `Uvicorn` | Asynchronous IPC backend serving REST endpoints for thesis analysis, scenario simulations, macro metrics, cache maintenance, and journal queries. |
| **Local LLM Engine** | `Ollama` (`gemma4:e4b` / `qwen3.5:4b`) | 100% offline, zero-subscription inference running on local GPU/CPU via IPv4 loopback (`127.0.0.1:11434`). |
| **Cloud LLM Gateway** | `Groq Cloud API` (`llama-3.3-70b-versatile`) | Multi-model fallback inference with reasoning token cleanup, delivering sub-2s cloud execution. |
| **Scrapers & Market Data** | `curl_cffi`, `yfinance`, `httpx`, `BeautifulSoup4` | Resilient NSE scrapers with Chrome 120 TLS/JA3 impersonation, BSE corporate announcements, Screener.in 3-year CFO/PAT accrual forensics, and India VIX. |
| **Global Macro & News Intelligence** | `WebSearchClient`, `FREDClient`, `FinnhubClient` | Live Google News RSS search and Yahoo Finance news matching user-specific thesis keywords; live Brent Crude, US 10Y Treasury, and DXY via FRED API. |
| **Structured Evidence (LKB)** | `Pydantic v2` | Enforces rigid data schemas for the Local Knowledge Base (LKB), citation IDs (`[LKB-XX]`), and pre-mortem risk items. |
| **Local Feature Store & Caching** | `DuckDB` | Embedded sub-15ms feature cache with configurable TTL (15-minute equity packets) and automatic stale entry pruning. |
| **Local Decision Journal** | `DuckDB` | Embedded, zero-maintenance columnar SQL database for audit history, session replay, and pre-mortem validation tracking (strictly excluded from git). |
| **Report Export Engine** | `ReportLab` | Native institutional-grade PDF generator with strict XML escaping and clean print formatting. |
| **Frontend UI** | HTML5, Vanilla CSS, Modern JavaScript | Zerodha Kite & Bloomberg Terminal dark-mode interface with zero npm/webpack dependencies, infinite looping telemetry ticker, GFM markdown rendering, and printable PDF styling. |
| **Testing & Quality** | `pytest`, `pytest-asyncio` | 55 automated test cases covering prompt-injection defenses, XSS escaping, ticker regex validation, DuckDB persistence, scrapers, macro feeds, Finnhub, web search, and caching. |

---

## Core Features

### 1. Cognitive Bias & Behavioral Traps Detector (`BiasAgent`)
Retail investors rarely lose money from a lack of data; they lose money from psychological traps. FAIDA intercepts and reframes:
* **Anchoring Bias**: Fixating on past peaks (*"Down from ₹1,200 to ₹600, so it's a bargain"*).
* **Loss Aversion / Sunk Cost**: Holding to "break even" rather than calculating opportunity costs against 7.1% risk-free G-Secs.
* **FOMO / Recency Bias**: Chasing rapid price velocity without institutional delivery volume confirmation.
* **Lottery Ticket Fallacy**: Asymmetric downside exposure in loss-making penny stocks.
* **Social Proof & Confirmation Bias**: Trading on unverified Telegram/WhatsApp tips without balance sheet audit.

### 2. Interactive Macro Scenario Simulator ("What-If?" Stress Tester)
Allows the investor to challenge their thesis against sudden macroeconomic shocks:
* **Brent Crude Surge ($95–$100/bbl)**: Evaluates input cost inflation on paint manufacturers, airlines, and auto OEMs.
* **RBI Repo Rate Hike (+25 bps)**: Evaluates borrowing cost spikes for NBFCs, real estate developers, and banks.
* **USD/INR Depreciation (past ₹86.50)**: Evaluates margin expansion for IT/Pharma exporters vs. margin compression for importers.
* **Margin Compression (-250 bps)**: Models operating deleverage and valuation multiple rerating.

### 3. India VIX Macro Weather Gauge
Live volatility indicator embedded in the top navbar classifying market regimes:
* **India VIX < 13**: *Low Volatility / Complacency* (Option sellers dominant; susceptible to exogenous shocks).
* **India VIX 13–18**: *Normal Indian Market Regime* (Standard variance; technical levels hold).
* **India VIX 18–24**: *Elevated Volatility* (Widen stop-loss thresholds; reduce position sizing).
* **India VIX > 24**: *Extreme Panic / Stress* (High drawdown regime; capital preservation preferred).

### 4. Seamless Looping Macro Telemetry Ticker
Continuous 360° real-time scrolling ticker tape featuring comprehensive Indian and global market benchmarks:
* **Indian Benchmarks**: NIFTY 50, SENSEX, BANK NIFTY, INDIA VIX, NIFTY IT, G-SEC 10Y, RBI REPO RATE, FII/DII Net Flows.
* **Global Macro**: BRENT CRUDE (FRED), US 10Y YIELD (FRED), US DOLLAR INDEX (DXY), USD/INR Spot.
* **Commodities**: MCX Gold Spot (₹/10g), MCX Silver Spot (₹/1kg).
* *Interactive Pause*: Hovering over the ticker tape halts animation for closer metric inspection.

### 5. Query-Aware Deep Context & Live Web Intelligence
When the investor enters an argument (e.g. crude volatility headwinds, commercial vehicle expansion, safe dividend yield), FAIDA dynamically extracts thesis keywords, searches real-time news via Google News RSS and Yahoo Finance, and injects context-matched facts directly into the Local Knowledge Base.

### 6. Exportable Investment Pre-Mortem One-Pager (Native PDF / Print)
Generates an institutional-grade, clean single-page PDF summary for trade journals and audits:
* Proposed thesis, ticker, action, and target price.
* Grounded LKB Evidence Fact Sheet with timestamped snapshot.
* Cognitive Biases & Invalidation/Stop-Loss Levels.
* **Explainability References Layer**: Direct source links and citations for all scraped evidence (NSE Bhavcopy, Screener.in, BSE Filings, FRED Macro, Web News Catalysts).
* *Example Template*: See [`docs/examples/sample_pre_mortem_one_pager.html`](docs/examples/sample_pre_mortem_one_pager.html) and compiled PDF [`docs/examples/sample_pre_mortem_one_pager.pdf`](docs/examples/sample_pre_mortem_one_pager.pdf).

### 7. 6-Level Adversarial Continuum Slider
Calibrate the Red Team's personality from **Level 1 (Socratic Educator)** for beginners to **Level 6 (Forensic Quant Analyst)** for experienced traders.

### 8. Grounded Local Knowledge Base (Zero Hallucinations)
The AI is strictly barred from inventing metrics. Every claim must cite verified numeric facts from the LKB using `[LKB-XX]` tags, which render as clickable verification pills in the UI.

---

## Quickstart & Setup

### Prerequisites
* Windows 10/11, macOS, or Linux.
* Python 3.10+ (Python 3.11 recommended).
* (Optional for local offline inference) [Ollama](https://ollama.com/) with `gemma4:e4b` or `qwen3.5:4b` installed.

### 1-Click Launch

**Windows:**
Double-click `run.bat` or execute in PowerShell:
```cmd
run.bat
```

**Linux / macOS:**
Execute in terminal:
```bash
chmod +x run.sh
./run.sh
```
*The script automatically detects or creates a `.venv`, installs dependencies using `uv` (or standard `pip`), checks Ollama status, and boots the desktop app.*

### Manual Setup
```bash
# 1. Clone repository
git clone https://github.com/EricSiq/FAIDA-Adverserial-Indian-Market-Intelligence.git
cd FAIDA-Adverserial-Indian-Market-Intelligence

# 2. Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment (optional)
# On Windows:
copy .env.example .env
# On Linux/macOS:
cp .env.example .env

# 5. Launch desktop application
python main.py
```

---

## Configuration (`.env`)

FAIDA is pre-configured to run out of the box with zero external keys. To enable high-speed cloud fallback, configure `.env`:

```ini
# Active Provider: 'ollama' (Local) or 'groq' (Cloud)
FAIDA_PROVIDER=ollama
OLLAMA_MODEL=gemma4:e4b
OLLAMA_URL=http://127.0.0.1:11434

# Optional Cloud Acceleration (Groq API)
GROQ_API_KEY=your_free_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Global Macro & News APIs
FRED_API_KEY=your_free_fred_api_key_here
FINNHUB_API_KEY=your_free_finnhub_api_key_here
BROKER_API_KEY=
BROKER_NAME=upstox

# Local Feature Store Cache & Decision Journal
FEATURE_STORE_PATH=./data/faida_features.duckdb
DB_PATH=./data/faida_journal.duckdb
```

---

## Automated Test Suite

Run the full automated test suite covering all scrapers, models, parser, journal, bias detectors, macro feeds, caching, and security endpoints:

```bash
.venv\Scripts\pytest.exe -v
```

**Status:** 55 / 55 passed (100% test coverage across all subsystems).

---

## Project Documentation Hub

* **[01. System Architecture (`01_SYSTEM_ARCHITECTURE.md`)](01_SYSTEM_ARCHITECTURE.md)**:
  Detailed 7-agent topology, LKB Grounding Engine, 6-level tone continuum, and low-memory desktop architecture.
* **[02. Data Sources & Scraping Matrix (`02_INDIAN_DATA_SOURCES_AND_SCRAPING_MATRIX.md`)](02_INDIAN_DATA_SOURCES_AND_SCRAPING_MATRIX.md)**:
  100% free data pipelines across Indian Equities (NSE/BSE, Screener.in), Fixed Income (CCIL 10Y G-Secs, RBI DBIE), Commodities (MCX), and news feeds.
* **[03. Decision Framework & Roadmap (`03_DECISION_FRAMEWORK_AND_ROADMAP.md`)](03_DECISION_FRAMEWORK_AND_ROADMAP.md)**:
  Confirmed technical decisions log, architecture choices, and phased delivery roadmap.

---

## Regulatory & Educational Notice (SEBI Compliance)

Under Indian financial regulations (SEBI Research Analyst and Investment Adviser Regulations), automated systems providing investment advice face regulatory scrutiny.

**FAIDA is engineered strictly as an educational risk-awareness and pre-mortem invalidation tool.** It intentionally presents counter-theses to stress-test retail investor hypotheses. It does **NOT** provide buy/sell recommendations or SEBI-registered financial advisory services. All investments in Indian securities and commodities are subject to market risks.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
