"""Olist Analytics MCP Server entry point."""

from fastmcp import FastMCP

from olist_mcp.tools import dataset_stats, documentation, geographic, temporal

mcp = FastMCP(
    name="olist-analytics-mcp",
    instructions=(
        "MCP server for Olist Brazilian e-commerce analytics. "
        "Provides tools for dataset statistics, geographic analysis, "
        "ML predictions, business insights, temporal analysis, "
        "documentation, visualization, and data querying."
    ),
)

# Register tool modules
dataset_stats.register(mcp)
documentation.register(mcp)
geographic.register(mcp)
temporal.register(mcp)

if __name__ == "__main__":
    mcp.run()
