import httpx
from typing import Dict, Any, List, Optional
import logging
import re
from datetime import datetime, timedelta

logger = logging.getLogger("faida.scrapers.bse")

class BSEClient:
    """Client for BSE India corporate announcements and regulatory governance filings."""

    BASE_URL = "https://api.bseindia.com/BseWebAPI/api/AnnSubCategoryGetData/w"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.bseindia.com/",
        "Origin": "https://www.bseindia.com"
    }

    # Taxonomy mapping for Top Indian Equities (NSE Symbol -> BSE Scrip Code)
    SCRIP_CODE_MAP = {
        "RELIANCE": "500325",
        "TCS": "532540",
        "HDFCBANK": "500180",
        "INFY": "500209",
        "ICICIBANK": "532174",
        "TATAMOTORS": "500570",
        "SBIN": "500112",
        "BHARTIARTL": "532454",
        "ITC": "500875",
        "ASIANPAINT": "500820",
        "MARUTI": "532500",
        "LT": "500510",
        "AXISBANK": "532215",
        "KOTAKBANK": "500247",
        "WIPRO": "507685"
    }

    @classmethod
    def get_announcements(cls, symbol: str, days_lookback: int = 60) -> List[Dict[str, Any]]:
        clean_symbol = symbol.strip().upper().replace(".NS", "").replace(".BO", "")
        scrip_code = cls.SCRIP_CODE_MAP.get(clean_symbol, "")

        if not scrip_code:
            return []

        to_date = datetime.now().strftime("%Y%m%d")
        from_date = (datetime.now() - timedelta(days=days_lookback)).strftime("%Y%m%d")

        params = {
            "pageno": "1",
            "strCat": "-1",
            "strPrevDate": from_date,
            "strScrip": scrip_code,
            "strSearch": "P",
            "strToDate": to_date,
            "strType": "C"
        }

        try:
            with httpx.Client(headers=cls.HEADERS, timeout=4.0) as client:
                resp = client.get(cls.BASE_URL, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    table = data.get("Table", []) if isinstance(data, dict) else []
                    return cls._parse_announcements(table)
        except Exception as err:
            logger.debug(f"BSE announcements fetch error for {clean_symbol}: {err}")

        return []

    @classmethod
    def _parse_announcements(cls, items: Any) -> List[Dict[str, Any]]:
        if not isinstance(items, list):
            return []
        parsed = []
        governance_keywords = [
            "resignation", "auditor", "credit rating", "downgrade", "sebi",
            "investigation", "penalty", "show cause", "default", "delay in payment",
            "pledge", "search", "income tax"
        ]

        for it in items[:15]:
            headline = str(it.get("NEWSSUB", "")).strip()
            details = str(it.get("HEADLINE", "")).strip()
            date_str = str(it.get("NEWS_DT", "")).strip()
            category = str(it.get("CATEGORYNAME", "")).strip()

            full_text = f"{headline} {details}".lower()
            is_risk_flag = any(kw in full_text for kw in governance_keywords)

            parsed.append({
                "date": date_str,
                "category": category,
                "headline": headline,
                "is_risk_flag": is_risk_flag,
                "source": "BSE_ANNOUNCEMENTS"
            })

        return parsed
