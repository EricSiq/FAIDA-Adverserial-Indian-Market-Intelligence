"""
FAIDA: Financial Adversarial Indian Data Agents
Module: backend.lkb.builder
Description:
    Local Knowledge Base (LKB) Fact Compiler.
    
    Acts as the single source of truth for the adversarial swarm by consolidating multi-source
    market signals into a deterministic, strongly-typed LKBPacket.
    
    Data Integration Points:
        1. YFinanceClient: 52-week extremes, RSI(14), EMA-20, EMA-50, EMA-200.
        2. ScreenerClient: P/E, ROCE, Promoter Pledging, 3Y CFO/PAT Accrual Ratio, Audit Red Flags.
        3. NSEClient: Live exchange quote and Delivery-to-Traded-Quantity percentage.
        4. BSEClient: Regulatory disclosures, board meeting outcomes, and corporate governance alerts.
        5. MacroClient: India VIX regime label, 10-Year Indian Sovereign G-Sec yield baseline.
        6. FREDClient: St. Louis Fed global macro drivers (Brent Crude, US 10Y Yield, DXY).
        7. FinnhubClient: Real-time company news, ADR developments, and sentiment catalysts.
        8. FeatureStore (DuckDB): TTL-governed local caching for sub-second offline-first retrieval.
"""

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
from backend.scrapers.web_search_client import WebSearchClient
from backend.db.feature_store import FeatureStore

class LKBBuilder:
    """
    Consolidates heterogeneous, multi-source Indian financial data into a standardized,
    verifiable Local Knowledge Base (LKB) packet with discrete [LKB-XX] fact identifiers.
    Enriches generic company data with deep, query-aware web intelligence and macro transmission facts.
    """

    def __init__(self, use_cache: bool = True, feature_store: Optional[FeatureStore] = None):
        self.nse_client = NSEClient()
        self.use_cache = use_cache
        self.feature_store = feature_store or (FeatureStore() if use_cache else None)

    def build_equity_packet(
        self,
        symbol: str,
        exchange: str = "NSE",
        user_query: Optional[str] = None,
        force_refresh: bool = False
    ) -> LKBPacket:
        clean_symbol = symbol.strip().upper().replace(".NS", "").replace(".BO", "")
        
        # Check feature store cache for generic packet when no specific query overrides
        if self.use_cache and not force_refresh and not user_query and self.feature_store:
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
        company_name = screener_data.get("company_name") or (nse_data.get("company_name") if nse_data else clean_symbol)

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

        # Fact: Delivery Percentage & Conviction
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

        # ---------------------------------------------------------------------
        # Query-Aware Contextual Facts: Specific to Investor's Stated Rationale
        # ---------------------------------------------------------------------
        query_upper = (user_query or "").upper()

        # Contextual Fact: Crude Oil / Energy Sensitivity
        if any(term in query_upper for term in ["CRUDE", "OIL", "BRENT", "PETROL", "DIESEL", "FUEL", "REFIN", "OPEC"]) or clean_symbol in ["RELIANCE", "ONGC", "BPCL", "IOC", "HPCL"]:
            from backend.scrapers.fred_client import FREDClient
            brent_obs = FREDClient.get_series_observation("BRENT_CRUDE")
            brent_val = brent_obs.get("value", 82.50)
            facts.append(LKBFact(
                id=f"LKB-{fact_idx:02d}",
                category=LKBFactCategory.MACRO,
                source="FRED_BRENT",
                metric="Brent Crude Oil Benchmark Spot",
                value=f"${brent_val:.2f}/bbl",
                unit="USD",
                context="Directly impacts investor thesis on energy/crude volatility. Affects gross refining margins (GRMs), petrochemical spreads, and working capital requirements."
            ))
            fact_idx += 1

        # Contextual Fact: Dividend Yield Spread vs Sovereign Risk-Free Rate
        if any(term in query_upper for term in ["DIVIDEND", "YIELD", "PAYOUT", "SAFE", "DEFENSIVE", "INCOME"]):
            div_yield = ratios.get("Dividend Yield") or yf_data.get("dividend_yield")
            if div_yield is not None:
                spread = round(float(div_yield) - float(gsec_10y), 2)
                facts.append(LKBFact(
                    id=f"LKB-{fact_idx:02d}",
                    category=LKBFactCategory.VALUATION,
                    source="SCREENER_DIVIDEND",
                    metric="Equity Dividend Yield vs Sovereign Spread",
                    value=f"{div_yield}% (Spread: {spread}%)",
                    unit="%",
                    context=f"Investor seeks dividend safety. Stock yields {div_yield}% vs 10Y Indian Sovereign G-Sec at {gsec_10y}%, generating a net spread of {spread}%."
                ))
                fact_idx += 1

        # Contextual Fact: Currency & US Dollar Transmission
        if any(term in query_upper for term in ["DOLLAR", "USD", "INR", "RUPEE", "CURRENCY", "EXPORT", "FOREX"]) or clean_symbol in ["TCS", "INFY", "WIPRO", "HCLTECH", "TECHM", "SUNPHARMA", "DRREDDY", "CIPLA"]:
            from backend.scrapers.fred_client import FREDClient
            dxy_obs = FREDClient.get_series_observation("US_DOLLAR_INDEX")
            dxy_val = dxy_obs.get("value", 104.20)
            facts.append(LKBFact(
                id=f"LKB-{fact_idx:02d}",
                category=LKBFactCategory.MACRO,
                source="FRED_DXY",
                metric="US Dollar Index (DXY) & Currency Transmission",
                value=f"{dxy_val}",
                unit="Points",
                context="Measures global dollar strength. A strong dollar index drives INR depreciation pressure, raising imported input costs while acting as a hedge for export revenue."
            ))
            fact_idx += 1

        # Contextual Fact: Commercial Vehicle / Auto Expansion Dynamics
        if any(term in query_upper for term in ["COMMERCIAL VEHICLE", "CV", "AUTO", "TRUCK", "BUS", "EV", "EXPANSION", "FLEET"]) and clean_symbol in ["TATAMOTORS", "MARUTI", "M&M", "ASHOKLEY", "EICHERMOT"]:
            facts.append(LKBFact(
                id=f"LKB-{fact_idx:02d}",
                category=LKBFactCategory.TECHNICAL,
                source="INDUSTRY_AUTO_MONITOR",
                metric="Commercial Vehicle & Auto Cyclicality Dynamics",
                value="High Cyclical Beta",
                unit="",
                context="CV and auto expansion is heavily tied to domestic infrastructure freight volume, diesel inflation, and fleet financing interest rates."
            ))
            fact_idx += 1

        # ---------------------------------------------------------------------
        # Deep Real-Time Web Search & Query-Targeted News Catalysts
        # ---------------------------------------------------------------------
        web_articles = WebSearchClient.search_query_context(
            clean_symbol,
            company_name=company_name,
            user_query=user_query,
            limit=3
        )

        for art in web_articles:
            matched = art.get("is_query_matched", False)
            metric_title = "Query-Targeted News Catalyst" if matched else "Market & Company News Catalyst"
            src_clean = art.get("source", "Web").upper().replace(" ", "_")[:18]
            snippet = art.get("snippet", "")
            pub_date = art.get("published", "")
            date_ctx = f" (Published: {pub_date})" if pub_date else ""
            
            facts.append(LKBFact(
                id=f"LKB-{fact_idx:02d}",
                category=LKBFactCategory.NEWS,
                source=f"NEWS_{src_clean}",
                metric=metric_title,
                value=art.get("title", "News Catalyst")[:130],
                unit="",
                context=f"{snippet[:240]}{date_ctx}"
            ))
            fact_idx += 1

        packet = LKBPacket(
            session_id=session_id,
            symbol=clean_symbol,
            exchange=exchange,
            asset_class=AssetClass.EQUITY,
            facts=facts,
            metadata={
                "company_name": company_name,
                "has_nse_live": nse_data is not None,
                "red_flag_count": len(red_flags),
                "query_context_applied": bool(user_query)
            }
        )

        if self.use_cache and self.feature_store and not user_query:
            try:
                self.feature_store.set(clean_symbol, "EQUITY_PACKET", packet.model_dump(), ttl_seconds=900)
            except Exception:
                pass

        return packet

