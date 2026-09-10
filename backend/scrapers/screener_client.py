import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
import re

class ScreenerClient:
    """Scrapes Screener.in for Indian equities fundamental ratios, balance sheet health, and red flags."""

    BASE_URL = "https://www.screener.in/company/{symbol}/consolidated/"
    FALLBACK_URL = "https://www.screener.in/company/{symbol}/"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    @staticmethod
    def _sanitize_symbol(symbol: str) -> Optional[str]:
        if not symbol or not isinstance(symbol, str):
            return None
        clean = symbol.strip().upper().replace(".NS", "").replace(".BO", "")
        if re.fullmatch(r"^[A-Z0-9&_-]{1,20}$", clean):
            return clean
        return None

    @classmethod
    def get_fundamentals(cls, symbol: str) -> Dict[str, Any]:
        clean_symbol = cls._sanitize_symbol(symbol)
        if not clean_symbol:
            return {"symbol": symbol, "error": "Invalid symbol format", "source": "SCREENER"}

        url = cls.BASE_URL.format(symbol=clean_symbol)
        try:
            with httpx.Client(headers=cls.HEADERS, timeout=12.0, follow_redirects=True) as client:
                resp = client.get(url)
                if resp.status_code == 404:
                    # Fall back to standalone if consolidated does not exist
                    resp = client.get(cls.FALLBACK_URL.format(symbol=clean_symbol))
                
                if resp.status_code != 200:
                    return {"symbol": clean_symbol, "error": f"HTTP {resp.status_code}", "source": "SCREENER"}

                return cls._parse_html(resp.text, clean_symbol)
        except Exception as e:
            return {"symbol": clean_symbol, "error": str(e), "source": "SCREENER"}

    @classmethod
    def _parse_html(cls, html: str, symbol: str) -> Dict[str, Any]:
        soup = BeautifulSoup(html, "html.parser")
        result: Dict[str, Any] = {
            "symbol": symbol,
            "company_name": "",
            "ratios": {},
            "pros": [],
            "cons": [],
            "red_flags": [],
            "source": "SCREENER"
        }

        # Company Title
        title_tag = soup.find("h1", class_="margin-0") or soup.find("h1")
        if title_tag:
            result["company_name"] = title_tag.get_text(strip=True)

        # Top Ratios Box
        ratios_container = soup.find("ul", id="top-ratios")
        if ratios_container:
            for item in ratios_container.find_all("li"):
                name_tag = item.find("span", class_="name")
                val_tag = item.find("span", class_="number") or item.find("span", class_="value")
                if name_tag and val_tag:
                    name = name_tag.get_text(strip=True)
                    val_str = val_tag.get_text(strip=True).replace(",", "")
                    try:
                        val = float(val_str)
                    except ValueError:
                        val = val_str
                    result["ratios"][name] = val

        # Pros and Cons
        pros_card = soup.find("div", class_="pros")
        if pros_card:
            result["pros"] = [li.get_text(strip=True) for li in pros_card.find_all("li")]

        cons_card = soup.find("div", class_="cons")
        if cons_card:
            result["cons"] = [li.get_text(strip=True) for li in cons_card.find_all("li")]

        # Extract specific red-flag indicators from Cons
        for con in result["cons"]:
            lower_con = con.lower()
            if any(term in lower_con for term in ["promoter", "interest coverage", "debt", "contingent", "tax rate", "cash flow", "pledged", "low return"]):
                result["red_flags"].append(con)

        # Extract Shareholding & Promoter Pledging from Shareholding Table
        shareholding_sec = soup.find("section", id="shareholding")
        if shareholding_sec:
            pledge_match = re.search(r"Pledged\s*percentage[:\s]*([\d\.]+)%", shareholding_sec.get_text())
            if pledge_match:
                result["ratios"]["Promoter Pledging"] = float(pledge_match.group(1))

        return result
