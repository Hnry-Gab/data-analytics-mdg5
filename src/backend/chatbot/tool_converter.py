"""Convert MCP Tool objects to OpenAI function-calling format for OpenRouter."""
from __future__ import annotations

import mcp.types as types


def mcp_tools_to_openai_functions(tools: list[types.Tool]) -> list[dict]:
    """Convert a list of MCP Tools to OpenAI function-calling dicts.

    The mapping is nearly 1:1 because ``Tool.inputSchema`` is already JSON Schema.
    """
    functions: list[dict] = []
    for tool in tools:
        fn = {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.inputSchema,
            },
        }
        functions.append(fn)
    return functions
