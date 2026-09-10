import yfinance as yf
from typing import Dict, Any, Optional
import math

class YFinanceClient:
    """Extracts price history, moving averages, RSI, and valuation from Yahoo Finance for Indian tickers."""

    @staticmethod
    def _format_ticker(symbol: str, exchange: str = "NSE") -> str:
        symbol = symbol.strip().upper()
        if symbol.endswith(".NS") or symbol.endswith(".BO"):
            return symbol
        suffix = ".BO" if exchange.upper() == "BSE" else ".NS"
        return f"{symbol}{suffix}"

    @classmethod
    def get_market_summary(cls, symbol: str, exchange: str = "NSE") -> Dict[str, Any]:
        ticker_str = cls._format_ticker(symbol, exchange)
        ticker = yf.Ticker(ticker_str)

        try:
            # 1. Basic Info
            info = ticker.info or {}
            current_price = info.get("currentPrice") or info.get("regularMarketPrice") or 0.0
            prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose") or current_price
            day_change = current_price - prev_close if current_price and prev_close else 0.0
            day_change_pct = (day_change / prev_close * 100.0) if prev_close else 0.0

            # 2. Historical data for technical indicators (6 months)
            hist = ticker.history(period="6mo")
            ema_20, ema_50, ema_200, rsi_14 = None, None, None, None

            if not hist.empty and len(hist) >= 14:
                closes = hist["Close"]
                # 20 EMA & 50 EMA
                if len(closes) >= 20:
                    ema_20 = round(float(closes.ewm(span=20, adjust=False).mean().iloc[-1]), 2)
                if len(closes) >= 50:
                    ema_50 = round(float(closes.ewm(span=50, adjust=False).mean().iloc[-1]), 2)
                if len(closes) >= 200:
                    ema_200 = round(float(closes.ewm(span=200, adjust=False).mean().iloc[-1]), 2)

                # RSI 14
                delta = closes.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi_series = 100 - (100 / (1 + rs))
                if not math.isnan(rsi_series.iloc[-1]):
                    rsi_14 = round(float(rsi_series.iloc[-1]), 2)

            return {
                "symbol": symbol.upper(),
                "formatted_ticker": ticker_str,
                "current_price": round(float(current_price), 2),
                "previous_close": round(float(prev_close), 2),
                "day_change": round(float(day_change), 2),
                "day_change_pct": round(float(day_change_pct), 2),
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
                "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
                "market_cap": info.get("marketCap"),
                "trailing_pe": round(float(info["trailingPE"]), 2) if info.get("trailingPE") else None,
                "forward_pe": round(float(info["forwardPE"]), 2) if info.get("forwardPE") else None,
                "price_to_book": round(float(info["priceToBook"]), 2) if info.get("priceToBook") else None,
                "beta": round(float(info["beta"]), 2) if info.get("beta") else None,
                "dividend_yield": round(float(info["dividendYield"] * 100), 2) if info.get("dividendYield") else None,
                "ema_20": ema_20,
                "ema_50": ema_50,
                "ema_200": ema_200,
                "rsi_14": rsi_14,
                "volume": info.get("regularMarketVolume") or (int(hist["Volume"].iloc[-1]) if not hist.empty else 0),
                "source": "YFINANCE"
            }
        except Exception as err:
            return {
                "symbol": symbol.upper(),
                "formatted_ticker": ticker_str,
                "error": str(err),
                "current_price": 0.0,
                "source": "YFINANCE"
            }
