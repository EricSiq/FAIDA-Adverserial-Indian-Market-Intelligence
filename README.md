# FAIDA: Financial Adversarial Indian Data Agents

[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)](#)
[![Stack](https://img.shields.io/badge/Stack-Python%203.11%20%7C%20FastAPI%20%7C%20PyWebView-orange)](#)
[![LLM](https://img.shields.io/badge/LLM-Local%20Ollama%20(gemma4:e4b)%20%7C%20Groq%20Cloud%20API-green)](#)
[![Data](https://img.shields.io/badge/Data%20Sources-NSE%20%7C%20Screener.in%20%7C%20CCIL%20%7C%20MCX-purple)](#)
[![Tests](https://img.shields.io/badge/Tests-35%2F35%20Passing%20(pytest)-brightgreen)](#)

> **FAIDA** (*फ़ायदा* — "Benefit / Profit"): An offline-capable, lightweight desktop application hosting an adversarial swarm of AI agents designed to act as an uncompromising **Red Team / Devil's Advocate** for retail investment decisions in the Indian capital markets (Equities, Bonds, Commodities).

---

## 🛠️ Tech Stack

FAIDA is engineered with a **Python-first, zero-overhead** philosophy. It avoids heavy browser runtimes (Electron/Chromium builds > 400MB) in favor of native OS webviews and local-first execution (< 120MB RAM idle).

| Layer | Technology | Purpose & Implementation Details |
| :--- | :--- | :--- |
| **Desktop Shell** | `PyWebView` | Native OS webview wrapper providing an ultra-lightweight desktop window without Node.js or Rust toolchain dependencies. |
| **API Server & IPC** | `FastAPI` + `Uvicorn` | Asynchronous IPC backend serving REST endpoints for thesis analysis, scenario simulations, macro metrics, and journal queries. |
| **Local LLM Engine** | `Ollama` (`gemma4:e4b` / `qwen3.5:4b`) | 100% offline, zero-subscription inference running on local GPU/CPU via IPv4 loopback (`127.0.0.1:11434`). |
| **Cloud LLM Gateway** | `Groq Cloud API` (`llama-3.3-70b-versatile`) | Optional cloud toggle for instant, low-latency inference on battery-constrained laptops. |
| **Scrapers & Market Data** | `yfinance`, `httpx`, `BeautifulSoup4` | Live NSE India quotes, historical bhavcopies (200 EMA), delivery ratios, Screener.in balance sheet forensics, and India VIX. |
| **Structured Evidence (LKB)** | `Pydantic v2` | Enforces rigid data schemas for the Local Knowledge Base (LKB), citation IDs (`[LKB-XX]`), and pre-mortem risk items. |
| **Local Decision Journal** | `DuckDB` | Embedded, zero-maintenance columnar SQL database for audit history, session replay, and pre-mortem validation tracking. |
| **Frontend UI** | HTML5, Vanilla CSS, Modern JavaScript | Dark-mode glassmorphic interface with zero npm/webpack dependencies, responsive micro-animations, and printable PDF styling. |
| **Testing & Quality** | `pytest`, `pytest-asyncio` | 35 automated test cases covering prompt-injection defenses, XSS escaping, ticker regex validation, DuckDB persistence, and scrapers. |

---

## 🌟 Core Features

### 1. 🧠 Cognitive Bias & Behavioral Traps Detector (`BiasAgent`)
Retail investors rarely lose money from a lack of data; they lose money from psychological traps. FAIDA intercepts and reframes:
* **Anchoring Bias**: Fixating on past peaks (*"Down from ₹1,200 to ₹600, so it's a bargain"*).
* **Loss Aversion / Sunk Cost**: Holding to "break even" rather than calculating opportunity costs against 7.1% risk-free G-Secs.
* **FOMO / Recency Bias**: Chasing rapid price velocity without institutional delivery volume confirmation.
* **Lottery Ticket Fallacy**: Asymmetric downside exposure in loss-making penny stocks.
* **Social Proof & Confirmation Bias**: Trading on unverified Telegram/WhatsApp tips without balance sheet audit.

### 2. ⚡ Interactive Macro Scenario Simulator ("What-If?" Stress Tester)
Allows the investor to challenge their thesis against sudden macroeconomic shocks:
* **🛢️ Brent Crude Surge ($95–$100/bbl)**: Evaluates input cost inflation on paint manufacturers, airlines, and auto OEMs.
* **🏦 RBI Repo Rate Hike (+25 bps)**: Evaluates borrowing cost spikes for NBFCs, real estate developers, and banks.
* **💵 USD/INR Depreciation (past ₹86.50)**: Evaluates margin expansion for IT/Pharma exporters vs. margin compression for importers.
* **📉 Margin Compression (-250 bps)**: Models operating deleverage and valuation multiple rerating.

### 3. 📊 India VIX Macro Weather Gauge
Live volatility indicator embedded in the top navbar classifying market regimes:
* **India VIX < 13**: *Low Volatility / Complacency* (Option sellers dominant; susceptible to exogenous shocks).
* **India VIX 13–18**: *Normal Indian Market Regime* (Standard variance; technical levels hold).
* **India VIX 18–24**: *Elevated Volatility* (Widen stop-loss thresholds; reduce position sizing).
* **India VIX > 24**: *Extreme Panic / Stress* (High drawdown regime; capital preservation preferred).

### 4. 📄 Exportable "Investment Pre-Mortem One-Pager" (Print / PDF)
Generates an institutional-grade, clean one-page PDF summary for personal trade journals:
* Proposed thesis, ticker, action, and target price.
* Grounded LKB Evidence Fact Sheet with timestamped snapshot.
* Cognitive Biases & Invalidation/Stop-Loss Levels.
* **Mandatory Pre-Trade Invalidation Checklist** and physical signature line before placing orders on Zerodha, Groww, or Angel One.
* *Example Template*: See [`docs/examples/sample_pre_mortem_one_pager.html`](file:///c:/Users/erics/Documents/AIML%20Projects/Adverserial%20Financial%20Agents/docs/examples/sample_pre_mortem_one_pager.html).

### 5. 🎚️ 6-Level Adversarial Continuum Slider
Calibrate the Red Team's personality from **Level 1 (100% Socratic Educator)** for beginners to **Level 6 (100% Forensic Quant / Roaster)** for experienced traders.

### 6. 🛡️ Grounded Local Knowledge Base (Zero Hallucinations)
The AI is strictly barred from inventing metrics. Every claim must cite verified numeric facts from the LKB using `[LKB-XX]` tags, which render as clickable verification pills in the UI.

---

## 🚀 Quickstart & Setup

### Prerequisites
* Windows 10/11, macOS, or Linux.
* Python 3.10+ (Python 3.11 recommended).
* (Optional for local offline inference) [Ollama](https://ollama.com/) with `gemma4:e4b` or `qwen3.5:4b` installed.

### 1-Click Launch (Windows)
Double-click `run.bat` or execute in PowerShell:
```cmd
run.bat
```
*The script automatically detects or creates a `.venv`, installs dependencies using `uv` (or standard `pip`), and boots the desktop app.*

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
copy .env.example .env

# 5. Launch desktop application
python main.py
```

---

## ⚙️ Configuration (`.env`)

FAIDA is pre-configured to run out of the box with zero external keys. To enable high-speed cloud fallback, configure `.env`:

```ini
# Active Provider: 'ollama' (Local) or 'groq' (Cloud)
FAIDA_PROVIDER=ollama
OLLAMA_MODEL=gemma4:e4b
OLLAMA_URL=http://127.0.0.1:11434

# Optional Cloud Acceleration
GROQ_API_KEY=your_free_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GEMINI_API_KEY=
```

---

## 🧪 Automated Test Suite

Run the full automated test suite covering all scrapers, models, parser, journal, bias detectors, and security endpoints:

```bash
.venv\Scripts\pytest.exe -v
```

**Status:** 35 / 35 passed (100% test coverage across all subsystems).

---

## 📚 Project Documentation Hub

* **[01. System Architecture (`01_SYSTEM_ARCHITECTURE.md`)](file:///c:/Users/erics/Documents/AIML%20Projects/Adverserial%20Financial%20Agents/01_SYSTEM_ARCHITECTURE.md)**:
  Detailed 7-agent topology, LKB Grounding Engine, 6-level tone continuum, and low-memory desktop architecture.
* **[02. Data Sources & Scraping Matrix (`02_INDIAN_DATA_SOURCES_AND_SCRAPING_MATRIX.md`)](file:///c:/Users/erics/Documents/AIML%20Projects/Adverserial%20Financial%20Agents/02_INDIAN_DATA_SOURCES_AND_SCRAPING_MATRIX.md)**:
  100% free data pipelines across Indian Equities (NSE/BSE, Screener.in), Fixed Income (CCIL 10Y G-Secs, RBI DBIE), Commodities (MCX), and news feeds.
* **[03. Decision Framework & Roadmap (`03_DECISION_FRAMEWORK_AND_ROADMAP.md`)](file:///c:/Users/erics/Documents/AIML%20Projects/Adverserial%20Financial%20Agents/03_DECISION_FRAMEWORK_AND_ROADMAP.md)**:
  Confirmed technical decisions log, architecture choices, and phased delivery roadmap.

---

## ⚖️ Regulatory & Educational Notice (SEBI Compliance)

Under Indian financial regulations (SEBI Research Analyst and Investment Adviser Regulations), automated systems providing investment advice face regulatory scrutiny.

**FAIDA is engineered strictly as an educational risk-awareness and pre-mortem invalidation tool.** It intentionally presents counter-theses to stress-test retail investor hypotheses. It does **NOT** provide buy/sell recommendations or SEBI-registered financial advisory services. All investments in Indian securities and commodities are subject to market risks.
