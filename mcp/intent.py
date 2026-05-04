import re
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
TICKER_STOP_WORDS = {
    "WHAT", "WHATS", "PRICE", "CURRENT", "STOCK", "SHOULD", "BUY",
    "SELL", "TODAY", "PLEASE", "ABOUT", "NEWS", "ANALYSIS", "ANALYZE",
    "THE", "FOR", "AND", "YOU", "CAN", "GIVE", "ME", "WITH", "LONG",
    "TERM", "INVEST", "INVESTING", "NOW", "IS", "OF"
}


def _get_openai_client():
    # Build the client lazily to avoid crashing at import time
    # when local dependency versions are incompatible.
    try:
        return OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
    except Exception:
        return None

def detect_intent(message: str):
    prompt = f"""
    Analyze the following user message and determine the intent related to stock trading.
    Possible intents: stock_price, recommendation, general, news, analysis, portfolio

    Also extract the stock ticker if mentioned (e.g., AAPL, GOOGL).

    Message: "{message}"

    Respond in JSON format:
    {{
        "intent": "intent_here",
        "ticker": "TICKER" or null,
        "confidence": 0.0-1.0
    }}
    """

    client = _get_openai_client()
    if client:
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.1
            )
            result = response.choices[0].message.content.strip()
            # Parse JSON
            import json
            data = json.loads(result)
            return data
        except Exception:
            pass

    # Fallback to simple detection
    message_lower = message.lower()
    if "price" in message_lower:
        intent = "stock_price"
    elif "buy" in message_lower or "invest" in message_lower:
        intent = "recommendation"
    elif "news" in message_lower:
        intent = "news"
    elif "analysis" in message_lower or "analyze" in message_lower:
        intent = "analysis"
    else:
        intent = "general"

    ticker_candidates = re.findall(r"\b[A-Z]{1,5}\b", message.upper())
    ticker_candidates = [t for t in ticker_candidates if t not in TICKER_STOP_WORDS]
    # Prefer the last valid token so "price of AAPL" picks AAPL, not earlier words.
    ticker = ticker_candidates[-1] if ticker_candidates else None

    return {
        "intent": intent,
        "ticker": ticker,
        "confidence": 0.5
    }