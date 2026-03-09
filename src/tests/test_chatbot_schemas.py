"""Tests for chatbot schemas (ChatRequest, SSEEvent, ChatMessage)."""

import pytest
from pydantic import ValidationError

from backend.chatbot.schemas import ChatMessage, ChatRequest, SSEEvent


class TestChatRequest:
    def test_valid_request(self):
        req = ChatRequest(message="hello", session_id="s1")
        assert req.message == "hello"
        assert req.session_id == "s1"

    def test_empty_message_rejected(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="", session_id="s1")

    def test_message_too_long_rejected(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="x" * 4001, session_id="s1")

    def test_missing_session_id_rejected(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="hello")  # type: ignore[call-arg]

    def test_empty_session_id_rejected(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="hello", session_id="")


class TestSSEEvent:
    def test_text_delta_event(self):
        evt = SSEEvent(event="text_delta", data={"content": "hi"})
        assert evt.event == "text_delta"
        assert evt.data["content"] == "hi"

    def test_tool_call_event(self):
        evt = SSEEvent(event="tool_call", data={"name": "get_stats"})
        assert evt.event == "tool_call"

    def test_error_event(self):
        evt = SSEEvent(event="error", data={"message": "fail"})
        assert evt.event == "error"

    def test_done_event(self):
        evt = SSEEvent(event="done")
        assert evt.data == {}

    def test_invalid_event_type_rejected(self):
        with pytest.raises(ValidationError):
            SSEEvent(event="invalid_type")


class TestChatMessage:
    def test_user_message(self):
        msg = ChatMessage(role="user", content="hello")
        assert msg.role == "user"

    def test_system_message(self):
        msg = ChatMessage(role="system", content="you are helpful")
        assert msg.role == "system"

    def test_assistant_message(self):
        msg = ChatMessage(role="assistant", content="hi there")
        assert msg.role == "assistant"

    def test_tool_message_fields(self):
        msg = ChatMessage(
            role="tool",
            content="result",
            tool_call_id="call_1",
            name="get_stats",
        )
        assert msg.role == "tool"
        assert msg.tool_call_id == "call_1"
        assert msg.name == "get_stats"

    def test_invalid_role_rejected(self):
        with pytest.raises(ValidationError):
            ChatMessage(role="invalid", content="x")
