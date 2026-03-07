"""Tests for chatbot FastAPI routes."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.chatbot.routes import router

# Standalone test app (avoids importing src.main which needs catboost)
from fastapi import FastAPI

_app = FastAPI()
_app.include_router(router)


class TestChatEndpoint:
    def setup_method(self):
        self.client = TestClient(_app)

    def test_chat_disabled_returns_503(self):
        with patch("src.chatbot.routes.CHATBOT_ENABLED", False):
            resp = self.client.post(
                "/api/chat",
                json={"message": "hi", "session_id": "s1"},
            )
        assert resp.status_code == 503

    def test_chat_no_api_key_returns_503(self):
        with patch("src.chatbot.routes.CHATBOT_ENABLED", True), \
             patch("src.chatbot.routes.OPENROUTER_API_KEY", ""):
            resp = self.client.post(
                "/api/chat",
                json={"message": "hi", "session_id": "s1"},
            )
        assert resp.status_code == 503

    def test_chat_invalid_request_returns_422(self):
        with patch("src.chatbot.routes.CHATBOT_ENABLED", True), \
             patch("src.chatbot.routes.OPENROUTER_API_KEY", "sk-test"):
            resp = self.client.post("/api/chat", json={"message": ""})
        assert resp.status_code == 422

    def test_chat_returns_sse_content_type(self):
        """With valid config, the response should be text/event-stream."""
        async def mock_handler(message, session_id):
            yield 'event: done\ndata: {}\n\n'

        with patch("src.chatbot.routes.CHATBOT_ENABLED", True), \
             patch("src.chatbot.routes.OPENROUTER_API_KEY", "sk-test"), \
             patch("src.chatbot.routes.handle_chat_message", mock_handler):
            resp = self.client.post(
                "/api/chat",
                json={"message": "hello", "session_id": "s1"},
            )
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers["content-type"]


class TestChatStatusEndpoint:
    def setup_method(self):
        self.client = TestClient(_app)

    def test_status_returns_json(self):
        resp = self.client.get("/api/chat/status")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/json"

    def test_status_fields(self):
        resp = self.client.get("/api/chat/status")
        data = resp.json()
        assert "enabled" in data
        assert "llm_configured" in data
        assert "mcp_connected" in data
        assert "tools_available" in data
        assert isinstance(data["tools_available"], int)
