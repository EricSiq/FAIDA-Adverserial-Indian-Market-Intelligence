# 03. Decision Framework & Project Roadmap: FAIDA

## 1. Confirmed Decisions Log (All 11 Decisions Locked)

All strategic and tactical decisions for **FAIDA** have been finalized:

| # | Architecture Dimension | Selected Decision | Strategic Implementation Details |
| :---: | :--- | :--- | :--- |
| **1** | **Project Identity** | **FAIDA** (*Financial Adversarial Indian Data Agents*) | Memorable acronym playing on the Hindi word *फ़ायदा* ("profit/benefit"), contrasting with its adversarial red-teaming nature. |
| **2** | **Desktop Runtime** | **PyWebView + FastAPI (Localhost)** | Zero Node.js / Rust build complexity for the end-user; native OS window with dark-mode web UI; lightweight (< 120MB RAM). |
| **3** | **LLM Engine** | **Hybrid Local-First** | Out-of-the-box local inference via Ollama (**`gemma4:e4b`** as primary local, fallback `qwen3.5:4b`), with an optional UI settings toggle to connect high-speed cloud APIs (**Groq API** e.g. `llama-3.3-70b-versatile`, or Google Gemini 2.5 Flash). |
| **4** | **Agent Orchestration** | **Custom Lightweight Async State Machine** | Sub-400 token micro-prompts per turn. Eliminates heavy prompt templates from frameworks like CrewAI, preventing context saturation and drift on 3B–4B models. |
| **5** | **Tone & Persona** | **6-Level Continuum Slider** | Allows the user to calibrate the interaction from `Level 1: 100% Socratic Educator` (beginner analogies) to `Level 6: 100% Technical Finance / Quant Forensic` (zero fluff, pure balance-sheet metrics). |
| **6** | **Grounding & Explainability**| **Local Knowledge Base (LKB)** | Raw scraped market data is deterministically parsed into an LKB fact sheet before prompting. The LLM is strictly constrained to cite facts using `[LKB-XX]` tags. The UI renders these as clickable verification badges. |
| **7** | **Packaging & Setup** | **Single-Click `run.bat` Launcher** | Automatically detects Python 3.11, creates `.venv`, installs `requirements.txt`, checks Ollama connectivity, and boots the native desktop window. |
| **8** | **Decision Persistence** | **Local DuckDB Journal (`faida_journal.duckdb`)** | Automatically records each user thesis, target price, date, LKB snapshot, and the Adversarial Pre-Mortem report so users can track how warnings materialized over time. |
| **9** | **Scraping Cadence** | **Strictly On-Demand with 15-min Cache** | Scrapers trigger on user query; zero background CPU/network churn; fast local cache check prevents redundant external hits. |
| **10** | **Regulatory Framing** | **Permanent SEBI Educational Disclaimer** | A permanent, elegant UI footer banner clarifies that FAIDA is an educational pre-mortem/risk-awareness tool and does not provide SEBI-registered financial advisory services. |
| **11** | **Phase 1 Asset Scope** | **NSE & BSE Equities (Large, Mid, Small)** | Master equity technicals, Screener.in balance sheet forensics, and corporate red-teaming first; G-Secs, Bonds, and MCX commodities follow in Phase 2. |

---

## 2. Micro-Implementation Readiness Checklist

With all high-level and architectural decisions locked, only **3 operational defaults** need to be standardized during the initial code setup (we have already selected the best-practice defaults for you):

1. **Database File Location**:
   * Stored in the application root as `./data/faida_journal.duckdb` (automatically created and excluded from git if sensitive).
2. **Default Ollama Model String**:
   * Configured by default to `qwen3.5:4b` (verified as installed on your system), with automatic fallback to any available local model (`gemma4:e4b`, `qwen2.5:7b`) if requested.
3. **Default Port for Local FastAPI IPC**:
   * Binds to `127.0.0.1:8765` (isolated to localhost; port auto-increments if occupied).

**Conclusion: There are zero blocking decisions left. The project is ready for immediate Phase 1 implementation.**

---

## 3. Project Directory Layout (To be Built)

```
Adverserial Financial Agents/
│
├── run.bat                          # One-click Windows launcher
├── requirements.txt                 # Pinned dependencies
├── main.py                          # PyWebView entry point & launcher
│
├── backend/
│   ├── app.py                       # FastAPI ASGI application
│   ├── config.py                    # App configuration & Ollama/Cloud toggles
│   │
│   ├── scrapers/                    # Resilient Indian market scrapers
│   │   ├── nse_client.py            # NSE live quotes & delivery % with cookie session
│   │   ├── screener_client.py       # Screener.in 10-year fundamental ratios & red flags
│   │   └── yfinance_client.py       # Historical OHLCV, moving averages, RSI
│   │
│   ├── lkb/                         # Grounding Engine
│   │   ├── models.py                # Pydantic schemas for LKB facts and citations
│   │   └── builder.py               # Deterministic normalizer assembling the LKB Fact Sheet
│   │
│   ├── agents/                      # Custom Lightweight Async State Machine
│   │   ├── parser_agent.py          # User investment hypothesis deconstructor
│   │   ├── debater_agent.py         # 6-level Red-Team Devil's Advocate
│   │   ├── educator_agent.py        # Pre-Mortem synthesis & financial glossary
│   │   └── orchestrator.py          # State machine coordination loop
│   │
│   ├── llm/                         # Inference Gateway
│   │   ├── provider.py              # Unified interface for Ollama & Cloud APIs
│   │   └── ollama_client.py         # Local Ollama HTTP client (localhost:11434)
│   │
│   └── db/                          # Persistence
│       └── journal.py               # DuckDB thesis & pre-mortem history tracker
│
└── frontend/                        # Native PyWebView UI (Dark Glassmorphism)
    ├── index.html                   # Clean, single-page application shell
    ├── css/
    │   └── styles.css               # Modern dark-mode styling with HSL tokens
    └── js/
        ├── app.js                   # Chat interaction & IPC bridge
        ├── slider.js                # 6-Level Adversarial Continuum Slider
        └── lkb_viewer.js            # Clickable LKB citation & evidence inspector
```

---

## 4. Phased Implementation Roadmap

```mermaid
gantt
    title FAIDA Project Execution Roadmap
    dateFormat  YYYY-MM-DD
    section Phase 1: Core Scrapers & Grounding Hub
    run.bat & Python venv setup               :done, 2026-09-10, 1d
    NSE & Screener.in Resilient Scrapers      :active, 2026-09-11, 2d
    LKB Fact Sheet Generator (Zero-Hallucination):2026-09-13, 1d
    DuckDB Decision Journal Setup             :2026-09-14, 1d
    section Phase 2: Multi-Agent Red-Team Core
    Async State Machine & Parser Agent        :2026-09-15, 2d
    6-Level Adversarial Red-Team Engine       :2026-09-17, 2d
    Pre-Mortem Synthesizer with Citations     :2026-09-19, 1d
    section Phase 3: Desktop UI & PyWebView Shell
    FastAPI Localhost IPC API                 :2026-09-20, 1d
    Modern Dark Glassmorphic Web UI           :2026-09-21, 2d
    Tone Slider, Clickable LKB Badges & Radar :2026-09-23, 2d
    section Phase 4: Verification & End-to-End Demo
    Test Real Scenarios (e.g. Sell Reliance at 2900):2026-09-25, 2d
    Packaging, Offline Tests & SEBI Disclaimer:2026-09-27, 1d
```
