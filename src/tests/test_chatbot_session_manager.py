"""Tests for in-memory session manager."""

import time

from backend.chatbot.session_manager import SessionManager
from backend.chatbot import config as _cfg


class TestSessionManager:
    def setup_method(self):
        self.sm = SessionManager()

    def test_create_new_session(self):
        h = self.sm.get_or_create("new-1")
        assert h == []

    def test_get_existing_session(self):
        self.sm.append("s1", {"role": "user", "content": "hi"})
        h = self.sm.get_or_create("s1")
        assert len(h) == 1
        assert h[0]["content"] == "hi"

    def test_append_message(self):
        self.sm.append("s1", {"role": "user", "content": "a"})
        self.sm.append("s1", {"role": "assistant", "content": "b"})
        h = self.sm.get_or_create("s1")
        assert len(h) == 2
        assert h[0]["role"] == "user"
        assert h[1]["role"] == "assistant"

    def test_truncation_preserves_system(self):
        old = _cfg.MAX_HISTORY_MESSAGES
        _cfg.MAX_HISTORY_MESSAGES = 3
        try:
            self.sm.append("s", {"role": "system", "content": "sys"})
            self.sm.append("s", {"role": "user", "content": "m1"})
            self.sm.append("s", {"role": "assistant", "content": "m2"})
            self.sm.append("s", {"role": "user", "content": "m3"})
            h = self.sm.get_or_create("s")
            assert len(h) == 3
            assert h[0]["role"] == "system"
        finally:
            _cfg.MAX_HISTORY_MESSAGES = old

    def test_truncation_removes_oldest(self):
        old = _cfg.MAX_HISTORY_MESSAGES
        _cfg.MAX_HISTORY_MESSAGES = 2
        try:
            self.sm.append("s", {"role": "user", "content": "a"})
            self.sm.append("s", {"role": "user", "content": "b"})
            self.sm.append("s", {"role": "user", "content": "c"})
            h = self.sm.get_or_create("s")
            assert len(h) == 2
            assert h[0]["content"] == "b"
            assert h[1]["content"] == "c"
        finally:
            _cfg.MAX_HISTORY_MESSAGES = old

    def test_last_active_updated(self):
        self.sm.get_or_create("s1")
        t1 = self.sm._sessions["s1"]["last_active"]
        time.sleep(0.01)
        self.sm.get_or_create("s1")
        t2 = self.sm._sessions["s1"]["last_active"]
        assert t2 > t1

    def test_cleanup_stale_removes_old(self):
        self.sm.get_or_create("old")
        removed = self.sm.cleanup_stale(max_age_seconds=0)
        assert removed == 1
        assert "old" not in self.sm._sessions

    def test_cleanup_stale_keeps_active(self):
        self.sm.get_or_create("active")
        removed = self.sm.cleanup_stale(max_age_seconds=3600)
        assert removed == 0
        assert "active" in self.sm._sessions
