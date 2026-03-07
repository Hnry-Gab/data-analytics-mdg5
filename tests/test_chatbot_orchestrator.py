"""Tests for the orchestrator agentic loop (all external deps mocked)."""

import asyncio
import importlib
import json
from unittest.mock import AsyncMock, MagicMock, patch


def _parse_sse_events(sse_strings: list[str]) -> list[dict]:
    """Parse SSE strings into list of {event, data} dicts."""
    events = []
    for s in sse_strings:
        lines = s.strip().split("\n")
        event_type = ""
        for line in lines:
            if line.startswith("event: "):
                event_type = line[7:]
            elif line.startswith("data: "):
                events.append({"event": event_type, "data": json.loads(line[6:])})
    return events


async def _collect(gen):
    return [e async for e in gen]


class TestOrchestrator:
    def test_missing_api_key(self):
        """No API key → error + done."""
        import src.chatbot.orchestrator as mod
        importlib.reload(mod)

        async def run():
            with patch.object(mod, "OPENROUTER_API_KEY", ""):
                return await _collect(mod.handle_chat_message("hi", "test-nokey"))

        events = asyncio.run(run())
        parsed = _parse_sse_events(events)
        assert parsed[0]["event"] == "error"
        assert parsed[1]["event"] == "done"

    def test_simple_text_response(self):
        """LLM returns text without tool calls → text_delta + done."""
        import src.chatbot.orchestrator as mod
        importlib.reload(mod)

        chunks = [
            {"choices": [{"delta": {"content": "Hello"}, "finish_reason": None}]},
            {"choices": [{"delta": {"content": " world"}, "finish_reason": None}]},
            {"choices": [{"delta": {}, "finish_reason": "stop"}]},
        ]

        async def mock_stream(messages, tools=None):
            for c in chunks:
                yield c

        mod.mcp_client._session = MagicMock()
        mod.mcp_client._tools = []

        async def run():
            with patch.object(mod, "OPENROUTER_API_KEY", "sk-test"), \
                 patch.object(mod, "stream_chat_completion", side_effect=mock_stream):
                return await _collect(mod.handle_chat_message("hi", "test-text"))

        events = asyncio.run(run())
        parsed = _parse_sse_events(events)
        event_types = [e["event"] for e in parsed]
        assert event_types.count("text_delta") == 2
        assert event_types[-1] == "done"
        assert parsed[0]["data"]["content"] == "Hello"

    def test_tool_call_flow(self):
        """LLM requests tool → MCP executes → LLM responds with text."""
        import src.chatbot.orchestrator as mod
        importlib.reload(mod)

        tool_chunks = [
            {"choices": [{"delta": {"tool_calls": [{"index": 0, "id": "c1", "function": {"name": "get_delay", "arguments": ""}}]}, "finish_reason": None}]},
            {"choices": [{"delta": {"tool_calls": [{"index": 0, "function": {"arguments": "{}"}}]}, "finish_reason": None}]},
            {"choices": [{"delta": {}, "finish_reason": "tool_calls"}]},
        ]
        followup_chunks = [
            {"choices": [{"delta": {"content": "6.77%"}, "finish_reason": None}]},
            {"choices": [{"delta": {}, "finish_reason": "stop"}]},
        ]
        call_count = [0]

        async def mock_stream(messages, tools=None):
            if call_count[0] == 0:
                call_count[0] += 1
                for c in tool_chunks:
                    yield c
            else:
                for c in followup_chunks:
                    yield c

        mod.mcp_client._session = MagicMock()
        mod.mcp_client._tools = []
        mod.mcp_client.call_tool = AsyncMock(return_value="National delay: 6.77%")

        async def run():
            with patch.object(mod, "OPENROUTER_API_KEY", "sk-test"), \
                 patch.object(mod, "stream_chat_completion", side_effect=mock_stream):
                return await _collect(mod.handle_chat_message("delay?", "test-tool"))

        events = asyncio.run(run())
        parsed = _parse_sse_events(events)
        event_types = [e["event"] for e in parsed]
        assert "tool_call" in event_types
        assert "tool_result" in event_types
        assert "text_delta" in event_types
        assert event_types[-1] == "done"

    def test_openrouter_error(self):
        """Stream raises exception → error + done."""
        import src.chatbot.orchestrator as mod
        importlib.reload(mod)

        async def mock_stream_fail(messages, tools=None):
            raise ConnectionError("API down")
            yield  # noqa: E501

        mod.mcp_client._session = MagicMock()
        mod.mcp_client._tools = []

        async def run():
            with patch.object(mod, "OPENROUTER_API_KEY", "sk-test"), \
                 patch.object(mod, "stream_chat_completion", side_effect=mock_stream_fail):
                return await _collect(mod.handle_chat_message("hi", "test-err"))

        events = asyncio.run(run())
        parsed = _parse_sse_events(events)
        event_types = [e["event"] for e in parsed]
        assert "error" in event_types
        assert event_types[-1] == "done"

    def test_system_prompt_injected(self):
        """New session gets system prompt as first message."""
        import src.chatbot.orchestrator as mod
        importlib.reload(mod)

        chunks = [
            {"choices": [{"delta": {"content": "ok"}, "finish_reason": None}]},
            {"choices": [{"delta": {}, "finish_reason": "stop"}]},
        ]

        async def mock_stream(messages, tools=None):
            assert messages[0]["role"] == "system"
            assert "Olist" in messages[0]["content"]
            for c in chunks:
                yield c

        mod.mcp_client._session = MagicMock()
        mod.mcp_client._tools = []

        async def run():
            with patch.object(mod, "OPENROUTER_API_KEY", "sk-test"), \
                 patch.object(mod, "stream_chat_completion", side_effect=mock_stream):
                return await _collect(mod.handle_chat_message("test", "test-sys"))

        events = asyncio.run(run())
        parsed = _parse_sse_events(events)
        assert parsed[-1]["event"] == "done"
