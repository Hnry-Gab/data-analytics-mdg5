"""Error handling tests for the Olist MCP server.

Validates invalid inputs are handled gracefully.
"""

import asyncio

from olist_mcp.server import mcp


def _call(tool_name: str, args: dict | None = None) -> str:
    result = asyncio.get_event_loop().run_until_complete(mcp.call_tool(tool_name, args or {}))
    return result.content[0].text


class TestInvalidInputHandling:
    def test_invalid_chart_name(self):
        text = _call("get_chart_as_base64", {"chart_name": "nonexistent_zzz"})
        assert "Error" in text

    def test_invalid_html_chart_name(self):
        text = _call("get_html_chart_content", {"chart_name": "nonexistent"})
        assert "Error" in text

    def test_invalid_order_id(self):
        text = _call("search_orders_by_order_id", {"order_id": "fake_order_id_xyz"})
        assert "Error" in text or "not found" in text.lower()

    def test_invalid_chart_state_type(self):
        text = _call("generate_delay_by_state_chart", {"state_type": "invalid"})
        assert "Error" in text

    def test_invalid_timeseries_granularity(self):
        text = _call("generate_time_series_chart", {"granularity": "year"})
        assert "Error" in text

    def test_heatmap_impossible_min_orders(self):
        text = _call("generate_route_heatmap", {"min_orders": 99999999})
        assert "Error" in text

    def test_invalid_column_stats(self):
        text = _call("get_column_statistics", {"column_name": "nonexistent_col"})
        assert "Error" in text

    def test_dynamic_aggregate_invalid_column(self):
        text = _call("dynamic_aggregate", {"column": "zzz", "agg": "sum"})
        assert "Error" in text

    def test_dynamic_aggregate_invalid_agg(self):
        text = _call("dynamic_aggregate", {"column": "price", "agg": "average"})
        assert "Error" in text

    def test_compare_groups_empty(self):
        text = _call("compare_groups", {
            "group_a_filters": [{"column": "customer_state", "op": "eq", "value": "ZZ"}],
            "group_b_filters": [{"column": "customer_state", "op": "eq", "value": "SP"}],
            "metrics": ["mean:price"],
        })
        assert "Error" in text

    def test_correlation_chart_high_threshold(self):
        text = _call("generate_correlation_bar_chart", {"min_abs_correlation": 0.99})
        assert len(text) > 10  # Should not crash
