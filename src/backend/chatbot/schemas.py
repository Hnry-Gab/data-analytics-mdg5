"""Pydantic V2 schemas for the chat endpoint."""
from pydantic import BaseModel, Field
from typing import Literal, Any


class ChatRequest(BaseModel):
    """Incoming chat message from the frontend."""
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str = Field(..., min_length=1, max_length=64)


class SSEEvent(BaseModel):
    """Server-Sent Event payload."""
    event: Literal["text_delta", "tool_call", "tool_result", "error", "done"]
    data: dict[str, Any] = Field(default_factory=dict)


class ChatMessage(BaseModel):
    """Single message in conversation history (OpenAI chat format)."""
    role: Literal["system", "user", "assistant", "tool"]
    content: str | None = None
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None
    name: str | None = None
