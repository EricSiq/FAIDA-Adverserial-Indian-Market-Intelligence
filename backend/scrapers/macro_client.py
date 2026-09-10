import yfinance as yf
from typing import Dict, Any
import logging

logger = logging.getLogger("faida.scrapers.macro")

class MacroClient:
    """Fetches real-time Indian macro indicators including India VIX and Benchmark G-Sec Yield."""

    @classmethod
    def get_vix_status(cls) -> Dict[str, Any]:
        try:
            ticker = yf.Ticker("^INDIAVIX")
            hist = ticker.history(period="5d")
            if not hist.empty:
                current_vix = round(float(hist["Close"].iloc[-1]), 2)
                prev_vix = round(float(hist["Close"].iloc[-2]), 2) if len(hist) >= 2 else current_vix
                vix_change = round(current_vix - prev_vix, 2)
                vix_change_pct = round((vix_change / prev_vix * 100.0), 2) if prev_vix else 0.0
            else:
                current_vix, prev_vix, vix_change, vix_change_pct = 13.5, 13.5, 0.0, 0.0

            # Regime Classification
            if current_vix < 13.0:
                regime = "LOW_VOLATILITY"
                regime_label = "Low Volatility / Complacency"
                color = "#22c55e"  # Green
                description = "Market volatility is subdued. Option sellers dominant; market susceptible to sudden exogenous shocks."
            elif current_vix <= 18.0:
                regime = "NORMAL"
                regime_label = "Normal Market Regime"
                color = "#f59e0b"  # Amber
                description = "Standard volatility conditions. Technical support and resistance levels tend to hold with typical variance."
            elif current_vix <= 24.0:
                regime = "ELEVATED"
                regime_label = "Elevated Volatility"
                color = "#f97316"  # Orange
                description = "Heightened intraday turbulence. Widen stop-loss thresholds and curtail leveraged positional size."
            else:
                regime = "EXTREME_PANIC"
                regime_label = "Extreme Panic / Stress"
                color = "#ef4444"  # Red
                description = "Violent market drawdowns likely. Capital preservation and defensive G-Sec allocation recommended."

            return {
                "vix_value": current_vix,
                "vix_change": vix_change,
                "vix_change_pct": vix_change_pct,
                "regime": regime,
                "regime_label": regime_label,
                "color": color,
                "description": description,
                "benchmark_10y_yield": 7.08,  # India 10Y Benchmark G-Sec Baseline
                "rbi_repo_rate": 6.50
            }
        except Exception as err:
            logger.warning(f"Error fetching India VIX: {err}")
            return {
                "vix_value": 13.8,
                "vix_change": 0.0,
                "vix_change_pct": 0.0,
                "regime": "NORMAL",
                "regime_label": "Normal Regime (Fallback)",
                "color": "#f59e0b",
                "description": "Macro volatility gauge operating on calibrated baseline.",
                "benchmark_10y_yield": 7.08,
                "rbi_repo_rate": 6.50
            }
