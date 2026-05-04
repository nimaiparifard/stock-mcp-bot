from collections import defaultdict
import time

user_context = defaultdict(dict)

def get_context(user_id: str):
    if user_id not in user_context:
        user_context[user_id] = {
            "risk": "moderate",
            "last_stock": None,
            "conversation_history": [],
            "preferences": {}
        }
    return user_context[user_id]

def update_context(user_id: str, key: str, value):
    user_context[user_id][key] = value

def add_to_history(user_id: str, message: str, response: str):
    history = user_context[user_id].get("conversation_history", [])
    history.append({
        "timestamp": time.time(),
        "user_message": message,
        "bot_response": response
    })
    # Keep only last 10 messages
    user_context[user_id]["conversation_history"] = history[-10:]

def get_conversation_history(user_id: str, limit=5):
    history = user_context[user_id].get("conversation_history", [])
    return history[-limit:]