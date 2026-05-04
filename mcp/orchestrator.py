from tools.stock_api import get_stock_price, get_stock_history
from tools.analysis import analyze_stock

def run_tools(intent_data):
    ticker = intent_data.get("ticker")
    intent = intent_data["intent"]

    result = {}

    if not ticker:
        return {"error": "No ticker specified"}

    try:
        if intent == "stock_price":
            result["price_data"] = get_stock_price(ticker)

        elif intent in ["recommendation", "analysis"]:
            price_data = get_stock_price(ticker)
            analysis = analyze_stock(price_data)
            history = get_stock_history(ticker, "1mo")

            result["price_data"] = price_data
            result["analysis"] = analysis
            result["history"] = history

        elif intent == "news":
            # Placeholder for news - would need news API
            result["news"] = f"Latest news for {ticker} would be fetched here"

        elif intent == "portfolio":
            # Placeholder for portfolio management
            result["portfolio"] = "Portfolio features not implemented yet"

        else:
            result["general"] = "General stock information"

        return result
    except Exception as e:
        return {"error": str(e)}