import httpx
from typing import Dict, Any, Optional
import time

class NSEClient:
    """Resilient client for unofficial NSE India public API endpoints."""

    BASE_URL = "https://www.nseindia.com"
    QUOTE_URL = "https://www.nseindia.com/api/quote-equity?symbol={symbol}"
    TRADE_INFO_URL = "https://www.nseindia.com/api/quote-equity?symbol={symbol}&section=trade_info"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/",
    }

    def __init__(self):
        self.session = httpx.Client(headers=self.HEADERS, timeout=10.0, follow_redirects=True)
        self.last_handshake = 0.0
        self._ensure_cookies()

    def _ensure_cookies(self):
        """Refresh cookie jar every 10 minutes or on first call."""
        now = time.time()
        if now - self.last_handshake > 600:
            try:
                self.session.get(self.BASE_URL)
                self.last_handshake = now
            except Exception as err:
                print(f"[NSEClient] Cookie handshake warning: {err}")

    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        clean_symbol = symbol.strip().upper().replace(".NS", "").replace(".BO", "")
        self._ensure_cookies()
        url = self.QUOTE_URL.format(symbol=clean_symbol)

        try:
            resp = self.session.get(url)
            if resp.status_code in (401, 403):
                # Re-handshake once
                self.session.get(self.BASE_URL)
                resp = self.session.get(url)

            if resp.status_code == 200:
                data = resp.json()
                price_info = data.get("priceInfo", {})
                sec_info = data.get("securityInfo", {})
                metadata = data.get("metadata", {})

                return {
                    "symbol": clean_symbol,
                    "company_name": data.get("info", {}).get("companyName", clean_symbol),
                    "last_price": price_info.get("lastPrice"),
                    "change": price_info.get("change"),
                    "pChange": price_info.get("pChange"),
                    "open": price_info.get("open"),
                    "high": price_info.get("intraDayHighLow", {}).get("max"),
                    "low": price_info.get("intraDayHighLow", {}).get("min"),
                    "previous_close": price_info.get("previousClose"),
                    "week_high_52": price_info.get("weekHighLow", {}).get("max"),
                    "week_low_52": price_info.get("weekHighLow", {}).get("min"),
                    "total_traded_volume": price_info.get("totalTradedVolume"),
                    "delivery_quantity": sec_info.get("deliveryQuantity"),
                    "delivery_to_traded_quantity": sec_info.get("deliveryToTradedQuantity"),
                    "series": metadata.get("series", "EQ"),
                    "source": "NSE_LIVE"
                }
        except Exception as err:
            print(f"[NSEClient] Error fetching quote for {clean_symbol}: {err}")
        return None
