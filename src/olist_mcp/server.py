"""Olist Analytics MCP Server entry point."""

from fastmcp import FastMCP

from .tools import (
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
        "Olist Brazilian e-commerce delay analytics. "
        "Dataset: 110k delivered orders, target=foi_atraso (binary delay flag, 6.77% positive rate). "
        "Key features: velocidade_lojista_dias (dispatch speed, strongest predictor), freight_value, "
        "price, product_weight_g, volume_cm3, distancia_haversine_km, rota (seller_state→customer_state). "
        "\n\n"
        "WORKFLOW: Start with get_dataset_overview or get_business_summary for context. "
        "Use dynamic_aggregate/group_by_metrics for exploration. "
        "Use batch_query to combine multiple queries in one call. "
        "Filter format: [{\"column\": \"col\", \"op\": \"eq|neq|gt|gte|lt|lte|contains|in|notnull\", \"value\": val}]. "
        "Metrics format for group_by: [\"agg:column\"] e.g. [\"mean:foi_atraso\", \"sum:price\", \"count:order_id\"]. "
        "For predictions, required params: velocidade_lojista_dias, freight_value, price, product_weight_g, volume_cm3."
    ),
)

# Register tool modules (6 modules, 26 tools total)
dataset_stats.register(mcp)
dynamic_query.register(mcp)
catboost_ml.register(mcp)
business_insights.register(mcp)
visualization.register(mcp)
calculator.register(mcp)

if __name__ == "__main__":
    mcp.run()
