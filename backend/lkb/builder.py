from typing import Dict, Any, List
import uuid
from datetime import datetime

from backend.lkb.models import (
    LKBPacket,
    LKBFact,
    LKBFactCategory,
    AssetClass
)
from backend.scrapers.yfinance_client import YFinanceClient
from backend.scrapers.screener_client import ScreenerClient
from backend.scrapers.nse_client import NSEClient

class LKBBuilder:
    """Consolidates scraped Indian market signals into a deterministic Local Knowledge Base (LKB)."""

    def __init__(self):
        self.nse_client = NSEClient()

    def build_equity_packet(self, symbol: str, exchange: str = "NSE") -> LKBPacket:
        clean_symbol = symbol.strip().upper().replace(".NS", "").replace(".BO", "")
        session_id = f"faida-{clean_symbol}-{uuid.uuid4().hex[:8]}"
        facts: List[LKBFact] = []
        fact_idx = 1

        # 1. Fetch Technical & Historical from Yahoo Finance
        yf_data = YFinanceClient.get_market_summary(clean_symbol, exchange)
        
        # 2. Fetch Fundamentals from Screener.in
        screener_data = ScreenerClient.get_fundamentals(clean_symbol)

        # 3. Fetch Live Quote & Delivery from NSE
        nse_data = self.nse_client.get_quote(clean_symbol) if exchange.upper() == "NSE" else None

        # Determine best current price
        current_price = 0.0
        if nse_data and nse_data.get("last_price"):
            current_price = float(nse_data["last_price"])
            price_src = "NSE_LIVE"
        elif yf_data.get("current_price"):
            current_price = float(yf_data["current_price"])
            price_src = "YFINANCE"
        else:
            price_src = "UNKNOWN"

        # Fact: Current Price
        if current_price > 0:
            facts.append(LKBFact(
                id=f"LKB-{fact_idx:02d}",
                category=LKBFactCategory.TECHNICAL,
                source=price_src,
                metric="Current Market Price",
                value=round(current_price, 2),
                unit="INR",
                context=f"Recorded at {datetime.now().strftime('%H:%M IST')}"
            ))
            fact_idx += 1

        # Fact: 52-Week Range
        high_52 = (nse_data.get("week_high_52") if nse_data else None) or yf_data.get("fifty_two_week_high")
        low_52 = (nse_data.get("week_low_52") if nse_data else None) or yf_data.get("fifty_two_week_low")
        if high_52 and low_52:
            pct_from_high = round(((high_52 - current_price) / high_52) * 100, 1) if current_price else 0.0
            facts.append(LKBFact(
                id=f"LKB-{fact_idx:02d}",
                category=LKBFactCategory.TECHNICAL,
                source="EXCHANGE",
                metric="52-Week High/Low",
                value=f"High: ₹{high_52} | Low: ₹{low_52}",
                unit="INR",
                context=f"Currently trading {pct_from_high}% below its 52-week peak."
            ))
            fact_idx += 1

        # Fact: Technical Indicators (EMA & RSI)
        if yf_data.get("rsi_14"):
            rsi_val = yf_data["rsi_14"]
            condition = "OVERSOLD (<30)" if rsi_val < 30 else ("OVERBOUGHT (>70)" if rsi_val > 70 else "NEUTRAL")
            facts.append(LKBFact(
                id=f"LKB-{fact_idx:02d}",
                category=LKBFactCategory.TECHNICAL,
                source="YFINANCE",
                metric="RSI (14-Day)",
                value=rsi_val,
                unit="Points",
                context=f"Momentum condition is {condition}."
            ))
            fact_idx += 1

        if yf_data.get("ema_200") and current_price:
            ema200 = yf_data["ema_200"]
            pos = "ABOVE" if current_price >= ema200 else "BELOW"
            pct_diff = round(((current_price - ema200) / ema200) * 100, 1)
            facts.append(LKBFact(
                id=f"LKB-{fact_idx:02d}",
                category=LKBFactCategory.TECHNICAL,
                source="YFINANCE",
                metric="200-Day Exponential Moving Average",
                value=ema200,
                unit="INR",
                context=f"Price is trading {pos} 200-EMA by {abs(pct_diff)}% (Long-term trend gauge)."
            ))
            fact_idx += 1

        # Fact: Delivery Percentage (NSE)
        if nse_data and nse_data.get("delivery_to_traded_quantity") is not None:
            deliv_pct = round(float(nse_data["delivery_to_traded_quantity"]), 2)
            facts.append(LKBFact(
                id=f"LKB-{fact_idx:02d}",
                category=LKBFactCategory.LIQUIDITY,
                source="NSE_BHAVCOPY",
                metric="Delivery Percentage",
                value=deliv_pct,
                unit="%",
                context="Low delivery (<25%) indicates speculative intraday churn; High delivery (>50%) indicates institutional accumulation."
            ))
            fact_idx += 1

        # Fact: Valuation Multiples (Screener.in)
        ratios = screener_data.get("ratios", {})
        pe_val = ratios.get("Stock P/E") or yf_data.get("trailing_pe")
        if pe_val:
            facts.append(LKBFact(
                id=f"LKB-{fact_idx:02d}",
                category=LKBFactCategory.VALUATION,
                source="SCREENER",
                metric="Price to Earnings (P/E)",
                value=pe_val,
                unit="x",
                context="Valuation multiple on trailing twelve-month earnings."
            ))
            fact_idx += 1

        roce_val = ratios.get("ROCE")
        if roce_val:
            facts.append(LKBFact(
                id=f"LKB-{fact_idx:02d}",
                category=LKBFactCategory.VALUATION,
                source="SCREENER",
                metric="Return on Capital Employed (ROCE)",
                value=roce_val,
                unit="%",
                context="Capital efficiency metric. >15% is generally considered wealth-creative in Indian equities."
            ))
            fact_idx += 1

        # Fact: Governance & Promoter Pledging
        pledge_val = ratios.get("Promoter Pledging", 0.0)
        facts.append(LKBFact(
            id=f"LKB-{fact_idx:02d}",
            category=LKBFactCategory.GOVERNANCE,
            source="SCREENER",
            metric="Promoter Pledged Shares",
            value=pledge_val,
            unit="%",
            context="Any pledge > 10% introduces severe margin call liquidation risks during market corrections."
        ))
        fact_idx += 1

        # Fact: Red Flags from Screener Cons
        red_flags = screener_data.get("red_flags", [])
        if red_flags:
            for flag in red_flags[:3]:
                facts.append(LKBFact(
                    id=f"LKB-{fact_idx:02d}",
                    category=LKBFactCategory.GOVERNANCE,
                    source="SCREENER_AUDIT",
                    metric="Forensic Audit Red Flag",
                    value=flag,
                    unit="",
                    context="Balance sheet / corporate governance caution flag identified by public financial audit."
                ))
                fact_idx += 1

        # Fact: Macro Benchmark (RBI / CCIL Baseline)
        facts.append(LKBFact(
            id=f"LKB-{fact_idx:02d}",
            category=LKBFactCategory.MACRO,
            source="CCIL_INDIA",
            metric="India 10-Year Benchmark G-Sec Yield",
            value=7.08,
            unit="%",
            context="Risk-free rate baseline against which equity earnings yield must provide an adequate equity risk premium."
        ))
        fact_idx += 1

        return LKBPacket(
            session_id=session_id,
            symbol=clean_symbol,
            exchange=exchange,
            asset_class=AssetClass.EQUITY,
            facts=facts,
            metadata={
                "company_name": screener_data.get("company_name") or (nse_data.get("company_name") if nse_data else clean_symbol),
                "has_nse_live": nse_data is not None,
                "red_flag_count": len(red_flags)
            }
        )
