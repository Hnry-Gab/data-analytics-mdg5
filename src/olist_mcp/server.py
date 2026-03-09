"""Olist Analytics MCP Server entry point."""

from fastmcp import FastMCP

from olist_mcp.tools import (
    business_insights,
    catboost_ml,
    dataset_stats,
    dynamic_query,
    visualization,
    calculator,
)

mcp = FastMCP(
    name="olist-analytics-mcp",
    instructions=(
        "MCP server for Olist Brazilian e-commerce analytics. "
        "25 tools: dynamic queries (aggregate, group_by, top_n, compare, batch), "
        "CatBoost V5 ML (predict, model_info, feature_importance, simulate), "
        "dataset stats, business insights, visualization, and calculator."
    ),
)

# Register tool modules (5 modules, 22 tools total)
dataset_stats.register(mcp)
dynamic_query.register(mcp)
catboost_ml.register(mcp)
business_insights.register(mcp)
visualization.register(mcp)
calculator.register(mcp)

if __name__ == "__main__":
    mcp.run()
