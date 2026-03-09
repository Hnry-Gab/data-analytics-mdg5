"""In-memory session manager — conversation history per session_id."""
from __future__ import annotations

import time

from backend.chatbot import config as _cfg


class SessionManager:
    """Stores chat history keyed by session_id (in-memory, lost on restart)."""

    def __init__(self) -> None:
        self._sessions: dict[str, dict] = {}

    def get_or_create(self, session_id: str) -> list[dict]:
        """Return existing history or create an empty session."""
        now = time.time()
        if session_id not in self._sessions:
            self._sessions[session_id] = {
                "history": [],
                "created_at": now,
                "last_active": now,
            }
        self._sessions[session_id]["last_active"] = now
        return self._sessions[session_id]["history"]

    def append(self, session_id: str, message: dict) -> None:
        """Add a message and enforce the history size limit."""
        history = self.get_or_create(session_id)
        history.append(message)
        self._truncate(history)

    def cleanup_stale(self, max_age_seconds: float = 3600) -> int:
        """Remove sessions inactive for longer than *max_age_seconds*."""
        now = time.time()
        stale = [
            sid
            for sid, data in self._sessions.items()
            if now - data["last_active"] > max_age_seconds
        ]
        for sid in stale:
            del self._sessions[sid]
        return len(stale)

    # -- internals -----------------------------------------------------------

    @staticmethod
    def _truncate(history: list[dict]) -> None:
        """Trim history to MAX_HISTORY_MESSAGES, preserving the system prompt."""
        while len(history) > _cfg.MAX_HISTORY_MESSAGES:
            # Never remove index 0 if it's the system prompt
            if history[0].get("role") == "system":
                del history[1]
            else:
                del history[0]


# Module-level singleton
session_manager = SessionManager()
