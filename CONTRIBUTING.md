# Contributing to FAIDA

Thank you for your interest in contributing to **FAIDA** (*Financial Adversarial Indian Data Agents*)!

FAIDA is an open-source, offline-first adversarial intelligence desktop tool designed to protect retail investors in Indian capital markets from cognitive traps, speculation, and confirmation bias through deterministic evidence and AI red-teaming.

---

## Guiding Principles

1. **Deterministic Evidence (Zero Hallucination)**:
   - Claims made by the AI must cite verified numeric facts from the Local Knowledge Base (`[LKB-XX]`).
   - Scrapers must cleanly handle missing fields, structural HTML changes, and rate limits without crashing.

2. **Offline-First & Lightweight**:
   - The application must boot quickly and operate comfortably within < 120MB idle RAM.
   - Heavy runtimes (Electron/Node builds) and bloated agent frameworks are intentionally avoided.

3. **SEBI Educational Compliance**:
   - FAIDA is strictly an educational risk-awareness and pre-mortem tool.
   - Never add features that generate algorithmic buy/sell recommendations or violate SEBI advisory guidelines.

---

## Development Setup

### 1. Fork and Clone
```bash
git clone https://github.com/<your-username>/FAIDA-Adverserial-Indian-Market-Intelligence.git
cd FAIDA-Adverserial-Indian-Market-Intelligence
```

### 2. Create Virtual Environment
```bash
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On Linux / macOS:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Copy the example environment configuration:
```bash
cp .env.example .env
```
Configure your preferred settings (e.g. `FAIDA_PROVIDER=ollama` or `groq`).

---

## Running Tests

Every contribution must pass the full test suite before submitting a Pull Request:

```bash
pytest -v
```

Ensure that:
* All existing test cases pass (56/56).
* New features include corresponding unit and integration tests in `tests/`.
* Code syntax compiles cleanly with `python -m compileall backend tests main.py`.

---

## Pull Request Guidelines

1. **Branch Naming**:
   - `feat/feature-name` for new capabilities.
   - `fix/bug-description` for bug fixes.
   - `docs/doc-update` for documentation improvements.

2. **Commit Conventions**:
   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat(scrapers): add MCX crude oil scraper`
   - `fix(pdf): handle unescaped XML ampersand in company names`
   - `test(bias): add unit tests for gambler's fallacy`

3. **Security & Secrets**:
   - Never commit `.env` or personal API keys.
   - All external user input must be sanitized against prompt injection and XSS.

---

## License

By contributing to FAIDA, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
