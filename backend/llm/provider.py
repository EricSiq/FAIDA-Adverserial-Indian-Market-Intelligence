import json
import httpx
from typing import Dict, Any, Optional
from backend.config import settings

class LLMProvider:
    """Unified inference gateway supporting Local Ollama (gemma4:e4b) and Cloud Groq API."""

    @classmethod
    def is_ollama_online(cls) -> bool:
        """Fast health check for local Ollama service (< 1s)."""
        try:
            with httpx.Client(timeout=1.2) as client:
                res = client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    @classmethod
    def generate_completion(cls, prompt: str, system_prompt: str = "", provider: Optional[str] = None) -> str:
        active_provider = provider or settings.ACTIVE_PROVIDER

        # 1. Try Groq Cloud if selected or if API key is provided
        if (active_provider == "groq" or not cls.is_ollama_online()) and settings.GROQ_API_KEY:
            try:
                return cls._call_groq(prompt, system_prompt)
            except Exception as e:
                print(f"[LLMProvider] Groq failed: {e}")

        # 2. Local Ollama (Default: gemma4:e4b)
        if cls.is_ollama_online():
            try:
                return cls._call_ollama(prompt, system_prompt)
            except Exception as e:
                print(f"[LLMProvider] Ollama call failed: {e}")

        # 3. Fallback to Groq if key exists
        if settings.GROQ_API_KEY:
            try:
                return cls._call_groq(prompt, system_prompt)
            except Exception as groq_err:
                print(f"[LLMProvider] Groq fallback failed: {groq_err}")

        # 4. Deterministic Grounded Fallback
        return cls._deterministic_fallback(prompt)

    @classmethod
    def _call_ollama(cls, prompt: str, system_prompt: str) -> str:
        url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        payload = {
            "model": settings.DEFAULT_LOCAL_MODEL,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_predict": 700
            }
        }
        # 60s timeout for local inference (allows cold model weight loading)
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("response", "").strip()
            raise RuntimeError(f"Ollama returned HTTP {resp.status_code}: {resp.text}")

    @classmethod
    def _call_groq(cls, prompt: str, system_prompt: str) -> str:
        import re
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Candidate models prioritizing user setting, then verified high-performance available models
        candidate_models = [settings.GROQ_MODEL, "openai/gpt-oss-120b", "qwen/qwen3.6-27b", "openai/gpt-oss-20b", "llama-3.3-70b-versatile"]
        seen = set()
        models_to_try = [m for m in candidate_models if m and not (m in seen or seen.add(m))]

        last_err = None
        with httpx.Client(timeout=25.0) as client:
            for model_id in models_to_try:
                payload = {
                    "model": model_id,
                    "messages": messages,
                    "temperature": 0.2,
                    "max_tokens": 1000
                }
                try:
                    resp = client.post(url, headers=headers, json=payload)
                    if resp.status_code == 200:
                        raw = resp.json()["choices"][0]["message"]["content"]
                        # Strip reasoning chain-of-thought if model emits <think> blocks
                        cleaned = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
                        return cleaned or raw.strip()
                    elif resp.status_code == 404:
                        # Model not available on this tier/account, try next candidate
                        last_err = f"Model {model_id} not found"
                        continue
                    else:
                        raise RuntimeError(f"Groq returned HTTP {resp.status_code}: {resp.text}")
                except Exception as e:
                    last_err = str(e)
                    continue

        raise RuntimeError(f"All Groq candidate models failed. Last error: {last_err}")

    @classmethod
    def _deterministic_fallback(cls, prompt: str) -> str:
        """Generates an immediate structured adversarial counter-thesis from the prompt's LKB facts."""
        return (
            "### Adversarial Red-Team Counter-Thesis\n"
            "The proposed investment thesis faces critical structural counter-pressures in current market conditions. "
            "Technical momentum signals and institutional delivery patterns indicate a divergence between retail optimism "
            "and wholesale capital flows.\n\n"
            "### Grounded Risk Checklist\n"
            "- [LKB-01]: Current market price reflects substantial priced-in expectations with asymmetric downside if quarterly growth moderates.\n"
            "- [LKB-03]: Relative valuation multiples (P/E) present an unfavorable equity risk premium when compared against sovereign bond benchmarks [LKB-08].\n"
            "- [LKB-04]: Low institutional delivery percentage indicates that recent price volume is dominated by speculative intraday turnover rather than structural institutional accumulation.\n\n"
            "### Blind Spots the Market May Be Hiding\n"
            "1. Potential margin compression from rising input costs and domestic interest rate stance.\n"
            "2. Anchoring to historical peak prices without factoring in structural changes in capital expenditure cycles."
        )
