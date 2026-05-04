import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")


def _get_openai_client():
    # Build client lazily so dependency mismatches do not crash imports.
    try:
        return OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
    except Exception:
        return None

def generate_response(intent_data, tool_data, context):
    intent = intent_data["intent"]
    ticker = intent_data.get("ticker")

    if "error" in tool_data:
        return f"Sorry, I encountered an error: {tool_data['error']}"

    # Prepare context for LLM
    context_str = f"User context: {context}"
    tool_str = str(tool_data)

    prompt = f"""
    You are a helpful stock trading assistant. Generate a natural, informative response based on the following:

    Intent: {intent}
    Ticker: {ticker}
    Tool Data: {tool_str}
    User Context: {context_str}

    Provide a concise, professional response suitable for a chat interface.
    """

    client = _get_openai_client()
    if client:
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a knowledgeable stock market assistant. Provide accurate, helpful information about stocks."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception:
            pass

    # Fallback to template responses
    return generate_fallback_response(intent_data, tool_data)

def generate_fallback_response(intent_data, tool_data):
    intent = intent_data["intent"]
    ticker = intent_data.get("ticker", "Unknown")

    if intent == "stock_price":
        price_data = tool_data.get("price_data", {})
        if "error" in price_data:
            return f"Sorry, couldn't fetch price for {ticker}: {price_data['error']}"
        price = price_data.get("price", "N/A")
        change = price_data.get("change", "N/A")
        return f"{ticker} is currently trading at ${price} (change: ${change})"

    elif intent in ["recommendation", "analysis"]:
        analysis = tool_data.get("analysis", {})
        trend = analysis.get("trend", "unknown")
        recommendation = analysis.get("recommendation", "Monitor closely")
        return f"Analysis for {ticker}: Trend is {trend}. {recommendation}"

    elif intent == "news":
        return f"News feature for {ticker} is coming soon!"

    elif intent == "portfolio":
        return "Portfolio management features are under development."

    return "I can help with stock prices, analysis, and recommendations. What would you like to know?"