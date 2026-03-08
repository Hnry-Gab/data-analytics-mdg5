"""OpenRouter async streaming client — OpenAI-compatible chat completions."""
from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator

import httpx

from src.chatbot.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_MAX_TOKENS,
    OPENROUTER_MODEL,
    OPENROUTER_TEMPERATURE,
)

logger = logging.getLogger(__name__)

_http_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    """Lazy-init httpx client with connection pooling."""
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            base_url=OPENROUTER_BASE_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://olist-logistics.app",
                "X-Title": "Olist Logistics Analytics",
            },
            timeout=httpx.Timeout(connect=10, read=300, write=120, pool=10),
        )
    return _http_client


async def stream_chat_completion(
    messages: list[dict],
    tools: list[dict] | None = None,
) -> AsyncIterator[dict]:
    """Stream chat completion from OpenRouter (OpenAI-compatible SSE).

    Yields parsed JSON chunks from the SSE stream:
    - ``{"choices": [{"delta": {"content": "..."}}]}``         — text token
    - ``{"choices": [{"delta": {"tool_calls": [...]}}]}``      — partial tool call
    - ``{"choices": [{"finish_reason": "stop"|"tool_calls"}]}`` — end signal
    """
    payload: dict = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "max_tokens": OPENROUTER_MAX_TOKENS,
        "temperature": OPENROUTER_TEMPERATURE,
        "stream": True,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    client = _get_client()
    async with client.stream("POST", "/chat/completions", json=payload) as response:
        response.raise_for_status()
        async for line in response.aiter_lines():
            if not line.startswith("data: "):
                continue
            data = line[6:]  # strip "data: " prefix
            if data == "[DONE]":
                return
            try:
                yield json.loads(data)
            except json.JSONDecodeError:
                logger.warning("Skipping malformed SSE chunk: %s", data[:120])


async def close_client() -> None:
    """Close the httpx client (called on FastAPI shutdown)."""
    global _http_client
    if _http_client is not None and not _http_client.is_closed:
        await _http_client.aclose()
        _http_client = None
