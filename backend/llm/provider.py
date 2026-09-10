import json
import httpx
from typing import Dict, Any, Optional
from backend.config import settings

class LLMProvider:
    """Unified inference gateway supporting Local Ollama (gemma4:e4b) and Cloud Groq API."""

    @classmethod
    def generate_completion(cls, prompt: str, system_prompt: str = "", provider: Optional[str] = None) -> str:
        active_provider = provider or settings.ACTIVE_PROVIDER

        # 1. Try Groq Cloud if selected or if API key is provided
        if active_provider == "groq" and settings.GROQ_API_KEY:
            try:
                return cls._call_groq(prompt, system_prompt)
            except Exception as e:
                print(f"[LLMProvider] Groq failed, attempting Ollama: {e}")

        # 2. Local Ollama (Default: gemma4:e4b)
        try:
            return cls._call_ollama(prompt, system_prompt)
        except Exception as e:
            print(f"[LLMProvider] Ollama call failed: {e}")
            # If user provided a Groq key, fall back to Groq
            if settings.GROQ_API_KEY:
                try:
                    return cls._call_groq(prompt, system_prompt)
                except Exception as groq_err:
                    print(f"[LLMProvider] Groq fallback failed: {groq_err}")

        # 3. Deterministic Grounded Fallback (if Ollama is offline and no Groq key)
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
        with httpx.Client(timeout=45.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("response", "").strip()
            raise RuntimeError(f"Ollama returned HTTP {resp.status_code}: {resp.text}")

    @classmethod
    def _call_groq(cls, prompt: str, system_prompt: str) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": settings.GROQ_MODEL,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 1000
        }
        with httpx.Client(timeout=25.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()
            raise RuntimeError(f"Groq returned HTTP {resp.status_code}: {resp.text}")

    @classmethod
    def _deterministic_fallback(cls, prompt: str) -> str:
        """Heuristic fallback ensuring zero app crash if offline."""
        return (
            "FAIDA Grounding Engine Note: Local Ollama service is currently unreached. "
            "Displaying deterministic rule-based analysis directly from the Local Knowledge Base (LKB)."
        )
