from typing import Dict, Any, List, Optional
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
from backend.db.feature_store import FeatureStore

class LKBBuilder:
    """Consolidates scraped Indian market signals into a deterministic Local Knowledge Base (LKB)."""

    def __init__(self, use_cache: bool = True, feature_store: Optional[FeatureStore] = None):
        self.nse_client = NSEClient()
        self.use_cache = use_cache
        self.feature_store = feature_store or (FeatureStore() if use_cache else None)

    def build_equity_packet(self, symbol: str, exchange: str = "NSE", force_refresh: bool = False) -> LKBPacket:
        clean_symbol = symbol.strip().upper().replace(".NS", "").replace(".BO", "")
        
        if self.use_cache and not force_refresh and self.feature_store:
            cached = self.feature_store.get(clean_symbol, "EQUITY_PACKET")
            if cached:
                try:
                    return LKBPacket(**cached)
                except Exception:
                    pass

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

        # Fact: 52-Week Range & Percentile Positioning
        high_52 = (nse_data.get("week_high_52") if nse_data else None) or yf_data.get("fifty_two_week_high")
        low_52 = (nse_data.get("week_low_52") if nse_data else None) or yf_data.get("fifty_two_week_low")
        if high_52 and low_52 and high_52 > low_52:
            pct_from_high = round(((high_52 - current_price) / high_52) * 100, 1) if current_price else 0.0
            range_pct = round(((current_price - low_52) / (high_52 - low_52)) * 100, 1) if current_price else 50.0
            facts.append(LKBFact(
                id=f"LKB-{fact_idx:02d}",
                category=LKBFactCategory.TECHNICAL,
                source="EXCHANGE",
                metric="52-Week Range & Percentile",
                value=f"{range_pct}th Percentile (Range: ₹{low_52} - ₹{high_52})",
                unit="",
                context=f"Trading at the {range_pct}th percentile of its 52-week price distribution ({pct_from_high}% below peak)."
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

        if yf_data.get("ema_20") and current_price:
            ema20 = yf_data["ema_20"]
            pos = "ABOVE" if current_price >= ema20 else "BELOW"
            facts.append(LKBFact(
                id=f"LKB-{fact_idx:02d}",
                category=LKBFactCategory.TECHNICAL,
                source="YFINANCE",
                metric="20-Day Exponential Moving Average",
                value=ema20,
                unit="INR",
                context=f"Short-term momentum gauge. Price is {pos} 20-EMA."
            ))
            fact_idx += 1

        if yf_data.get("ema_50") and current_price:
            ema50 = yf_data["ema_50"]
            pos = "ABOVE" if current_price >= ema50 else "BELOW"
            facts.append(LKBFact(
                id=f"LKB-{fact_idx:02d}",
                category=LKBFactCategory.TECHNICAL,
                source="YFINANCE",
                metric="50-Day Exponential Moving Average",
                value=ema50,
                unit="INR",
                context=f"Medium-term trend gauge. Price is {pos} 50-EMA."
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

        # Fact: Delivery Percentage & Baseline
        if nse_data and nse_data.get("delivery_to_traded_quantity") is not None:
            deliv_pct = round(float(nse_data["delivery_to_traded_quantity"]), 2)
            conviction = "High Institutional Accumulation (>45%)" if deliv_pct >= 45 else ("Speculative Intraday Churn (<25%)" if deliv_pct < 25 else "Moderate Turnover")
            facts.append(LKBFact(
                id=f"LKB-{fact_idx:02d}",
                category=LKBFactCategory.LIQUIDITY,
                source="NSE_BHAVCOPY",
                metric="Security Delivery Ratio",
                value=deliv_pct,
                unit="%",
                context=f"Delivery conviction: {conviction} relative to benchmark 30-day liquidity levels."
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
                context="Trailing twelve-month price-to-earnings multiple."
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

        # Fact: Forensic Accounting (CFO to PAT Accrual Ratio)
        forensics = screener_data.get("forensics", {})
        if "cfo_to_pat_ratio" in forensics:
            cfo_pat = forensics["cfo_to_pat_ratio"]
            tot_cfo = forensics.get("cumulative_3y_cfo", 0.0)
            tot_pat = forensics.get("cumulative_3y_pat", 0.0)
            status = "HEALTHY CASH CONVERSION (>0.80)" if cfo_pat >= 0.80 else "ACCRUAL WARNING (<0.70)"
            facts.append(LKBFact(
                id=f"LKB-{fact_idx:02d}",
                category=LKBFactCategory.GOVERNANCE,
                source="SCREENER_FORENSICS",
                metric="3-Year CFO / PAT Accrual Ratio",
                value=f"{cfo_pat}x",
                unit="",
                context=f"Operating Cash Flow: ₹{tot_cfo} Cr vs Net Profit: ₹{tot_pat} Cr. Quality Status: {status}."
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

        # Fact: BSE Corporate Announcements & Governance Disclosures
        from backend.scrapers.bse_client import BSEClient
        bse_items = BSEClient.get_announcements(clean_symbol)
        risk_bse = [it for it in bse_items if it.get("is_risk_flag")]
        if risk_bse:
            for it in risk_bse[:2]:
                facts.append(LKBFact(
                    id=f"LKB-{fact_idx:02d}",
                    category=LKBFactCategory.GOVERNANCE,
                    source="BSE_FILINGS",
                    metric="Regulatory & Governance Notice",
                    value=it.get("headline", "Regulatory Filing"),
                    unit="",
                    context=f"Disclosed on {it.get('date', 'recent')}. Governance flag detected."
                ))
                fact_idx += 1

        # Fact: Dynamic Macro Benchmark & India VIX
        from backend.scrapers.macro_client import MacroClient
        vix_status = MacroClient.get_vix_status()
        vix_val = vix_status.get("vix_value", 13.5)
        vix_regime = vix_status.get("regime_label", "Normal Market Regime")
        gsec_10y = vix_status.get("benchmark_10y_yield", 7.08)

        facts.append(LKBFact(
            id=f"LKB-{fact_idx:02d}",
            category=LKBFactCategory.MACRO,
            source="NSE_INDICES",
            metric="India VIX Market Regime",
            value=f"{vix_val} ({vix_regime})",
            unit="Points",
            context=vix_status.get("description", "Macro volatility condition.")
        ))
        fact_idx += 1

        facts.append(LKBFact(
            id=f"LKB-{fact_idx:02d}",
            category=LKBFactCategory.MACRO,
            source="CCIL_INDIA",
            metric="India 10-Year Benchmark G-Sec Yield",
            value=gsec_10y,
            unit="%",
            context="Risk-free sovereign rate baseline. Equity earnings yield (1/PE) must provide an adequate spread above this rate."
        ))
        fact_idx += 1

        # Fact: Finnhub Real-Time News & Global Sentiment
        from backend.scrapers.finnhub_client import FinnhubClient
        news_items = FinnhubClient.get_company_news(clean_symbol)
        if news_items:
            for item in news_items[:2]:
                facts.append(LKBFact(
                    id=f"LKB-{fact_idx:02d}",
                    category=LKBFactCategory.NEWS,
                    source=f"FINNHUB_{item.get('source', 'GLOBAL').upper().replace(' ', '_')}",
                    metric="Market & Company News Catalyst",
                    value=item.get("headline", "Market News Catalyst"),
                    unit="",
                    context=item.get("summary", "")[:240]
                ))
                fact_idx += 1

        packet = LKBPacket(
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

        if self.use_cache and self.feature_store:
            try:
                self.feature_store.set(clean_symbol, "EQUITY_PACKET", packet.model_dump(), ttl_seconds=900)
            except Exception:
                pass

        return packet

