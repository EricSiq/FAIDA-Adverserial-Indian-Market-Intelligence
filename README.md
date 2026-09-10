# FAIDA: Financial Adversarial Indian Data Agents

[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)](#)
[![Stack](https://img.shields.io/badge/Stack-Python%203.11%20%7C%20FastAPI%20%7C%20PyWebView-orange)](#)
[![LLM](https://img.shields.io/badge/LLM-Local%20Ollama%20(gemma4:e4b)%20%7C%20Groq%20Cloud%20API-green)](#)
[![Data](https://img.shields.io/badge/Data%20Sources-NSE%20%7C%20Screener.in%20%7C%20CCIL%20%7C%20MCX-purple)](#)

> **FAIDA** (*फ़ायदा* — "Benefit / Profit"): An offline-capable, lightweight desktop application hosting an adversarial swarm of AI agents designed to act as an uncompromising **Red Team / Devil's Advocate** for retail investment decisions in the Indian capital markets (Equities, Bonds, Commodities).

---

## 🧭 Core Architectural Pillars

1. **Lightweight Native Desktop**: Built using **PyWebView + FastAPI** on `localhost`, requiring < 120MB of RAM without any complex Node.js or Rust build toolchains.
2. **Grounded Local Knowledge Base (LKB)**: Zero hallucinations. The LLM is strictly constrained to cite deterministic numbers parsed from live NSE, Screener.in, and CCIL endpoints using `[LKB-XX]` tags. The UI renders these as clickable verification badges.
3. **Hybrid Local-First Inference**: Runs 100% locally on **`gemma4:e4b`** via Ollama, with an optional UI toggle to connect high-speed cloud providers (**Groq API** e.g. `llama-3.3-70b-versatile`, or Google Gemini 2.5 Flash).
4. **6-Level Adversarial Continuum Slider**: Calibrate the Red Team's tone dynamically from `100% Socratic Educator` (beginner-friendly analogies) to `100% Technical Finance / Quant Forensic` (zero fluff, pure balance sheet and volatility metrics).

---

## 📚 Project Documentation Hub

* **[01. System Architecture (`01_SYSTEM_ARCHITECTURE.md`)](file:///c:/Users/erics/Documents/AIML%20Projects/Adverserial%20Financial%20Agents/01_SYSTEM_ARCHITECTURE.md)**
  Detailed 7-agent micro-agent topology, LKB Grounding Engine, 6-level tone continuum, and low-memory desktop architecture.

* **[02. Data Sources & Scraping Matrix (`02_INDIAN_DATA_SOURCES_AND_SCRAPING_MATRIX.md`)](file:///c:/Users/erics/Documents/AIML%20Projects/Adverserial%20Financial%20Agents/02_INDIAN_DATA_SOURCES_AND_SCRAPING_MATRIX.md)**
  100% free data pipelines across Indian Equities (NSE/BSE, Screener.in), Fixed Income (CCIL 10Y G-Secs, RBI DBIE), Commodities (MCX), and news RSS, with cookie session handshakes and caching rules.

* **[03. Decision Framework & Roadmap (`03_DECISION_FRAMEWORK_AND_ROADMAP.md`)](file:///c:/Users/erics/Documents/AIML%20Projects/Adverserial%20Financial%20Agents/03_DECISION_FRAMEWORK_AND_ROADMAP.md)**
  Confirmed decisions log, the 5 remaining tactical decisions, and the phased implementation roadmap.
