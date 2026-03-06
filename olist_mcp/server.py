"""Olist Analytics MCP Server entry point."""

from fastmcp import FastMCP

from olist_mcp.tools import (
    business_insights,
    dataset_stats,
    documentation,
    geographic,
    ml_model,
    query_filter,
    temporal,
)

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
business_insights.register(mcp)
ml_model.register(mcp)
query_filter.register(mcp)

if __name__ == "__main__":
    mcp.run()
