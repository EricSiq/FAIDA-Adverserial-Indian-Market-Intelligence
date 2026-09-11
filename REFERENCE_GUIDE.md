# FAIDA: Reference Guide and Technical System Report
**Financial Adversarial Indian Data Agents: An Evidence-Grounded AI Red-Teaming Framework for Capital Markets**

---

## 1. Introduction

The integration of Artificial Intelligence in Banking and Financial Services (BFSI) has predominantly centered on predictive analytics, automated algorithmic execution, customer service automation, and sentiment extraction. However, the generative AI era has introduced a critical vulnerability into financial decision-making: sycophantic alignment and synthetic confabulation (hallucination). Standard large language models (LLMs) are optimized to satisfy conversational prompts, often validating user preconceptions and compounding cognitive biases rather than challenging unverified assumptions.

FAIDA (Financial Adversarial Indian Data Agents) is an offline-capable, evidence-grounded desktop system designed to reverse this dynamic. Operating as an automated "Red Team" or adversarial devil's advocate, FAIDA subjects retail and institutional investment theses in the Indian capital markets (Equities, Sovereign Debt, Commodities) to rigorous counter-analysis. By synthesizing live market microstructure data, fundamental forensic ratios, and macroeconomic benchmarks into an immutable Local Knowledge Base (LKB), FAIDA guarantees that every adversarial challenge is anchored in verified numerical facts rather than generative speculation.

---

## 2. Problem Statement and Statement of Need

### 2.1 The Retail Asymmetry in Indian Financial Markets
Over the past decade, Indian capital markets have experienced unprecedented retail financialization. Active demat accounts have expanded past 160 million, driven by zero-commission discount brokers, mobile trading interfaces, and digital payment infrastructure (UPI). Concurrently, retail participation in volatile derivatives (NSE index and stock options) has surged. A regulatory study conducted by the Securities and Exchange Board of India (SEBI) revealed that over 90% of active retail traders in the equity derivatives segment incur net capital losses.

### 2.2 Cognitive Biases in Investment Allocation
Retail capital destruction is rarely driven by a deficit of market data. Rather, it is propelled by systematic behavioral distortions:
* **Anchoring Bias**: Fixating on historic high-water marks (e.g., viewing a stock falling from INR 1,200 to INR 600 as intrinsically cheap, ignoring fundamental balance sheet degradation).
* **Sunk Cost Fallacy & Loss Aversion**: Refusing to liquidate losing positions to avoid acknowledging losses, while disregarding the risk-free benchmark yield offered by 10-Year Indian Government Sovereign Bonds (G-Secs at ~7.08%).
* **FOMO and Momentum Chasing**: Entering speculative positions during late-stage momentum spikes without institutional delivery volume support.
* **Confirmation Bias**: Actively seeking narratives on social forums (Telegram, YouTube, WhatsApp groups) that validate an existing trade thesis while discarding negative financial indicators.

### 2.3 The Failure of Conventional Conversational AI in Finance
When investors query commercial LLM interfaces regarding trade ideas, standard chatbots typically provide agreeable summaries, speculative target prices, and unverified data points. In high-stakes capital allocation, hallucinated price-to-earnings ratios, fabricated delivery volumes, or out-of-date sovereign bond yields present material financial risk. There is an urgent need for an AI architecture that operates under zero-trust assumptions, refuses to validate ungrounded optimism, and enforces deterministic numerical grounding before generating counter-arguments.

---

## 3. Technical Functionality and Operation Guide

### 3.1 System Requirements and Prerequisites
* **Operating System**: Windows 10/11 (64-bit), macOS 12+, or modern Linux distribution (Ubuntu 22.04+).
* **Python Runtime**: Python 3.10 or 3.11.
* **Memory & Storage**: Minimum 4 GB RAM (< 120 MB RAM footprint at runtime); 500 MB free disk space.
* **Network Connectivity**: Optional. The system functions fully offline when paired with local Ollama weights; live scrapers and cloud inference activate seamlessly when internet connectivity is present.

### 3.2 Installation and Setup
To initialize the application from source:

```bash
# 1. Clone the repository
git clone https://github.com/EricSiq/FAIDA-Adverserial-Indian-Market-Intelligence.git
cd FAIDA-Adverserial-Indian-Market-Intelligence

# 2. Establish isolated Python virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On Linux / macOS:
source .venv/bin/activate

# 3. Install core dependencies
pip install -r requirements.txt

# 4. Initialize environment configuration
# On Windows:
copy .env.example .env
# On Linux / macOS:
cp .env.example .env
```

### 3.3 Execution
The application provides one-click automated boot scripts:
* **Windows**: Execute `run.bat` or run `.venv\Scripts\python.exe main.py`.
* **Linux / macOS**: Execute `./run.sh` or run `python main.py`.

The backend ASGI server boots on `http://127.0.0.1:8765`, while the native desktop shell (`PyWebView`) renders the high-contrast Zerodha Kite / Bloomberg-inspired financial interface.

### 3.4 Inference Configuration
FAIDA utilizes a multi-tiered inference strategy configured via environment variables or the UI Settings modal:
* **Primary Cloud Gateway (Default)**: Groq Cloud API utilizing free, high-throughput models (`qwen/qwen3.8-27b`, with automated fallback across `qwen/qwen3.6-27b`, `openai/gpt-oss-120b`, and `llama-3.3-70b-versatile`). Delivers sub-1.5 second response latency.
* **Local Offline Fallback**: Local Ollama instance serving `gemma4:e4b` or `qwen3.5:4b` over IPv4 loopback (`http://127.0.0.1:11434`).
* **Deterministic Fallback Engine**: If neither cloud nor local LLM endpoints are reachable, FAIDA executes an internal rule-based synthesis engine, generating structured risk reports directly from the LKB facts without crashing.

---

## 4. Methodological Architecture

FAIDA is architected in six discrete, decoupled layers, adhering to the principle of deterministic evidence separation:

```
+-------------------------------------------------------------------------+
| Layer 1: Native Presentation Layer (PyWebView + Zerodha/Bloomberg UI)   |
+-------------------------------------------------------------------------+
                                    |
                                    v (HTTP / REST IPC on localhost:8765)
+-------------------------------------------------------------------------+
| Layer 2: API Gateway & IPC Server (FastAPI + Uvicorn Async Runtime)     |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| Layer 3: Multi-Agent Orchestration Swarm                                |
|   - Parser Agent (Intent & Hypothesis Extraction)                       |
|   - Bias Detection Agent (Cognitive Trap Flagging)                      |
|   - Ingestion Micro-Agents (NSE, BSE, Screener, FRED, Web News)         |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| Layer 4: Local Knowledge Base (LKB) Grounding Engine (Pydantic v2)      |
|   - Deterministic Numerical Fact Extraction                             |
|   - Citation Indexing ([LKB-01] to [LKB-XX])                            |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| Layer 5: Grounded Inference Gateway (LLMProvider)                       |
|   - Groq API (Default: qwen/qwen3.8-27b) -> Ollama (gemma4:e4b)         |
|   - Reasoning Token Sanitization (<think> tag stripping)                |
|   - Strict Citation Enforcement & Prompt Injection Defenses             |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| Layer 6: Persistence & Storage Layer (DuckDB Feature Store & Journal)   |
+-------------------------------------------------------------------------+
```

### 4.1 Layer 1: Presentation Layer
Built using vanilla HTML5, CSS3, and modern JavaScript, deliberately avoiding heavyweight frontend frameworks (React, Vue, Node.js runtime).
* **Aesthetic Philosophy**: High-contrast, institutional dark mode styled after professional trading terminals (Zerodha Kite, Bloomberg).
* **Continuous Telemetry Ribbon**: Real-time horizontally looping marquee displaying NIFTY 50, SENSEX, BANK NIFTY, INDIA VIX, G-SEC 10Y, RBI Repo Rate, Brent Crude, US 10Y Yield, DXY, and MCX Gold/Silver.
* **Interactive Markdown Renderer**: Offline-bundled markdown parser (`marked.min.js`) converting structured LLM analysis into headings, lists, and interactive citation badges.

### 4.2 Layer 2: API Gateway & IPC Layer
An asynchronous FastAPI runtime acting as the local inter-process communication bridge.
* Implements strict schema validation using Pydantic models.
* Enforces input sanitization against prompt injection attacks and malicious regex patterns.
* Exposes endpoints for hypothesis processing (`/api/analyze`), macro stress-testing (`/api/simulate`), system configuration (`/api/config`), decision history (`/api/history`), and audit report compilation (`/api/export/pdf`).

### 4.3 Layer 3: Multi-Agent Orchestration Swarm
The core investigative pipeline decomposes an investment thesis across specialized autonomous sub-agents:
1. **Hypothesis Parser Agent**: Parses freeform natural language text to isolate the underlying financial asset (NSE/BSE symbol), intended action (BUY, SELL, HOLD), entry price, time horizon, and core thesis rationale.
2. **Behavioral Bias Agent**: Evaluates the linguistic framing against established behavioral finance pathologies (Anchoring, Sunk Cost, FOMO, Gambler's Fallacy, Confirmation Bias) and calculates a quantified Friction Index (0-100).
3. **Market Microstructure & Scraper Agents**:
   * *NSE Live Scraper*: Employs TLS/JA3 fingerprint impersonation (`curl_cffi`) to extract real-time security quotes, circuit limits, and security-wise delivery percentage.
   * *Screener.in Forensic Agent*: Extracts multi-year financial statements, computing Cash Flow from Operations (CFO) versus Profit After Tax (PAT) accrual divergence.
   * *Global Macro & Web Search Agent*: Dynamically generates search queries based on the user thesis, querying Google News RSS (India) and Yahoo Finance to surface real-time corporate catalysts, litigation filings, and supply chain disruptions.

### 4.4 Layer 4: Local Knowledge Base (LKB) Grounding Engine
The architectural heart of FAIDA's zero-hallucination guarantee.
* All scraped quantitative metrics and qualitative news items are serialized into strongly-typed `LKBPacket` structures.
* Every metric receives a unique, sequential index tag (`[LKB-01]`, `[LKB-02]`, etc.) containing the parameter name, numeric value, observation timestamp, and authoritative source URI.
* The LLM is supplied *only* with the serialized LKB packet and is constrained by system instructions to reference facts exclusively through citation tags.

### 4.5 Layer 5: Grounded Inference Gateway
A unified model abstraction layer managing model dispatch, cascading failover, and output sanitization:
* **Primary Tier**: Groq Cloud API invoking `qwen/qwen3.8-27b`. If unavailable, automatically attempts fallback models (`qwen/qwen3.6-27b`, `openai/gpt-oss-120b`, `llama-3.3-70b`).
* **Secondary Tier**: Local Ollama server executing `gemma4:e4b` over IPv4 loopback.
* **Reasoning Sanitization**: For reasoning models that emit internal thoughts (e.g., DeepSeek R1 or Qwen reasoning variants), regex token sanitizers strip `<think>...</think>` blocks before the final synthesis is displayed to the user.
* **Adversarial Continuum Control**: A 6-level slider modulates prompt directives from Level 1 (Socratic Educator, using gentle structural analogies) to Level 6 (Forensic Quant Analyst, employing uncompromising institutional skepticism).

### 4.6 Layer 6: Persistence & Storage Layer
Embedded data persistence powered by DuckDB:
* **Feature Store (`faida_features.duckdb`)**: Columnar cache storing scraped market packets with a 15-minute Time-To-Live (TTL) for equity metrics and 24-hour TTL for corporate balance sheets, preventing redundant network requests.
* **Decision Journal (`faida_journal.duckdb`)**: Local audit store recording user theses, detected biases, counter-arguments, and pre-mortem risk factors for longitudinal trade review. Strictly excluded from version control to preserve user privacy.

---

## 5. Real-World Usage Scope in Banking and Finance

### 5.1 Retail WealthTech and Discount Broker Integration
Modern discount brokerages can deploy FAIDA as an intelligent "Speed Bump" or Pre-Trade Friction Engine. When a retail client attempts to allocate capital into high-risk, low-delivery securities or during extreme volatility spikes (India VIX > 22), FAIDA can automatically generate a contextual pre-mortem card, prompting the client to acknowledge specific downside risks before execution.

### 5.2 Wealth Management and Advisory Support
Registered Investment Advisers (RIAs) and wealth managers can leverage FAIDA to audit client-submitted portfolios. The system rapidly stress-tests client holdings against macroeconomic scenarios (e.g., crude oil surging to $100/barrel, USD/INR depreciating past 86.50, or repo rate hikes), providing advisors with objective, documented rationale to rebalance portfolios into defensive allocations.

### 5.3 Corporate Governance and Credit Risk Underwriting
Commercial banking credit officers evaluate loan applicants based on financial integrity and promoter reliability. FAIDA's fundamental forensic agent automatically flags red flags such as CFO/PAT accrual divergence (where reported net profits are high but operational cash flows remain negative), pledged promoter shareholdings, and pending litigation announcements disclosed to stock exchanges.

### 5.4 Internal Audit and Trade Surveillance
Compliance departments within institutional asset management firms can utilize FAIDA's Decision Journal to maintain an unalterable audit trail of investment rationales. By documenting that an investment committee reviewed countervailing evidence prior to position entry, firms establish compliance with fiduciary duty standards and Model Risk Management guidelines (such as Federal Reserve SR 11-7 / OCC 2011-12 standards).

---

## 6. Impact Overview and Regulatory Alignment

### 6.1 Enhancing Capital Allocation Efficiency
Financial market efficiency relies on the continuous pricing of risk. By supplying retail market participants with institutional-grade adversarial analysis, FAIDA democratizes sophisticated risk controls previously accessible only to hedge funds and quantitative proprietary trading desks. This dampens speculative retail bubbles, discourages participation in manipulated micro-cap schemes, and channels capital toward structurally sound enterprises.

### 6.2 Regulatory Compliance (SEBI RA/IA Regulations)
In the Indian regulatory landscape, automated advisory platforms frequently run afoul of the SEBI (Research Analysts) Regulations, 2014, and SEBI (Investment Advisers) Regulations, 2013, which prohibit algorithmic buy/sell recommendations without explicit client risk profiling and registration.
* **Compliance by Design**: FAIDA is fundamentally constructed as an educational, pre-mortem invalidation tool. It does not output price targets, buy signals, or asset allocation mandates.
* **Inherent Invalidation**: Its singular purpose is to articulate why an investment thesis might *fail*, prompting the investor to conduct independent due diligence and respect market risk.

### 6.3 Technical and Environmental Sustainability
By replacing multi-gigabyte browser frameworks with lightweight native OS webviews (`PyWebView`) and optimizing backend feature caching through DuckDB, FAIDA operates within minimal hardware parameters (< 120 MB RAM). Its ability to toggle between sub-second cloud inference and completely offline local LLM weights ensures that retail investors across emerging markets can access institutional-grade risk intelligence without requiring costly subscriptions or high-end GPU workstations.
