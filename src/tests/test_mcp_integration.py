"""Integration tests for the Olist MCP server.

Validates that all 26 tools across 6 categories are registered correctly.
"""

import asyncio

import pytest

from olist_mcp.server import mcp


def _call(tool_name: str, args: dict | None = None) -> str:
    result = asyncio.run(mcp.call_tool(tool_name, args or {}))
    return result.content[0].text


EXPECTED_TOOLS_BY_CATEGORY = {
    "dataset_stats": [
        "get_dataset_overview",
        "get_column_statistics",
        "get_dataset_schema",
        "search_orders_by_order_id",
        "calculate_haversine_distance_tool",
    ],
    "dynamic_query": [
        "dynamic_aggregate",
        "group_by_metrics",
        "top_n_query",
        "compare_groups",
        "batch_query",
    ],
    "catboost_ml": [
        "predict_delay_catboost",
        "get_catboost_model_info",
        "get_catboost_feature_importance",
        "simulate_scenario",
    ],
    "business_insights": [
        "get_business_summary",
        "get_seller_profile",
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
    "calculator": [
        "math_operation",
        "percentage_calc",
        "calculate_growth",
    ],
}


class TestToolRegistration:
    def test_total_tool_count(self):
        tools = asyncio.run(mcp.list_tools())
        assert len(tools) == 26, f"Expected 26 tools, got {len(tools)}"

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

    def test_all_tools_have_descriptions(self):
        tools = asyncio.run(mcp.list_tools())
        for tool in tools:
            assert tool.description, f"Tool `{tool.name}` has no description"
            assert len(tool.description) > 10, f"Tool `{tool.name}` description too short"


class TestServerMetadata:
    def test_server_name(self):
        assert mcp.name == "olist-analytics-mcp"

    def test_server_has_instructions(self):
        assert mcp.instructions
        assert "foi_atraso" in mcp.instructions
