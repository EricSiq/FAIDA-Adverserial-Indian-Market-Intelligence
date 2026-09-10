import re
from typing import Optional
from backend.lkb.models import UserThesis, InvestmentAction, AssetClass, ToneLevel
from backend.llm.provider import LLMProvider

class ParserAgent:
    """Deconstructs user natural language inputs into a structured investment hypothesis."""

    KNOWN_SYMBOLS = {
        "RELIANCE": "RELIANCE", "RIL": "RELIANCE",
        "TATA MOTORS": "TATAMOTORS", "TATAMOTORS": "TATAMOTORS", "TTMT": "TATAMOTORS",
        "TCS": "TCS", "TATA CONSULTANCY": "TCS",
        "INFY": "INFY", "INFOSYS": "INFY",
        "HDFC": "HDFCBANK", "HDFC BANK": "HDFCBANK", "HDFCBANK": "HDFCBANK",
        "ICICI": "ICICIBANK", "ICICI BANK": "ICICIBANK", "ICICIBANK": "ICICIBANK",
        "ITC": "ITC", "SBIN": "SBIN", "SBI": "SBIN", "STATE BANK": "SBIN",
        "BHARTI": "BHARTIARTL", "AIRTEL": "BHARTIARTL", "BHARTIARTL": "BHARTIARTL",
        "KOTAK": "KOTAKBANK", "KOTAK BANK": "KOTAKBANK", "KOTAKBANK": "KOTAKBANK",
        "LT": "LT", "L&T": "LT", "LARSEN": "LT",
        "WIPRO": "WIPRO", "MARUTI": "MARUTI",
        "ZOMATO": "ZOMATO", "PAYTM": "PAYTM",
        "ADANI": "ADANIENT", "ADANI ENT": "ADANIENT", "ADANIENT": "ADANIENT",
        "ADANI PORTS": "ADANIPORTS", "ADANIPORTS": "ADANIPORTS",
        "TATA STEEL": "TATASTEEL", "TATASTEEL": "TATASTEEL",
        "BAJAJ FINANCE": "BAJFINANCE", "BAJFINANCE": "BAJFINANCE",
        "BAJAJ FINSERV": "BAJAJFINSV", "BAJAJFINSV": "BAJAJFINSV",
        "HINDUSTAN UNILEVER": "HINDUNILVR", "HUL": "HINDUNILVR", "HINDUNILVR": "HINDUNILVR",
        "ASIAN PAINTS": "ASIANPAINT", "ASIANPAINT": "ASIANPAINT",
        "TITAN": "TITAN", "SUN PHARMA": "SUNPHARMA", "SUNPHARMA": "SUNPHARMA",
        "NTPC": "NTPC", "ONGC": "ONGC", "POWER GRID": "POWERGRID", "POWERGRID": "POWERGRID",
        "COAL INDIA": "COALINDIA", "COALINDIA": "COALINDIA"
    }

    @classmethod
    def parse(cls, user_text: str, tone_level: int = 3) -> UserThesis:
        text_upper = user_text.upper()

        # 1. Detect Action (BUY / SELL / HOLD)
        action = InvestmentAction.BUY
        if any(w in text_upper for w in ["SELL", "EXIT", "BOOK PROFIT", "DUMP", "LIQUIDATE"]):
            action = InvestmentAction.SELL
        elif any(w in text_upper for w in ["HOLD", "STAY", "WAIT"]):
            action = InvestmentAction.HOLD

        # 2. Detect Symbol
        detected_symbol = "RELIANCE"  # Default fallback
        for key, sym in cls.KNOWN_SYMBOLS.items():
            if key in text_upper:
                detected_symbol = sym
                break
        else:
            # Try finding ticker like 2-10 capital letters
            words = re.findall(r"\b[A-Z]{3,12}\b", text_upper)
            for w in words:
                if w not in ["WANT", "STOCK", "PRICE", "RUPEES", "TODAY", "SHARE", "MARKET", "THINKING", "LOOKING", "SHOULD"]:
                    detected_symbol = w
                    break

        # 3. Detect Target Price
        target_price: Optional[float] = None
        price_matches = re.findall(r"(?:₹|RS\.?|INR|\@|AT)\s*([\d,]+(?:\.\d+)?)", user_text, re.IGNORECASE)
        if price_matches:
            try:
                target_price = float(price_matches[0].replace(",", ""))
            except ValueError:
                pass
        else:
            # Direct number match
            num_matches = re.findall(r"\b(\d{2,6}(?:\.\d+)?)\b", user_text)
            if num_matches:
                try:
                    target_price = float(num_matches[0])
                except ValueError:
                    pass

        try:
            tone_enum = ToneLevel(tone_level)
        except ValueError:
            tone_enum = ToneLevel.PRAGMATIC_RISK_OFFICER

        return UserThesis(
            raw_query=user_text,
            symbol=detected_symbol,
            exchange="NSE",
            asset_class=AssetClass.EQUITY,
            action=action,
            target_price=target_price,
            user_rationale=user_text,
            tone_level=tone_enum
        )
