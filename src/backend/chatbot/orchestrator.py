"""Orchestrator — agentic loop that wires LLM, MCP tools, and session history."""
from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator

from backend.chatbot.config import MAX_CONSECUTIVE_TOOL_ERRORS, MAX_TOOL_ITERATIONS, OPENROUTER_API_KEY
from backend.chatbot.mcp_client import mcp_client
from backend.chatbot.openrouter_client import stream_chat_completion
from backend.chatbot.session_manager import session_manager
from backend.chatbot.system_prompt import SYSTEM_PROMPT
from backend.chatbot.tool_converter import mcp_tools_to_openai_functions

logger = logging.getLogger(__name__)


def _make_sse(event: str, data: dict | None = None) -> str:
    """Format a Server-Sent Event line."""
    payload = json.dumps(data or {}, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"


async def handle_chat_message(message: str, session_id: str) -> AsyncIterator[str]:
    """Process a user message through the full LLM → tool calls → MCP → LLM loop.

    Yields SSE-formatted strings for streaming to the frontend.
    """
    # 0. Pre-flight: API key check
    if not OPENROUTER_API_KEY:
        yield _make_sse("error", {"message": "OPENROUTER_API_KEY não configurada."})
        yield _make_sse("done")
        return

    # 1. Session history
    history = session_manager.get_or_create(session_id)
    if not history or history[0].get("role") != "system":
        session_manager.append(session_id, {"role": "system", "content": SYSTEM_PROMPT})
    session_manager.append(session_id, {"role": "user", "content": message})

    # 2. Prepare OpenAI-format tools
    openai_tools = (
        mcp_tools_to_openai_functions(mcp_client.tools)
        if mcp_client.connected
        else None
    )

    # 3. Agentic loop
    consecutive_errors = 0

    for iteration in range(MAX_TOOL_ITERATIONS):
        messages = session_manager.get_or_create(session_id)
        full_content = ""
        tool_calls_accum: dict[int, dict] = {}
        finish_reason: str | None = None

        # 3a. Stream from OpenRouter
        try:
            async for chunk in stream_chat_completion(messages, openai_tools):
                choices = chunk.get("choices", [])
                if not choices:
                    continue
                delta = choices[0].get("delta", {})

                # Text token
                if delta.get("content"):
                    full_content += delta["content"]
                    yield _make_sse("text_delta", {"content": delta["content"]})

                # Tool call chunks (accumulated by index)
                if delta.get("tool_calls"):
                    for tc_chunk in delta["tool_calls"]:
                        idx = tc_chunk.get("index", 0)
                        if idx not in tool_calls_accum:
                            tool_calls_accum[idx] = {
                                "id": "",
                                "name": "",
                                "arguments_str": "",
                            }
                        acc = tool_calls_accum[idx]
                        if tc_chunk.get("id"):
                            acc["id"] = tc_chunk["id"]
                        fn = tc_chunk.get("function", {})
                        if fn.get("name"):
                            acc["name"] = fn["name"]
                        if fn.get("arguments"):
                            acc["arguments_str"] += fn["arguments"]

                # Track finish reason
                fr = choices[0].get("finish_reason")
                if fr:
                    finish_reason = fr

        except Exception as exc:
            logger.exception("OpenRouter streaming error")
            yield _make_sse("error", {"message": str(exc)})
            yield _make_sse("done")
            return

        # 3b. LLM requested tool calls
        if finish_reason == "tool_calls" and tool_calls_accum:
            # Save assistant message with tool_calls in history
            formatted_tool_calls = [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["name"],
                        "arguments": tc["arguments_str"],
                    },
                }
                for tc in tool_calls_accum.values()
            ]
            session_manager.append(session_id, {
                "role": "assistant",
                "content": full_content or None,
                "tool_calls": formatted_tool_calls,
            })

            for tc in tool_calls_accum.values():
                try:
                    args = json.loads(tc["arguments_str"]) if tc["arguments_str"] else {}
                except json.JSONDecodeError:
                    args = {}
                    logger.warning("Bad tool args JSON: %s", tc["arguments_str"][:200])

                yield _make_sse("tool_call", {
                    "name": tc["name"],
                    "arguments": args,
                })

                result = await mcp_client.call_tool(tc["name"], args)

                # Check for tool error
                is_error = result.startswith("[MCP error]") or result.startswith("**Error:**")

                if is_error:
                    consecutive_errors += 1
                    logger.warning(
                        "Tool '%s' error (%d/%d consecutive): %s",
                        tc["name"], consecutive_errors,
                        MAX_CONSECUTIVE_TOOL_ERRORS, result[:200],
                    )
                else:
                    consecutive_errors = 0

                yield _make_sse("tool_result", {
                    "name": tc["name"],
                    "content": result[:2000],
                })

                session_manager.append(session_id, {
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "name": tc["name"],
                    "content": result,
                })

            # Check if we hit the consecutive error limit
            if consecutive_errors >= MAX_CONSECUTIVE_TOOL_ERRORS:
                error_msg = (
                    f"As chamadas de ferramenta falharam {consecutive_errors} vezes consecutivas. "
                    f"Último erro: {result[:500]}"
                )
                logger.error(
                    "Aborting tool loop: %d consecutive errors reached limit",
                    consecutive_errors,
                )
                yield _make_sse("error", {"message": error_msg})
                # Save an assistant message explaining the error
                session_manager.append(session_id, {
                    "role": "assistant",
                    "content": f"⚠️ {error_msg}",
                })
                break

            continue  # Loop back to step 3: LLM processes tool results

        # 3c. LLM finished with text (or empty)
        if full_content:
            session_manager.append(session_id, {
                "role": "assistant",
                "content": full_content,
            })
        break

    yield _make_sse("done")
