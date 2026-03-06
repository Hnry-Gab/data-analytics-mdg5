"""Olist Analytics MCP Server entry point."""

from fastmcp import FastMCP

mcp = FastMCP(
    name="olist-analytics-mcp",
    instructions=(
        "MCP server for Olist Brazilian e-commerce analytics. "
        "Provides tools for dataset statistics, geographic analysis, "
        "ML predictions, business insights, temporal analysis, "
        "documentation, visualization, and data querying."
    ),
)

if __name__ == "__main__":
    mcp.run()
