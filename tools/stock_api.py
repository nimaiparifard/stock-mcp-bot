import yfinance as yf
from datetime import datetime, timedelta
import json
from urllib.request import urlopen
from urllib.error import URLError, HTTPError


def _get_stooq_fallback_price(ticker: str):
    # Stooq offers a simple CSV endpoint without API keys.
    # Most US tickers are available as "<ticker>.us".
    symbol = f"{ticker.lower()}.us"
    url = f"https://stooq.com/q/l/?s={symbol}&f=sd2t2ohlcv&h&e=csv"

    try:
        with urlopen(url, timeout=8) as response:
            body = response.read().decode("utf-8", errors="ignore")
    except (URLError, HTTPError, TimeoutError):
        return None

    lines = [line.strip() for line in body.splitlines() if line.strip()]
    if len(lines) < 2:
        return None

    # Expected row: Symbol,Date,Time,Open,High,Low,Close,Volume
    # Example: AAPL.US,2026-05-03,22:00:07,183.10,184.00,182.54,183.27,12345678
    parts = lines[1].split(",")
    if len(parts) < 8:
        return None

    close_val = parts[6]
    open_val = parts[3]
    volume_val = parts[7]

    if close_val in ("", "N/D", "0"):
        return None

    try:
        price = float(close_val)
    except ValueError:
        return None

    try:
        open_price = float(open_val) if open_val not in ("", "N/D") else price
    except ValueError:
        open_price = price

    try:
        volume = int(float(volume_val)) if volume_val not in ("", "N/D") else None
    except ValueError:
        volume = None

    return {
        "ticker": ticker.upper(),
        "price": round(price, 2),
        "change": round(price - open_price, 2),
        "volume": volume,
        "market_cap": None,
        "pe_ratio": None,
        "52_week_high": None,
        "52_week_low": None,
        "source": "stooq_fallback"
    }

def get_stock_price(ticker: str):
    try:
        ticker = ticker.upper()
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="1d")

        if hist.empty:
            fallback = _get_stooq_fallback_price(ticker)
            if fallback:
                return fallback
            return {
                "ticker": ticker,
                "price": None,
                "change": None,
                "error": "Stock not found"
            }

        current_price = hist['Close'].iloc[-1]
        previous_close = hist['Open'].iloc[0] if len(hist) > 1 else current_price
        change = current_price - previous_close

        return {
            "ticker": ticker,
            "price": round(current_price, 2),
            "change": round(change, 2),
            "volume": int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else None,
            "market_cap": info.get('marketCap'),
            "pe_ratio": info.get('trailingPE'),
            "52_week_high": info.get('fiftyTwoWeekHigh'),
            "52_week_low": info.get('fiftyTwoWeekLow'),
            "source": "yfinance"
        }
    except Exception as e:
        # If Yahoo is rate-limited/down, try an alternate public source.
        fallback = _get_stooq_fallback_price(ticker.upper())
        if fallback:
            fallback["warning"] = f"Primary source failed: {str(e)}"
            return fallback
        return {
            "ticker": ticker,
            "price": None,
            "change": None,
            "error": str(e)
        }

def get_stock_history(ticker: str, period="1mo"):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        return hist.to_dict('records')
    except Exception as e:
        return {"error": str(e)}