import httpx
from typing import Dict, Any, Optional
import logging
import os

logger = logging.getLogger("faida.scrapers.fred")

class FREDClient:
    """Fetches global macroeconomic indicators from the Federal Reserve Economic Data (FRED) API."""

    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

    SERIES_MAP = {
        "BRENT_CRUDE": "DCOILBRENTEU",   # Crude Oil Prices: Brent - Europe (Dollars per Barrel)
        "US_10Y_YIELD": "DGS10",         # 10-Year Treasury Constant Maturity Rate
        "US_DOLLAR_INDEX": "DTWEXBGS"    # Nominal Broad U.S. Dollar Index
    }

    # Calibrated macro baselines in case API key is absent or network is unavailable
    FALLBACK_VALUES = {
        "BRENT_CRUDE": 82.50,
        "US_10Y_YIELD": 4.25,
        "US_DOLLAR_INDEX": 104.20
    }

    @classmethod
    def get_series_observation(cls, series_key: str, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Fetches the latest observation for a macroeconomic series."""
        series_id = cls.SERIES_MAP.get(series_key)
        if not series_id:
            return {"series": series_key, "value": None, "source": "UNKNOWN"}

        key = api_key if api_key is not None else os.getenv("FRED_API_KEY", "").strip()

        if not key:
            # Safe zero-configuration fallback
            fallback_val = cls.FALLBACK_VALUES.get(series_key, 0.0)
            return {
                "series": series_key,
                "series_id": series_id,
                "value": fallback_val,
                "date": "Calibrated Baseline",
                "source": "FRED_BASELINE"
            }

        params = {
            "series_id": series_id,
            "api_key": key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": 5
        }

        try:
            with httpx.Client(timeout=9.0) as client:
                resp = client.get(cls.BASE_URL, params=params)
                if resp.status_code == 200:
                    obs_list = resp.json().get("observations", [])
                    for obs in obs_list:
                        val_str = obs.get("value", "")
                        if val_str and val_str != ".":
                            try:
                                return {
                                    "series": series_key,
                                    "series_id": series_id,
                                    "value": round(float(val_str), 2),
                                    "date": obs.get("date", ""),
                                    "source": "FRED_API"
                                }
                            except ValueError:
                                pass
        except Exception as err:
            logger.debug(f"FRED API request error for {series_key}: {err}")

        # Return calibrated baseline on error
        return {
            "series": series_key,
            "series_id": series_id,
            "value": cls.FALLBACK_VALUES.get(series_key, 0.0),
            "date": "Fallback Baseline",
            "source": "FRED_FALLBACK"
        }

    @classmethod
    def get_global_macro_snapshot(cls, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Returns consolidated snapshot of global macro risk drivers."""
        brent = cls.get_series_observation("BRENT_CRUDE", api_key)
        us10y = cls.get_series_observation("US_10Y_YIELD", api_key)
        dxy = cls.get_series_observation("US_DOLLAR_INDEX", api_key)

        return {
            "brent_crude_usd": brent.get("value"),
            "brent_date": brent.get("date"),
            "us_10y_yield_pct": us10y.get("value"),
            "us_dollar_index": dxy.get("value"),
            "is_live_api": any(
                item.get("source") == "FRED_API" for item in [brent, us10y, dxy]
            )
        }
