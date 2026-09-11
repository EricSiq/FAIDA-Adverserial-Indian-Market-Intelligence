"""
FAIDA: Financial Adversarial Indian Data Agents
Module: backend.agents.simulator_agent
Description:
    Adversarial Stress-Testing Engine that runs deterministic "What-If" macroeconomic
    and sectoral shock simulations against an Indian investment thesis.
    
    Supported Stress Scenarios:
        1. CRUDE_SURGE: Brent crude spikes to $95-$100/bbl (Current Account Deficit, raw material margin squeeze).
        2. RBI_RATE_HIKE: Unexpected 25 bps repo rate hike (NIM compression, equity multiple rerating, demand delay).
        3. INR_DEPRECIATION: USD/INR weakens past ₹86.50 (imported inflation vs IT/pharma export tailwinds).
        4. MARGIN_COMPRESSION: 250 bps operating margin drop (operating deleverage and forward P/E expansion).
"""

from typing import Dict, Any
from pydantic import BaseModel

class ScenarioResult(BaseModel):
    """Result of a deterministic macroeconomic stress-test simulation."""
    scenario_id: str
    scenario_title: str
    symbol: str
    estimated_impact: str  # e.g. "HIGH NEGATIVE (-7% to -12% Operating Profit)"
    mechanism: str
    red_team_warning: str
    hedging_takeaway: str

class SimulatorAgent:
    """
    Stress-tests investment positions against external shocks using sector-calibrated
    elasticity models tailored to the Indian macroeconomic environment.
    """

    SECTOR_MAPPINGS = {
        "RELIANCE": {"sector": "ENERGY_DIVERSIFIED", "crude_sensitivity": "MIXED", "fx_sensitivity": "POSITIVE_USD"},
        "TATAMOTORS": {"sector": "AUTO", "crude_sensitivity": "NEGATIVE", "fx_sensitivity": "POSITIVE_GBP_EUR"},
        "MARUTI": {"sector": "AUTO", "crude_sensitivity": "NEGATIVE", "fx_sensitivity": "NEGATIVE_JPY"},
        "ASIANPAINT": {"sector": "PAINTS_CHEMICALS", "crude_sensitivity": "SEVERELY_NEGATIVE", "fx_sensitivity": "NEGATIVE_USD"},
        "INFY": {"sector": "IT_EXPORTS", "crude_sensitivity": "NEUTRAL", "fx_sensitivity": "HIGHLY_POSITIVE_USD"},
        "TCS": {"sector": "IT_EXPORTS", "crude_sensitivity": "NEUTRAL", "fx_sensitivity": "HIGHLY_POSITIVE_USD"},
        "HDFCBANK": {"sector": "BANKING", "crude_sensitivity": "INDIRECT_NEGATIVE", "fx_sensitivity": "NEUTRAL"},
        "ICICIBANK": {"sector": "BANKING", "crude_sensitivity": "INDIRECT_NEGATIVE", "fx_sensitivity": "NEUTRAL"},
        "SBIN": {"sector": "BANKING", "crude_sensitivity": "INDIRECT_NEGATIVE", "fx_sensitivity": "NEUTRAL"},
        "ITC": {"sector": "FMCG", "crude_sensitivity": "MILD_NEGATIVE", "fx_sensitivity": "NEUTRAL"},
        "BHARTIARTL": {"sector": "TELECOM", "crude_sensitivity": "MILD_NEGATIVE", "fx_sensitivity": "NEGATIVE_USD_DEBT"}
    }

    @classmethod
    def simulate(cls, symbol: str, scenario_type: str) -> ScenarioResult:
        if not symbol or not isinstance(symbol, str):
            sym = "BENCHMARK"
        else:
            sym = symbol.strip().upper().replace(".NS", "").replace(".BO", "")
        sec_info = cls.SECTOR_MAPPINGS.get(sym, {"sector": "GENERAL_EQUITY", "crude_sensitivity": "NEGATIVE", "fx_sensitivity": "NEUTRAL"})


        if scenario_type == "CRUDE_SURGE":
            title = "Macro Shock: Brent Crude spikes to $95 - $100/bbl"
            if sec_info["sector"] in ["PAINTS_CHEMICALS", "AUTO"]:
                impact = "HIGH NEGATIVE (-7% to -12% Operating Profit)"
                mech = "Crude oil derivatives represent 30–50% of raw material input costs (monomers, solvents, titanium dioxide). Price increases cannot be passed immediately without demand destruction."
                warning = f"Gross margins for {sym} will compress rapidly over the next 2 quarters as working capital requirements escalate."
                hedge = "Check whether management holds pricing power, or consider defensive allocation into upstream energy or gold."
            elif sec_info["sector"] == "ENERGY_DIVERSIFIED":
                impact = "MODERATE / MIXED (+4% Upstream, -5% Petrochemicals)"
                mech = "While upstream exploration realizations increase, downstream refining and petrochemical margins suffer from elevated feedstock costs and potential windfall tax liabilities."
                warning = "High crude frequently invites government intervention via windfall excise duties or suppressed marketing margins on retail fuels."
                hedge = "Monitor Gross Refining Margins (GRMs) and windfall tax announcements from the Ministry of Petroleum."
            else:
                impact = "MODERATE NEGATIVE (-3% to -5% Market Drag)"
                mech = "Higher imported crude widens India's Current Account Deficit (CAD), puts pressure on the Rupee, and stokes imported inflation."
                warning = "Broad market multiple contraction as cost of domestic capital tightens."
                hedge = "Hold strict invalidation stop-losses."

        elif scenario_type == "RBI_RATE_HIKE":
            title = "Monetary Shock: RBI MPC unexpectedly hikes repo rate by 25 bps"
            if sec_info["sector"] in ["BANKING", "NBFC"]:
                impact = "MODERATE ASYMMETRIC (Short-term NIM squeeze, Net Margin pressure)"
                mech = "Cost of deposits reprices faster than fixed-rate asset yields, temporarily narrowing Net Interest Margins (NIMs)."
                warning = f"High credit growth could face moderation as retail borrower affordability drops; risk of rising credit costs in unsecured lending."
                hedge = "Favor banks with high CASA ratios (>40%) which remain insulated from deposit cost inflation."
            elif sec_info["sector"] in ["AUTO", "REALTY"]:
                impact = "HIGH NEGATIVE (-5% to -8% Demand Invalidation)"
                mech = "Automotive and housing loans face EMI spikes, directly dampening discretionary high-ticket retail purchases."
                warning = "Cyclical peak volumes will suffer cancellations and inventory buildup at dealership levels."
                hedge = "Avoid buying at cyclical peak valuations when policy rates are restrictive."
            else:
                impact = "MODERATE NEGATIVE (-4% Equity Multiple Compression)"
                mech = "Risk-free 10Y G-Sec yield rises above 7.25%, making equity earnings yield relatively less attractive."
                warning = "Institutional funds typically rebalance away from high-P/E growth stocks into fixed-income securities."
                hedge = "Ensure equity earnings yield (1 / PE) exceeds sovereign yield by at least 150 bps."

        elif scenario_type == "INR_DEPRECIATION":
            title = "Forex Shock: USD/INR weakens sharply past ₹86.50"
            if sec_info["sector"] == "IT_EXPORTS":
                impact = "FAVORABLE TAILWIND (+30 to +50 bps Operating Margin per 1% drop)"
                mech = "Revenues are billed predominantly in USD/EUR while employee costs and overheads are incurred in Indian Rupees."
                warning = f"While optical margins expand, global client IT discretionary spending delays remain a counter-weight."
                hedge = "Evaluate whether revenue growth is volume-driven or purely FX-cushioned."
            else:
                impact = "MODERATE NEGATIVE (Imported Inflation & Raw Material Escalation)"
                mech = "Higher landed costs for imported capital goods, semiconductors, and energy feedstocks."
                warning = "Foreign Institutional Investors (FIIs) tend to withdraw capital during sharp currency slides to protect USD returns."
                hedge = "Monitor daily FII cash market trends."

        else:
            title = "Earnings Shock: Quarterly Operating Margins compress by 250 bps"
            impact = "HIGH NEGATIVE (-8% to -15% Valuation Rerating)"
            mech = "Operating deleverage amplifies small revenue slowdowns into substantial net profit contractions."
            warning = f"Valuation multiples for {sym} will compress if the street downgrades FY27 EPS estimates."
            hedge = "Set an automated stop-loss at 95% of current price."

        return ScenarioResult(
            scenario_id=scenario_type,
            scenario_title=title,
            symbol=sym,
            estimated_impact=impact,
            mechanism=mech,
            red_team_warning=warning,
            hedging_takeaway=hedge
        )
