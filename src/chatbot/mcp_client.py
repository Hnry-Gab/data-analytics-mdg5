"""MCP Client Lifecycle Manager — singleton that keeps the MCP server subprocess alive."""
from __future__ import annotations

import logging
from contextlib import AsyncExitStack

import mcp.types as types
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from src.chatbot.config import MCP_SERVER_ARGS, MCP_SERVER_COMMAND, MCP_SERVER_CWD

logger = logging.getLogger(__name__)


class MCPClientManager:
    """Singleton lifecycle manager for the MCP server subprocess."""

    def __init__(self) -> None:
        self._session: ClientSession | None = None
        self._stack: AsyncExitStack | None = None
        self._tools: list[types.Tool] = []

    # -- properties ----------------------------------------------------------

    @property
    def connected(self) -> bool:
        return self._session is not None

    @property
    def tools(self) -> list[types.Tool]:
        return self._tools

    # -- lifecycle -----------------------------------------------------------

    async def start(self) -> None:
        """Spawn MCP server subprocess, handshake, and cache tool list."""
        if self._session is not None:
            logger.warning("MCP client already started — skipping")
            return

        params = StdioServerParameters(
            command=MCP_SERVER_COMMAND,
            args=MCP_SERVER_ARGS,
            cwd=MCP_SERVER_CWD,
        )

        self._stack = AsyncExitStack()
        try:
            read, write = await self._stack.enter_async_context(stdio_client(params))
            self._session = await self._stack.enter_async_context(
                ClientSession(read, write)
            )
            await self._session.initialize()

            result = await self._session.list_tools()
            self._tools = result.tools
            logger.info("Chatbot MCP: %d tools disponíveis", len(self._tools))
        except Exception:
            logger.exception("Failed to start MCP server — chatbot will run without tools")
            await self._cleanup()
            raise

    async def stop(self) -> None:
        """Close the AsyncExitStack, which terminates the subprocess."""
        await self._cleanup()
        logger.info("MCP client stopped")

    async def _cleanup(self) -> None:
        self._session = None
        self._tools = []
        if self._stack is not None:
            try:
                await self._stack.aclose()
            except Exception:
                logger.warning("Error closing MCP exit stack", exc_info=True)
            self._stack = None

    # -- tool execution ------------------------------------------------------

    async def call_tool(self, name: str, arguments: dict | None = None) -> str:
        """Execute an MCP tool and return its text content."""
        if self._session is None:
            return f"[MCP error] Not connected — cannot call tool '{name}'"

        try:
            result = await self._session.call_tool(name, arguments or {})
            parts: list[str] = []
            for block in result.content:
                if isinstance(block, types.TextContent):
                    parts.append(block.text)
            return "\n".join(parts) if parts else "[MCP] Tool returned no text content"
        except Exception as exc:
            logger.exception("MCP call_tool(%s) failed", name)
            return f"[MCP error] {exc}"


# Module-level singleton
mcp_client = MCPClientManager()
