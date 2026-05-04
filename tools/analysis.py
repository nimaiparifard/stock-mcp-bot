import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def analyze_stock(price_data):
    ticker = price_data["ticker"]
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="3mo")

        if hist.empty:
            return {"trend": "unknown", "error": "No historical data"}

        # Calculate moving averages
        hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
        hist['SMA_50'] = hist['Close'].rolling(window=50).mean()

        # RSI calculation
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        hist['RSI'] = 100 - (100 / (1 + rs))

        latest = hist.iloc[-1]
        prev = hist.iloc[-2] if len(hist) > 1 else latest

        # Trend analysis
        if latest['Close'] > latest['SMA_20'] and latest['SMA_20'] > latest['SMA_50']:
            trend = "bullish"
        elif latest['Close'] < latest['SMA_20'] and latest['SMA_20'] < latest['SMA_50']:
            trend = "bearish"
        else:
            trend = "sideways"

        # RSI interpretation
        rsi = latest['RSI']
        if rsi > 70:
            rsi_signal = "overbought"
        elif rsi < 30:
            rsi_signal = "oversold"
        else:
            rsi_signal = "neutral"

        # Volatility
        volatility = hist['Close'].pct_change().std() * (252 ** 0.5)  # Annualized

        return {
            "trend": trend,
            "rsi": round(rsi, 2) if not pd.isna(rsi) else None,
            "rsi_signal": rsi_signal,
            "volatility": round(volatility, 4) if not pd.isna(volatility) else None,
            "sma_20": round(latest['SMA_20'], 2) if not pd.isna(latest['SMA_20']) else None,
            "sma_50": round(latest['SMA_50'], 2) if not pd.isna(latest['SMA_50']) else None,
            "recommendation": get_recommendation(trend, rsi_signal, price_data)
        }
    except Exception as e:
        return {"trend": "unknown", "error": str(e)}

def get_recommendation(trend, rsi_signal, price_data):
    if price_data.get("error"):
        return "Unable to analyze due to data error"

    if trend == "bullish" and rsi_signal != "overbought":
        return "Consider buying - strong upward trend"
    elif trend == "bearish" and rsi_signal != "oversold":
        return "Consider selling or avoiding - downward trend"
    elif rsi_signal == "oversold":
        return "Potential buying opportunity - oversold conditions"
    elif rsi_signal == "overbought":
        return "Consider taking profits - overbought conditions"
    else:
        return "Hold or monitor - mixed signals"