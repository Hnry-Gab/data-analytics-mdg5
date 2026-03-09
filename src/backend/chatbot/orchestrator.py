"""Orchestrator — agentic loop that wires LLM, MCP tools, and session history."""
from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator

import re

from backend.chatbot.config import MAX_CONSECUTIVE_TOOL_ERRORS, MAX_TOOL_ITERATIONS, MAX_TOOL_RESULT_CHARS, OPENROUTER_API_KEY
from backend.chatbot.mcp_client import mcp_client
from backend.chatbot.openrouter_client import stream_chat_completion
from backend.chatbot.session_manager import session_manager
from backend.chatbot.system_prompt import SYSTEM_PROMPT
from backend.chatbot.tool_converter import mcp_tools_to_openai_functions

logger = logging.getLogger(__name__)

_ERROR_MARKERS = (
    "[MCP error]",
    "**Error",
    "**Error:**",
    "Unsupported query type",
    "Error:",
)


def _is_tool_error(result: str) -> bool:
    """Detect if a tool result represents an error.

    Handles both simple error strings and batch results where
    sub-queries contain inline errors (e.g. batch_query with
    multiple ``**Error:**`` entries).
    """
    if not result:
        return False

    # Direct prefix match
    for marker in _ERROR_MARKERS:
        if result.startswith(marker):
            return True

    # For batch results: count error vs success sections.
    # Only check within "--- QUERY" delimited batch output to avoid false positives.
    if "--- QUERY" in result and "**Error:**" in result:
        total_sections = result.count("--- QUERY")
        error_sections = len(re.findall(r"--- QUERY \d+.*?\n\*\*Error:\*\*", result))
        if total_sections > 0 and error_sections > 0:
            # If majority of queries failed, it's an error
            if error_sections / total_sections > 0.5:
                return True

    return False


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
    consecutive_empty = 0
    last_tool_signature: str | None = None
    repeated_call_count = 0
    MAX_REPEATED_CALLS = 1  # Break after 1 repeat (2nd identical call)

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

            # Detect repeated identical tool calls (LLM stuck in a loop)
            call_signature = json.dumps(
                [(tc["name"], tc["arguments_str"]) for tc in tool_calls_accum.values()],
                sort_keys=True,
            )
            if call_signature == last_tool_signature:
                repeated_call_count += 1
            else:
                repeated_call_count = 0
                last_tool_signature = call_signature

            if repeated_call_count >= MAX_REPEATED_CALLS:
                logger.warning(
                    "LLM repeated identical tool call %d times — injecting nudge",
                    repeated_call_count + 1,
                )
                # Don't execute the tool again. Instead, add dummy tool
                # responses and a nudge so the LLM uses data it already has.
                for tc in tool_calls_accum.values():
                    session_manager.append(session_id, {
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "name": tc["name"],
                        "content": (
                            "⚠️ Chamada duplicada bloqueada. Os dados já foram retornados na chamada anterior. "
                            "Use os resultados que você já possui para responder ao usuário. "
                            "NÃO chame ferramentas novamente — responda diretamente com texto."
                        ),
                    })
                continue  # Let LLM process the nudge

            for tc in tool_calls_accum.values():
                try:
                    args = json.loads(tc["arguments_str"]) if tc["arguments_str"] else {}
                except json.JSONDecodeError:
                    logger.warning("Bad tool args JSON: %s", tc["arguments_str"][:200])
                    # Tell the LLM about the malformed args so it can self-correct
                    session_manager.append(session_id, {
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "name": tc["name"],
                        "content": (
                            f"[MCP error] Malformed JSON arguments: {tc['arguments_str'][:200]}. "
                            "Please fix the JSON syntax and retry."
                        ),
                    })
                    consecutive_errors += 1
                    continue

                yield _make_sse("tool_call", {
                    "name": tc["name"],
                    "arguments": args,
                })

                result = await mcp_client.call_tool(tc["name"], args)

                # Check for tool error — covers both full-error results
                # and batch results where most/all sub-queries errored.
                is_error = _is_tool_error(result)

                if is_error:
                    consecutive_errors += 1
                    logger.warning(
                        "Tool '%s' error (%d/%d consecutive): %s",
                        tc["name"], consecutive_errors,
                        MAX_CONSECUTIVE_TOOL_ERRORS, result[:200],
                    )
                elif "--- QUERY" in result and "**Error:**" in result:
                    # Partial batch failure: some sub-queries failed but majority succeeded.
                    # Extract which queries failed and tell the LLM specifically.
                    consecutive_errors = 0
                    failed = re.findall(
                        r"--- QUERY (\d+).*?\n\*\*Error:\*\*\s*(.+?)(?:\n|$)",
                        result,
                    )
                    if failed:
                        details = "; ".join(
                            f"Query {num}: {msg.strip()}" for num, msg in failed
                        )
                        result += (
                            f"\n\n⚠️ **System note:** {len(failed)} sub-query(ies) failed: {details}. "
                            "The successful queries returned valid data — do NOT retry them. "
                            "Only fix or drop the failed queries."
                        )
                else:
                    consecutive_errors = 0

                yield _make_sse("tool_result", {
                    "name": tc["name"],
                    "content": result[:2000],
                })

                # Cap result size to prevent context bloat
                capped_result = result[:MAX_TOOL_RESULT_CHARS] if len(result) > MAX_TOOL_RESULT_CHARS else result
                if len(result) > MAX_TOOL_RESULT_CHARS:
                    capped_result += f"\n\n⚠️ [Result truncated from {len(result):,} to {MAX_TOOL_RESULT_CHARS:,} chars]"

                session_manager.append(session_id, {
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "name": tc["name"],
                    "content": capped_result,
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

        # LLM returned empty after processing tool results — nudge it to respond
        if iteration > 0 and not full_content:
            consecutive_empty += 1
            logger.warning("LLM returned empty response (iteration %d, nudge %d)", iteration, consecutive_empty)

            if consecutive_empty >= 2:
                error_msg = "Desculpe, não consegui gerar uma resposta. Por favor, tente reformular sua pergunta."
                yield _make_sse("error", {"message": error_msg})
                session_manager.append(session_id, {
                    "role": "assistant",
                    "content": f"⚠️ {error_msg}",
                })
                break

            session_manager.append(session_id, {
                "role": "user",
                "content": (
                    "Você recebeu os resultados das ferramentas acima mas não gerou uma resposta. "
                    "Por favor, resuma os resultados e responda à pergunta do usuário."
                ),
            })
            continue

        break

    yield _make_sse("done")
