"""Tests for MCP client lifecycle manager."""

import asyncio

from src.chatbot.mcp_client import MCPClientManager


class TestMCPClientManager:
    def test_initial_state_disconnected(self):
        client = MCPClientManager()
        assert client.connected is False

    def test_tools_empty_before_start(self):
        client = MCPClientManager()
        assert client.tools == []

    def test_call_tool_when_disconnected(self):
        """call_tool on disconnected client returns error string."""
        client = MCPClientManager()
        result = asyncio.run(client.call_tool("nonexistent", {}))
        assert "[MCP error]" in result
        assert "Not connected" in result


class TestMCPClientIntegration:
    """Integration tests requiring olist_mcp server available."""

    def test_start_discovers_tools(self):
        async def run():
            client = MCPClientManager()
            await client.start()
            try:
                assert client.connected is True
                assert len(client.tools) == 60
            finally:
                await client.stop()

        asyncio.run(run())

    def test_stop_disconnects(self):
        async def run():
            client = MCPClientManager()
            await client.start()
            await client.stop()
            assert client.connected is False
            assert client.tools == []

        asyncio.run(run())

    def test_double_start_is_idempotent(self):
        async def run():
            client = MCPClientManager()
            await client.start()
            try:
                await client.start()  # should not raise
                assert client.connected is True
            finally:
                await client.stop()

        asyncio.run(run())

    def test_call_tool_invalid_name(self):
        async def run():
            client = MCPClientManager()
            await client.start()
            try:
                result = await client.call_tool("nonexistent_tool_xyz", {})
                assert "unknown" in result.lower() or "error" in result.lower()
            finally:
                await client.stop()

        asyncio.run(run())
