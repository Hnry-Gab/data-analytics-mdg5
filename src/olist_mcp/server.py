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
        "Olist Brazilian e-commerce delay analytics. "
        "Dataset: 110k delivered orders, target=foi_atraso (binary delay flag, 6.77% positive rate). "
        "Key features: velocidade_lojista_dias (dispatch speed, strongest predictor), freight_value, "
        "price, product_weight_g, volume_cm3, distancia_haversine_km, rota (seller_state→customer_state). "
        "\n\n"
        "TOOLS (25): "
        "• Stats: get_dataset_overview, get_dataset_schema, get_column_statistics, search_orders_by_order_id, "
        "calculate_haversine_distance_tool, get_seller_profile "
        "• Query: dynamic_aggregate (single col agg with filters), group_by_metrics (group+multi-metric), "
        "top_n_query (ranked rows), compare_groups (A/B side-by-side), batch_query (combine multiple) "
        "• ML (CatBoost V5): predict_delay_catboost (single order), simulate_scenario (vary one feature), "
        "get_catboost_model_info, get_catboost_feature_importance "
        "• Insights: get_business_summary (5 key findings + recommendations) "
        "• Viz: list_available_charts, get_chart_as_base64 (static PNG), get_html_chart_content (interactive Plotly), "
        "generate_delay_by_state_chart, generate_correlation_bar_chart, generate_route_heatmap, "
        "generate_time_series_chart "
        "• Math: math_operation, percentage_calc, calculate_growth "
        "\n\n"
        "WORKFLOW: Start with get_dataset_overview or get_business_summary for context. "
        "Use dynamic_aggregate/group_by_metrics for exploration. "
        "Use batch_query to combine multiple queries in one call. "
        "Filter format: [{\"column\": \"col\", \"op\": \"eq|gt|lt|gte|lte|ne|in|between\", \"value\": val}]. "
        "Metrics format for group_by: [\"agg:column\"] e.g. [\"mean:foi_atraso\", \"sum:price\", \"count:order_id\"]. "
        "For predictions, required params: velocidade_lojista_dias, freight_value, price, product_weight_g, volume_cm3."
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
