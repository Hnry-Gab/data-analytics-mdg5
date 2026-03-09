"""Chatbot API routes — POST /api/chat (SSE) + GET /api/chat/status."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.chatbot.config import CHATBOT_ENABLED, OPENROUTER_API_KEY
from backend.chatbot.mcp_client import mcp_client
from backend.chatbot.orchestrator import handle_chat_message
from backend.chatbot.schemas import ChatRequest

router = APIRouter(prefix="/api", tags=["Chatbot"])


@router.post("/chat")
async def chat(request: ChatRequest):
    """Stream a chat response as Server-Sent Events."""
    if not CHATBOT_ENABLED:
        raise HTTPException(status_code=503, detail="Chatbot desabilitado.")
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=503, detail="OPENROUTER_API_KEY não configurada.")

    return StreamingResponse(
        handle_chat_message(request.message, request.session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/chat/status")
async def chat_status():
    """Chatbot health check."""
    return {
        "enabled": CHATBOT_ENABLED,
        "llm_configured": bool(OPENROUTER_API_KEY),
        "mcp_connected": mcp_client.connected,
        "tools_available": len(mcp_client.tools),
    }
