from typing import Dict, Any, Optional
import os
import logging

logger = logging.getLogger("faida.scrapers.broker")

class BrokerClient:
    """Pluggable read-only broker gateway (Upstox, Angel One SmartAPI, Dhan).
    
    If credentials are not configured in .env, seamlessly falls back to public scrapers.
    """

    @classmethod
    def is_configured(cls) -> bool:
        return bool(os.getenv("BROKER_API_KEY", "").strip())

    @classmethod
    def get_broker_name(cls) -> str:
        return os.getenv("BROKER_NAME", "generic").lower()

    @classmethod
    def get_quote(cls, symbol: str) -> Optional[Dict[str, Any]]:
        """Attempts to retrieve live quote from configured broker; returns None if not configured or failed."""
        api_key = os.getenv("BROKER_API_KEY", "").strip()
        if not api_key:
            return None

        import re
        clean_symbol = re.sub(r"[^A-Z0-9&_-]", "", symbol.strip().upper().replace(".NS", "").replace(".BO", ""))
        broker = cls.get_broker_name()

        # Upstox V2 Quote Adapter Mock/Interface
        if broker == "upstox":
            try:
                import httpx
                url = f"https://api.upstox.com/v2/market-quote/quotes?instrument_key=NSE_EQ|{clean_symbol}"
                headers = {"Accept": "application/json", "Authorization": f"Bearer {api_key}"}
                with httpx.Client(timeout=3.0) as client:
                    resp = client.get(url, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json().get("data", {}).get(f"NSE_EQ:{clean_symbol}", {})
                        return {
                            "symbol": clean_symbol,
                            "last_price": data.get("last_price"),
                            "volume": data.get("volume"),
                            "open": data.get("ohlc", {}).get("open"),
                            "high": data.get("ohlc", {}).get("high"),
                            "low": data.get("ohlc", {}).get("low"),
                            "close": data.get("ohlc", {}).get("close"),
                            "source": "BROKER_UPSTOX"
                        }
            except Exception as e:
                logger.debug(f"Upstox API quote failed: {e}")

        return None
