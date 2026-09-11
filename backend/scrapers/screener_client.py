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

        # Forensic Deep-Dive: Cash Flow from Operations (CFO) vs Net Profit (PAT)
        cfo_values: List[float] = []
        pat_values: List[float] = []

        cf_sec = soup.find("section", id="cash-flow")
        if cf_sec:
            for row in cf_sec.find_all("tr"):
                row_text = row.get_text(strip=True)
                if "cash from operating activity" in row_text.lower() or "operating activity" in row_text.lower():
                    cols = row.find_all("td")[1:]
                    for c in cols[-3:]:  # Last 3 reported fiscal years
                        num_str = re.sub(r"[^\d.-]", "", c.get_text(strip=True))
                        try:
                            cfo_values.append(float(num_str))
                        except ValueError:
                            pass
                    break

        pl_sec = soup.find("section", id="profit-loss")
        if pl_sec:
            for row in pl_sec.find_all("tr"):
                row_text = row.get_text(strip=True)
                if "net profit" in row_text.lower():
                    cols = row.find_all("td")[1:]
                    for c in cols[-3:]:  # Last 3 reported fiscal years
                        num_str = re.sub(r"[^\d.-]", "", c.get_text(strip=True))
                        try:
                            pat_values.append(float(num_str))
                        except ValueError:
                            pass
                    break

        # Compute Accrual Quality Divergence
        if cfo_values and pat_values and len(cfo_values) == len(pat_values):
            tot_cfo = sum(cfo_values)
            tot_pat = sum(pat_values)
            result["forensics"] = {
                "recent_cfo": cfo_values,
                "recent_pat": pat_values,
                "cumulative_3y_cfo": round(tot_cfo, 2),
                "cumulative_3y_pat": round(tot_pat, 2),
            }
            if tot_pat > 0:
                cfo_pat_ratio = round(tot_cfo / tot_pat, 2)
                result["forensics"]["cfo_to_pat_ratio"] = cfo_pat_ratio
                if cfo_pat_ratio < 0.70:
                    alert_msg = f"Forensic Accrual Risk: 3-Year CFO/PAT ratio is {cfo_pat_ratio} (Operating Cash Flow lags paper accounting Net Profit)."
                    result["red_flags"].append(alert_msg)
            elif tot_cfo < 0 and tot_pat <= 0:
                result["red_flags"].append("Severe Cash Burn: Company reports negative operating cash flow alongside accounting net losses.")
        else:
            result["forensics"] = {}

        return result

