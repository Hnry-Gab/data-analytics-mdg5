"""Tests for MCP Tool → OpenAI function format converter."""

import mcp.types as types

from src.chatbot.tool_converter import mcp_tools_to_openai_functions


class TestToolConverter:
    def test_convert_single_tool(self):
        tools = [
            types.Tool(
                name="get_overview",
                description="Returns overview",
                inputSchema={"type": "object", "properties": {}},
            )
        ]
        funcs = mcp_tools_to_openai_functions(tools)
        assert len(funcs) == 1
        assert funcs[0]["type"] == "function"
        assert funcs[0]["function"]["name"] == "get_overview"
        assert funcs[0]["function"]["description"] == "Returns overview"

    def test_convert_tool_no_description(self):
        tools = [
            types.Tool(
                name="no_desc",
                description=None,
                inputSchema={"type": "object", "properties": {}},
            )
        ]
        funcs = mcp_tools_to_openai_functions(tools)
        assert funcs[0]["function"]["description"] == ""

    def test_convert_tool_with_required_params(self):
        tools = [
            types.Tool(
                name="get_stats",
                description="Stats",
                inputSchema={
                    "type": "object",
                    "properties": {"col": {"type": "string"}},
                    "required": ["col"],
                },
            )
        ]
        funcs = mcp_tools_to_openai_functions(tools)
        assert funcs[0]["function"]["parameters"]["required"] == ["col"]

    def test_output_format_matches_openai(self):
        tools = [
            types.Tool(
                name="fn",
                description="desc",
                inputSchema={"type": "object", "properties": {}},
            )
        ]
        funcs = mcp_tools_to_openai_functions(tools)
        fn = funcs[0]
        assert set(fn.keys()) == {"type", "function"}
        assert set(fn["function"].keys()) == {"name", "description", "parameters"}

    def test_convert_empty_list(self):
        funcs = mcp_tools_to_openai_functions([])
        assert funcs == []

    def test_convert_multiple_tools(self):
        tools = [
            types.Tool(name=f"tool_{i}", description=f"Desc {i}", inputSchema={"type": "object", "properties": {}})
            for i in range(5)
        ]
        funcs = mcp_tools_to_openai_functions(tools)
        assert len(funcs) == 5
        assert [f["function"]["name"] for f in funcs] == [f"tool_{i}" for i in range(5)]
