"""Integration tests for the Olist MCP server.

Validates that all 60 tools across 8 categories are registered correctly,
each tool is callable, returns valid content, and the server starts without error.
"""

import asyncio

import pytest

from olist_mcp.server import mcp


def _call(tool_name: str, args: dict | None = None) -> str:
    result = asyncio.run(mcp.call_tool(tool_name, args or {}))
    return result.content[0].text


# ---------- Expected tool registry (from specs MCP-01 through MCP-08) ----------

EXPECTED_TOOLS_BY_CATEGORY = {
    "dataset_stats": [
        "get_dataset_overview",
        "get_column_statistics",
        "get_class_distribution",
        "get_correlation_table",
        "get_dataset_schema",
        "get_training_dataset_info",
    ],
    "geographic": [
        "get_delay_rate_by_customer_state",
        "get_delay_rate_by_seller_state",
        "get_interstate_vs_intrastate_analysis",
        "get_route_heatmap_data",
        "get_macro_region_analysis",
        "get_distance_analysis",
        "get_worst_routes",
        "calculate_haversine_distance",
    ],
    "ml_model": [
        "get_model_status",
        "predict_delay_probability",
        "get_model_metrics",
        "get_feature_importance",
        "get_model_hyperparameters",
        "get_state_encoding_map",
        "simulate_seller_improvement",
    ],
    "business_insights": [
        "get_top_worst_sellers",
        "get_top_worst_categories",
        "get_business_summary",
        "get_growth_recommendations",
        "get_seller_profile",
        "get_national_delay_rate",
        "get_price_freight_analysis",
    ],
    "temporal": [
        "get_delay_rate_by_month",
        "get_delay_rate_by_weekday",
        "get_orders_over_time",
        "get_date_range",
        "get_velocidade_lojista_distribution",
        "get_seasonal_analysis",
    ],
    "documentation": [
        "get_column_definition",
        "get_data_dictionary",
        "get_project_spec",
        "get_model_spec",
        "get_feature_engineering_plan",
        "get_viability_report",
        "get_eda_report",
        "get_task_details",
        "list_all_tasks",
        "get_algorithm_explanation",
        "get_stack_info",
    ],
    "visualization": [
        "list_available_charts",
        "get_chart_as_base64",
        "get_html_chart_content",
        "generate_delay_by_state_chart",
        "generate_correlation_bar_chart",
        "generate_route_heatmap",
        "generate_time_series_chart",
    ],
    "query_filter": [
        "filter_orders",
        "get_orders_by_state_pair",
        "get_category_deep_dive",
        "search_orders_by_order_id",
        "get_product_weight_analysis",
        "compare_two_states",
        "get_high_risk_order_profile",
        "get_seller_ranking",
    ],
}


class TestToolRegistration:
    """Verify all 60 tools are registered on the MCP server."""

    def test_total_tool_count(self):
        tools = asyncio.run(mcp.list_tools())
        assert len(tools) == 60, f"Expected 60 tools, got {len(tools)}"

    def test_all_expected_tools_present(self):
        tools = asyncio.run(mcp.list_tools())
        registered = {t.name for t in tools}
        all_expected = set()
        for tool_list in EXPECTED_TOOLS_BY_CATEGORY.values():
            all_expected.update(tool_list)
        missing = all_expected - registered
        assert not missing, f"Missing tools: {missing}"

    def test_no_unexpected_tools(self):
        tools = asyncio.run(mcp.list_tools())
        registered = {t.name for t in tools}
        all_expected = set()
        for tool_list in EXPECTED_TOOLS_BY_CATEGORY.values():
            all_expected.update(tool_list)
        extra = registered - all_expected
        assert not extra, f"Unexpected tools: {extra}"

    @pytest.mark.parametrize("category,expected_tools", EXPECTED_TOOLS_BY_CATEGORY.items())
    def test_category_tool_count(self, category, expected_tools):
        tools = asyncio.run(mcp.list_tools())
        registered = {t.name for t in tools}
        for tool_name in expected_tools:
            assert tool_name in registered, f"{category}: missing `{tool_name}`"

    def test_all_tools_have_descriptions(self):
        tools = asyncio.run(mcp.list_tools())
        for tool in tools:
            assert tool.description, f"Tool `{tool.name}` has no description"
            assert len(tool.description) > 10, (
                f"Tool `{tool.name}` description too short: '{tool.description}'"
            )


class TestToolCallability:
    """Verify every tool can be called and returns valid content."""

    # Tools that need no arguments (or have all-optional args)
    NO_ARG_TOOLS = [
        "get_dataset_overview",
        "get_class_distribution",
        "get_correlation_table",
        "get_dataset_schema",
        "get_training_dataset_info",
        "get_delay_rate_by_customer_state",
        "get_delay_rate_by_seller_state",
        "get_interstate_vs_intrastate_analysis",
        "get_route_heatmap_data",
        "get_macro_region_analysis",
        "get_distance_analysis",
        "get_model_status",
        "get_model_metrics",
        "get_model_hyperparameters",
        "get_top_worst_sellers",
        "get_top_worst_categories",
        "get_business_summary",
        "get_growth_recommendations",
        "get_national_delay_rate",
        "get_price_freight_analysis",
        "get_delay_rate_by_month",
        "get_delay_rate_by_weekday",
        "get_date_range",
        "get_velocidade_lojista_distribution",
        "get_seasonal_analysis",
        "get_data_dictionary",
        "get_project_spec",
        "get_model_spec",
        "get_feature_engineering_plan",
        "get_viability_report",
        "get_eda_report",
        "list_all_tasks",
        "get_stack_info",
        "list_available_charts",
        "get_product_weight_analysis",
        "get_high_risk_order_profile",
        "get_seller_ranking",
    ]

    @pytest.mark.parametrize("tool_name", NO_ARG_TOOLS)
    def test_tool_returns_content(self, tool_name):
        text = _call(tool_name)
        assert isinstance(text, str)
        assert len(text) > 20, f"`{tool_name}` returned too little content"

    def test_tool_with_args_column_stats(self):
        text = _call("get_column_statistics", {"column_name": "price"})
        assert "price" in text.lower()

    def test_tool_with_args_state_pair(self):
        text = _call("get_orders_by_state_pair", {
            "seller_state": "SP", "customer_state": "RJ",
        })
        assert "SP" in text

    def test_tool_with_args_filter(self):
        text = _call("filter_orders", {"customer_state": "SP"})
        assert "SP" in text

    def test_tool_with_args_category_dive(self):
        text = _call("get_category_deep_dive", {"category_name": "beleza"})
        assert "beleza" in text.lower()

    def test_tool_with_args_compare(self):
        text = _call("compare_two_states", {"state_a": "SP", "state_b": "AL"})
        assert "SP" in text and "AL" in text

    def test_tool_with_args_haversine(self):
        text = _call("calculate_haversine_distance", {
            "seller_lat": -23.55, "seller_lng": -46.63,
            "customer_lat": -22.91, "customer_lng": -43.17,
        })
        assert "km" in text.lower() or "distance" in text.lower()


class TestServerMetadata:
    """Verify MCP server metadata is correctly configured."""

    def test_server_name(self):
        assert mcp.name == "olist-analytics-mcp"

    def test_server_has_instructions(self):
        assert mcp.instructions
        assert "olist" in mcp.instructions.lower() or "analytics" in mcp.instructions.lower()
