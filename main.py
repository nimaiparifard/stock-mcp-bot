from fastapi import FastAPI, HTTPException
from models.schemas import ChatRequest, ChatResponse
from mcp.intent import detect_intent
from mcp.context import get_context, update_context, add_to_history
from mcp.orchestrator import run_tools
from mcp.reasoning import generate_response
import logging
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Stock MCP Bot", version="2.0.0")

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        logger.info(f"Processing chat for user {req.user_id}: {req.message}")

        # 1. Intent detection
        intent_data = detect_intent(req.message)
        logger.info(f"Detected intent: {intent_data}")

        # 2. Load context
        context = get_context(req.user_id)

        # 3. Run tools
        tool_data = run_tools(intent_data)
        logger.info(f"Tool data: {tool_data}")

        # 4. Generate response
        response_text = generate_response(intent_data, tool_data, context)

        # 5. Update context
        if intent_data.get("ticker"):
            update_context(req.user_id, "last_stock", intent_data["ticker"])

        # 6. Add to history
        add_to_history(req.user_id, req.message, response_text)

        return ChatResponse(response=response_text)

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/context/{user_id}")
def get_user_context(user_id: str):
    context = get_context(user_id)
    return context


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)