"""
FAIDA: Financial Adversarial Indian Data Agents
Module: backend.scrapers.finnhub_client
Description:
    Finnhub Financial Data Ingestion Client.
    
    Provides real-time company news, ADR developments, and macroeconomic news catalysts
    for Indian equities that have American Depository Receipts (ADRs) or international coverage.
    
    Features & Fail-safes:
        - Symbol Mapping: Maps Indian tickers to their corresponding US ADR tickers
          (e.g., INFY -> INFY, HDFCBANK -> HDB, TATAMOTORS -> TTM, ICICIBANK -> IBN).
        - Multi-Tier Fallback: If no company-specific news is returned, gracefully queries
          broader global market news.
        - Zero-Key Tolerance: Returns empty list if FINNHUB_API_KEY is unset, enabling
          completely offline or baseline operation without throwing unhandled exceptions.
"""

import os
import httpx
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from backend.config import settings

logger = logging.getLogger("faida.scrapers.finnhub")

class FinnhubClient:
    """
    Client for Finnhub Financial API: Company News, Market Sentiment, and News Catalysts.
    Enriches LKB packets with global institutional sentiment and news catalysts.
    """

    BASE_URL = "https://finnhub.io/api/v1"

    # Known Indian ADRs / Global tickers mapped on Finnhub
    GLOBAL_SYMBOL_MAP = {
        "INFY": "INFY",
        "HDFCBANK": "HDB",
        "ICICIBANK": "IBN",
        "WIPRO": "WIT",
        "TATAMOTORS": "TTM",
        "DRREDDY": "RDY",
    }

    @classmethod
    def get_company_news(cls, symbol: str, days_lookback: int = 14, api_key: Optional[str] = None) -> List[Dict[str, Any]]:
        key = api_key if api_key is not None else (os.getenv("FINNHUB_API_KEY") or settings.FINNHUB_API_KEY or "").strip()
        if not key:
            return []

        clean_symbol = symbol.strip().upper().replace(".NS", "").replace(".BO", "")
        # Resolve to global/ADR symbol if available, otherwise query domestic ticker
        query_symbol = cls.GLOBAL_SYMBOL_MAP.get(clean_symbol, clean_symbol)

        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=days_lookback)).strftime("%Y-%m-%d")

        url = f"{cls.BASE_URL}/company-news"
        params = {
            "symbol": query_symbol,
            "from": from_date,
            "to": to_date
        }
        headers = {"X-Finnhub-Token": key}

        try:
            with httpx.Client(timeout=6.0) as client:
                resp = client.get(url, params=params, headers=headers)
                if resp.status_code == 200:
                    items = resp.json()
                    if isinstance(items, list) and len(items) > 0:
                        return cls._parse_articles(items[:3])
        except Exception as e:
            logger.debug(f"Finnhub company-news request error for {symbol}: {e}")

        # Fallback to general market news if no company-specific news
        return cls.get_general_market_news(api_key=key)

    @classmethod
    def get_general_market_news(cls, category: str = "general", api_key: Optional[str] = None) -> List[Dict[str, Any]]:
        key = api_key if api_key is not None else (os.getenv("FINNHUB_API_KEY") or settings.FINNHUB_API_KEY or "").strip()
        if not key:
            return []

        url = f"{cls.BASE_URL}/news"
        params = {"category": category}
        headers = {"X-Finnhub-Token": key}

        try:
            with httpx.Client(timeout=6.0) as client:
                resp = client.get(url, params=params, headers=headers)
                if resp.status_code == 200:
                    items = resp.json()
                    if isinstance(items, list):
                        return cls._parse_articles(items[:2])
        except Exception as e:
            logger.debug(f"Finnhub general news request error: {e}")

        return []

    @classmethod
    def _parse_articles(cls, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        parsed = []
        for it in items:
            headline = str(it.get("headline", "")).strip()
            summary = str(it.get("summary", "")).strip()
            source = str(it.get("source", "Finnhub")).strip()
            url = str(it.get("url", "")).strip()
            if headline:
                parsed.append({
                    "headline": headline,
                    "summary": summary[:240],
                    "source": source,
                    "url": url,
                    "datetime": it.get("datetime")
                })
        return parsed
