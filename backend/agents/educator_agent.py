"""
FAIDA: Financial Adversarial Indian Data Agents
Module: backend.agents.educator_agent
Description:
    Synthesis & Pre-Mortem Audit Engine.
    
    Responsibilities:
        1. Calculates the deterministic Adversarial Friction Score (AFS) on a scale of 10 to 95.
           Incorporates RSI overbought/oversold limits, P/E multiple expansion, promoter pledging,
           delivery volume turnover conviction, and cognitive bias severity penalties.
        2. Synthesizes a structured PreMortemReport containing:
           - Grounded headline risk verdicts
           - Categorized risk items with direct LKB citation pointers
           - Bullish/Bearish psychological traps
           - Structural blind spots and corporate governance alarms
           - Concrete invalidation stops and profit targets
           - Pedagogical market microstructure takeaways for Indian retail investors
"""

from typing import Dict, Any, List
from backend.lkb.models import (
    UserThesis,
    LKBPacket,
    PreMortemReport,
    PreMortemRiskItem,
    InvestmentAction,
    ToneLevel
)

class EducatorAgent:
    """
    Synthesizes the adversarial debate and grounded LKB facts into an objective pre-mortem audit.
    Calculates the deterministic Adversarial Friction Score (AFS) to visually convey downside probability.
    """

    @classmethod
    def synthesize(cls, thesis: UserThesis, lkb: LKBPacket, counter_thesis_text: str, biases: List[Any] = None) -> PreMortemReport:
        # 1. Deterministic Calculation of Adversarial Friction Score (AFS: 0 - 100)
        score = 50  # baseline neutral risk
        bias_items = biases or []

        price = 0.0
        rsi = 50.0
        pe = 20.0
        deliv = 35.0
        pledge = 0.0

        for f in lkb.facts:
            if "Current Market Price" in f.metric and isinstance(f.value, (int, float)):
                price = float(f.value)
            elif "RSI" in f.metric and isinstance(f.value, (int, float)):
                rsi = float(f.value)
            elif "Price to Earnings" in f.metric and isinstance(f.value, (int, float)):
                pe = float(f.value)
            elif "Delivery" in f.metric and isinstance(f.value, (int, float)):
                deliv = float(f.value)
            elif "Promoter Pledged" in f.metric and isinstance(f.value, (int, float)):
                pledge = float(f.value)

        # Apply friction modifiers based on user intent
        if thesis.action == InvestmentAction.BUY:
            if rsi > 70: score += 20  # Overbought buying risk
            elif rsi < 35: score -= 10  # Oversold dip opportunity
            if pe > 35: score += 15   # Valuation stretch
            if pledge > 5: score += 20  # Severe pledge risk
            if deliv < 25: score += 10 # Low conviction volume
        elif thesis.action == InvestmentAction.SELL:
            if rsi < 30: score += 25  # Selling at panic bottom
            elif rsi > 65: score -= 15 # Prudent profit booking
            if pledge == 0: score += 5 # Selling a clean governance company

        # Apply friction modifiers from detected cognitive biases
        for b in bias_items:
            severity = getattr(b, "severity", "MEDIUM")
            if severity == "HIGH":
                score += 10
            elif severity == "MEDIUM":
                score += 5

        # Clamp between 10 and 95
        friction_score = max(10, min(95, int(score)))

        # 2. Headline Verdict
        if friction_score >= 70:
            headline = f"HIGH ASYMMETRIC RISK: Strong headwinds detected against {thesis.action.value}ing {thesis.symbol}."
        elif friction_score >= 45:
            headline = f"MODERATE FRICTION: Mixed signals. Proceed with structured invalidation stops."
        else:
            headline = f"FAVORABLE RISK/REWARD: Market technicals currently align reasonably with your thesis."

        # 3. Extract Citations & Risks
        citations = [f.id for f in lkb.facts[:6]]

        bearish_risks = [
            PreMortemRiskItem(
                risk_title="Momentum & Liquidity Conviction",
                severity="HIGH" if deliv < 25 else "MEDIUM",
                argument=f"Delivery percentage is at {deliv}%, highlighting speculative intraday activity.",
                lkb_citations=[f.id for f in lkb.facts if "Delivery" in f.metric]
            ),
            PreMortemRiskItem(
                risk_title="Valuation Multiple Discipline",
                severity="HIGH" if pe > 30 else "LOW",
                argument=f"Trading at trailing P/E of {pe}x relative to broader Indian equity benchmark risk-free yield.",
                lkb_citations=[f.id for f in lkb.facts if "P/E" in f.metric]
            )
        ]

        # Dynamically inject query-targeted contextual risks directly addressing user premise
        for f in lkb.facts:
            if "Query-Targeted" in f.metric or "Brent Crude" in f.metric or "Dividend Yield" in f.metric or "Auto Cyclicality" in f.metric:
                bearish_risks.insert(
                    0,
                    PreMortemRiskItem(
                        risk_title=f"Core Thesis Headwind ({f.metric})",
                        severity="HIGH" if thesis.action == InvestmentAction.BUY else "MEDIUM",
                        argument=f"{f.value} - {f.context}",
                        lkb_citations=[f.id]
                    )
                )
                break

        # 4. Educational Takeaways for retail investors
        educational_takeaways = [
            "Delivery Volume %: Unlike US markets, Indian exchanges publish delivery statistics daily. Always check if big players are taking shares home or just churning intraday.",
            "Promoter Pledging: Promoters borrowing against shares can cause sudden margin liquidation spirals if the market drops.",
            "Risk-Free Baseline: In India, 10-Year G-Secs yield ~7.1%. If your equity dividend yield plus earnings yield does not comfortably exceed this, capital may be misallocated."
        ]

        return PreMortemReport(
            symbol=thesis.symbol,
            action_analyzed=thesis.action,
            friction_score=friction_score,
            headline_verdict=headline,
            tone_level_used=thesis.tone_level,
            bearish_risks=bearish_risks,
            bullish_traps=[
                f"Anchoring bias: Assuming {thesis.symbol} must bounce just because it corrected from 52-week highs.",
                "Ignoring sector macro rotation away from cyclicals."
            ],
            blind_spots=[
                "Contingent liabilities or tax disputes unreflected in headline quarterly earnings.",
                "Upcoming monetary policy committee (RBI MPC) rate trajectory."
            ],
            invalidation_levels={
                "invalidation_price": round(price * 0.95, 2) if price else None,
                "take_profit_target": thesis.target_price or (round(price * 1.08, 2) if price else None)
            },
            educational_takeaways=educational_takeaways,
            detected_biases=[b.model_dump() if hasattr(b, 'model_dump') else b for b in bias_items],
            lkb_packet=lkb
        )
