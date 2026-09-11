# 01. System Architecture: FAIDA (Financial Adversarial Indian Data Agents)

## 1. Executive Summary

**FAIDA** (*Financial Adversarial Indian Data Agents*—a play on the Hindi word *फ़ायदा*, meaning "benefit/profit") is an offline-first, lightweight desktop application designed for retail investors in the Indian capital markets. Rather than functioning as an echo-chamber that validates a user's confirmation bias, FAIDA serves as a **verifiable Red Team / Devil's Advocate**.

When a user proposes an investment hypothesis—such as:
* *"I want to sell Reliance Industries at ₹2,900 because it hit resistance"*
* *"I want to buy Tata Motors at ₹980 anticipating commercial vehicle expansion"*
* *"I want to park ₹5,00,000 in 10-Year Indian Government G-Secs at 7.1% yield"*
* *"I want to buy MCX Gold Mini contracts anticipating geopolitical escalation"*

FAIDA's swarm of micro-agents scrapes live, freely available Indian financial sources, builds a **Local Knowledge Base (LKB)** of grounded facts, and challenges the user's thesis. Every argument made by the LLM is strictly grounded in verifiable evidence with inline citations to protect retail investors from hallucinations.

---

## 2. High-Level Architecture Diagram

```mermaid
graph TD
    User([User / Retail Investor]) <--> UI[Lightweight Desktop Shell\nPyWebView + Modern Dark Glassmorphic Web UI]
    
    subgraph Desktop Application Process (RAM < 120MB)
        UI <--> IPC[FastAPI / Local ASGI Layer on localhost]
        IPC <--> Orchestrator[FAIDA Async State Machine Orchestrator]
        
        subgraph Multi-Agent Swarm Core
            Orchestrator --> AgentParser[1. Intent & Hypothesis Parser]
            AgentParser --> AgentTech[2. Technical & Liquidity Agent]
            AgentParser --> AgentFund[3. Fundamental Forensic Agent]
            AgentParser --> AgentMacro[4. Macro, Bonds & MCX Agent]
            AgentParser --> AgentGov[5. Forensic, Regulatory & News Agent]
            
            AgentTech --> Ingestion[Data Ingestion Hub]
            AgentFund --> Ingestion
            AgentMacro --> Ingestion
            AgentGov --> Ingestion
            
            Ingestion --> LKB[(Local Knowledge Base / LKB\nSession Grounding Engine)]
            
            LKB --> Debater[6. Red Team / Adversarial Agent\nControlled by 6-Level Tone Slider]
            Debater --> Educator[7. Grounded Synthesizer & Educator]
        end
        
        subgraph Grounded Inference Gateway
            Debater <--> LLMGateway{Grounding LLM Gateway}
            Educator <--> LLMGateway
            LLMGateway --> LocalLLM[Local Ollama: gemma4:e4b (Primary Local)\nFallback: qwen3.5:4b]
            LLMGateway -. Fast Cloud Toggle .-> CloudLLM[Cloud API: Groq (Llama-3.3-70b) / Gemini 2.5 Flash]
        end
    end
    
    subgraph Freely Available Indian Financial Endpoints
        Ingestion -.-> NSE[NSE India Live Quotes & Delivery %]
        Ingestion -.-> Screener[Screener.in 10Y Fundamentals]
        Ingestion -.-> MacroSrc[CCIL India Yield Curve & RBI DBIE]
        Ingestion -.-> MCXSrc[MCX Gold, Silver & Crude Watch]
        Ingestion -.-> NewsSrc[BSE Announcements & Moneycontrol RSS]
        Ingestion -.-> YF[Yahoo Finance .NS / .BO Price Series]
    end
```

---

## 3. The Multi-Agent Swarm Topology

To run reliably on lightweight 2B–4B parameter local models (such as `gemma4:e4b` or `qwen3.5:4b`) without context saturation, FAIDA avoids monolithic prompt templates. It utilizes an **Async State Machine** of atomic, single-turn micro-agents where each task has a strict sub-400 token prompt footprint:

```
[User Input] 
     │
     ▼
[1. Intent Parser] ───────────► Produces structured Hypothesis JSON
     │
     ▼
[Parallel Scraping Swarm] ────► Fetches NSE, Screener, CCIL, MCX, News
     │
     ▼
[Local Knowledge Base (LKB)] ──► Compiles deterministic Fact Table with Source Tags
     │
     ▼
[6. Adversarial Red-Team] ────► Generates Counter-Thesis (Constrained by LKB & Slider)
     │
     ▼
[7. Grounded Synthesizer] ────► Produces Pre-Mortem Report with Clickable Evidence Links
```

### Agent Roles & Specifications

1. **Intent & Hypothesis Parser**:
   * Extracts asset class (`EQUITY`, `BOND`, `COMMODITY`), ticker symbol, exchange (`NSE`/`BSE`/`MCX`), intended action (`BUY`/`SELL`/`HOLD`), price target, and user's underlying thesis.
2. **Technical & Liquidity Agent**:
   * Retrieves live quotes, 52-week range, delivery % vs 10-day average, 20/50/200 EMA positions, RSI(14), and average true range (ATR).
3. **Fundamental Forensic Agent**:
   * Parses Screener.in for valuation multiples (P/E vs historical median, PEG, Price/Book), balance sheet strength (Debt-to-Equity, Interest Coverage, Contingent Liabilities), promoter holding & pledging trends, and Free Cash Flow (CFO vs PAT).
4. **Macro, Bonds & MCX Correlation Agent**:
   * Evaluates cross-asset drivers: India 10Y Benchmark G-Sec yield (CCIL), RBI Repo Rate status, USD/INR currency trajectory, and MCX Crude/Gold volatility.
5. **Forensic, Regulatory & Sentiment Agent**:
   * Scans BSE corporate announcements for auditor resignations, board changes, credit rating downgrades, SEBI regulatory orders, and financial news headlines.
6. **The Adversarial Red-Team Engine ("Devil's Advocate")**:
   * Takes the user's intent and actively mounts the strongest possible counter-case using facts from the Local Knowledge Base.
7. **Grounded Synthesizer & Educational Mentor**:
   * Formats the counter-arguments into an actionable **Pre-Mortem Invalidation Report**, complete with plain-English educational explanations and an Adversarial Friction Score (AFS).

---

## 4. Grounding Engine: The Local Knowledge Base (LKB)

A critical hazard in financial AI applications is the "hallucination of numbers" (e.g., an LLM fabricating a P/E ratio or delivery percentage). FAIDA enforces a **Zero-Hallucination Grounding Rule**:

```
Raw Scraped Data 
      │
      ▼
Python Data Normalizer (Deterministic Math)
      │
      ▼
Local Knowledge Base (LKB JSON Fact Sheet)
      │
      ├── [LKB-01]: "Reliance Industries Current Price: ₹2,985.40 (NSE, 2026-09-10 14:00)"
      ├── [LKB-02]: "Trailing P/E: 28.4 vs 5-Yr Median P/E: 24.1 (Screener.in)"
      ├── [LKB-03]: "Promoter Pledging: 0.0% (Screener.in Q1-2026)"
      ├── [LKB-04]: "Delivery Volume: 24.2% vs 30-Day Avg 41.5% (NSE Bhavcopy)"
      └── [LKB-05]: "India 10Y Benchmark G-Sec Yield: 7.09% (CCIL India)"
      │
      ▼
Constrained Prompt to LLM:
"You MUST cite facts using [LKB-XX]. You are forbidden from introducing any number not present in the LKB."
```

### Explainability in the UI
In the user interface, every counter-argument contains clickable badge tags (e.g., `[NSE: Delivery 24.2%]` or `[Screener: P/E 28.4]`). Clicking on a badge opens the exact source timestamp and raw snippet from the Local Knowledge Base, allowing the user to verify the claim immediately.

---

## 5. The 6-Level Adversarial Persona Continuum

Different investors require different communication styles—from complete beginners learning financial concepts to seasoned quants looking for pure balance-sheet forensics. FAIDA features an interactive **6-Level Red-Team Slider**:

| Level | Persona Name | Tone & Interaction Style | Primary Target Audience |
| :---: | :--- | :--- | :--- |
| **1** | **100% Socratic Educator** | Gentle, beginner-first, zero hostile jargon. Explains fundamental concepts through real-world analogies (e.g., comparing P/E to buying a neighborhood kirana shop). Encouraging and patient. | Complete newcomers, students, first-time Demat account holders. |
| **2** | **Mindful Mentor** | Balanced caution with educational framing. Points out potential risks while explaining *why* those risks matter to retail investors (e.g., explains how interest rate cycles affect stock multiples). | Retail investors with < 1 year experience. |
| **3** | **Pragmatic Risk Officer (Default)** | Balanced institutional risk management tone. Objective, professional, structured around risk-reward asymmetry, stop-loss invalidation, and portfolio allocation. | Active retail swing/positional traders. |
| **4** | **Cynical Contrarian** | Highly skeptical of market narratives and "hot tips". Actively interrogates why the user believes they have an edge over institutional funds (FIIs/DIIs) in this specific trade. | Experienced traders seeking a genuine stress-test. |
| **5** | **Hardcore Short-Seller** | Aggressive forensic examiner. Zeroes in on governance red flags, accounting discrepancies, cyclical peak margins, promoter selling, and liquidity traps. | Advanced investors vetting high-conviction positions. |
| **6** | **100% Technical Finance / Quant Forensic** | Zero conversational fluff. Pure mathematical ratios, delivery volume spikes, beta, standard deviation, Altman Z-score, order-book depth, and macro rate curves. | Quantitative traders, finance professionals, CFAs. |

---

## 6. Desktop Stack: PyWebView + FastAPI

* **Backend Process**: FastAPI running on `localhost` managed by Python 3.11.
* **Desktop Window**: `pywebview` creates a native OS window (Windows Webview2 / macOS WebKit / Linux WebKitGTK) pointing to the local UI.
* **UI Layer**: Modern HTML5 + Vanilla CSS (dark-mode glassmorphic theme with HSL colors) + Vanilla JS.
* **System Footprint**:
  * Disk: ~45 MB (Python dependencies).
  * Runtime Memory: ~80–120 MB RAM (excluding local Ollama model).
  * Startup Time: < 1.5 seconds to native window launch.

---

## 7. Decision Persistence: DuckDB Investment Journal

FAIDA includes an embedded, zero-maintenance **DuckDB Journal** (`./data/faida_journal.duckdb`). 

Whenever the user consults FAIDA on an investment decision, the engine saves:
* **Session Metadata**: Ticker, timestamp, target price, proposed action (`BUY`/`SELL`).
* **LKB Fact Snapshot**: The exact valuation multiples, delivery percentages, and technical indicators at that moment.
* **Red-Team Counter-Thesis**: The specific risks and invalidation levels flagged.
* **Pre-Mortem Outcome Tracker**: Allows the user to revisit the trade weeks or months later to evaluate whether the Red Team's warnings materialized, serving as a feedback loop for personal investing education.

---

## 8. Regulatory & Educational Framing (SEBI Compliance)

Under Indian financial regulations (SEBI Research Analyst and Investment Adviser Regulations), automated tools providing definitive stock recommendations can face regulatory exposure.

FAIDA is engineered strictly as an **Adversarial Red-Team & Educational Invalidation Tool**. The UI features a permanent, elegant footer disclaimer:

> **Educational & Research Notice**: *FAIDA (Financial Adversarial Indian Data Agents) is an educational research and pre-mortem risk-awareness tool powered by public market data. It intentionally presents counter-arguments to test investor theses and does NOT provide buy/sell recommendations or SEBI-registered financial advisory services. All investments in Indian securities and commodities are subject to market risks.*

---

## 9. Phased Execution Architecture (Phases 1 & 2)

* **Phase 1: Core Swarm & Offline Grounding**:
  * NSE & BSE Equities (Large, Mid, Small caps).
  * Real-time quotes, delivery volume spikes, Screener.in balance sheet extraction, and 6-level Red-Team continuum.
  * Embedded DuckDB Decision Journal for trade audit trail.

* **Phase 2.1: Scraper Resilience & Anti-Bot Hardening**:
  * `curl_cffi` TLS/JA3 impersonation (`chrome120`) bypassing Cloudflare / Akamai WAF blocks on NSE India endpoints.
  * Screener.in 3-Year Cash Flow from Operations (CFO) vs. Net Profit (PAT) forensic accrual divergence calculation (`cfo_to_pat_ratio` < 0.70 red flag).
  * BSE Corporate Announcements client (`BSEClient`) with automated governance risk filters (auditor resignations, SEBI inquiries, rating downgrades).

* **Phase 2.2: Statistical LKB Context & Multi-Temporal Distributions**:
  * 52-Week Range Percentile distribution placement showing exact deviation from cyclic highs.
  * Multi-year cumulative CFO/PAT ratio facts integrated into LKB packets.
  * Dynamic India VIX volatility regime categorization and 10-Year Benchmark G-Sec spread calculation.

* **Phase 2.3: Global Macro Engine & Pluggable Broker API Gateway**:
  * `FREDClient` integration fetching Brent Crude oil, US 10-Year Treasury Yield, and Broad US Dollar Index (DXY) with calibrated offline fallbacks.
  * `BrokerClient` pluggable read-only interface supporting zero-friction adapters for Upstox, Angel One SmartAPI, and Dhan.

* **Phase 2.4: DuckDB Local Feature Store & Caching Layer**:
  * Sub-15ms high-frequency feature cache (`market_features_cache`) with 15-minute TTL for on-demand equity packets.
  * Thread-safe connection lifecycle with automatic stale record eviction (`clear_expired()`) and zero-repetition remote scraping.

---

## 10. Advanced Intelligence & Behavioral Protection Layer

1. **Cognitive Bias & Behavioral Traps Detector (`BiasAgent`)**:
   * Scans user natural language rationales for psychological vulnerabilities: *Anchoring Bias* (anchoring to 52-week peaks), *Loss Aversion / Sunk Cost* ("holding until breakeven"), *FOMO & Recency Bias* ("gained 20% in 3 days"), and *Lottery Ticket Fallacy* (loss-making penny stocks).
   * Automatically modifies the Adversarial Friction Score and injects actionable cognitive reframing advice.
2. **India VIX Macro Weather Gauge (`MacroClient`)**:
   * Live volatility tracker mapping market regimes: Low Volatility/Complacency (<13), Normal (13–18), Elevated Volatility (18–24), and Extreme Panic (>24).
3. **Interactive Scenario Stress Tester (`SimulatorAgent`)**:
   * Real-time "What-If?" simulator modeling sudden shocks: Crude Oil spiking to $95+, RBI hiking repo rates by 25 bps, USD/INR depreciating past ₹86.50, and raw material EBITDA margin compression.
4. **Institutional Pre-Mortem One-Pager Export (`PreMortemPDFGenerator`)**:
   * Clean, professional PDF generator engineered with ReportLab, featuring complete XML escaping to prevent injection vulnerabilities, comprehensive references/evidence audit trails, and zero print dependencies.

---

## 11. Future Scaling Architecture: Portfolio Bulk Audit

*(Planned for Phase 2 scaling)*

* **Consolidated Account Statement (CAS) & Broker CSV Ingestion**:
  * Allows investors to upload portfolio exports from Zerodha Kite, Groww, Upstox, or CAMS/KFintech CAS statements.
* **Portfolio-Wide Red-Team Audit**:
  * Identifies hidden systemic correlations (e.g. 60% portfolio exposure to interest-rate sensitive cyclicals).
  * Flags portfolio constituents with deteriorating promoter pledge ratios (>10%) or consecutive quarters of institutional distribution.

