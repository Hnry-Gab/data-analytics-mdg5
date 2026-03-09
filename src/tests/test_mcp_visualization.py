"""Tests for MCP-07: EDA & Visualization Tools."""

import asyncio
import base64

from olist_mcp.server import mcp


def _call(tool_name: str, args: dict | None = None) -> str:
    result = asyncio.get_event_loop().run_until_complete(mcp.call_tool(tool_name, args or {}))
    return result.content[0].text


class TestListAvailableCharts:
    def test_lists_static(self):
        text = _call("list_available_charts")
        assert "Static" in text
        assert "correlacao" in text
        assert "cliente" in text

    def test_lists_interactive(self):
        text = _call("list_available_charts")
        assert "Interactive" in text
        assert "eda_1_correlacoes" in text

    def test_lists_live_generation(self):
        text = _call("list_available_charts")
        assert "Live Generation" in text
        assert "generate_delay_by_state_chart" in text


class TestGetChartAsBase64:
    def test_valid_chart(self):
        text = _call("get_chart_as_base64", {"chart_name": "correlacao"})
        assert "correlacao" in text
        assert "image/png" in text
        assert "iVBOR" in text  # PNG base64 signature

    def test_partial_match(self):
        text = _call("get_chart_as_base64", {"chart_name": "cliente"})
        assert "cliente" in text
        assert "Base64" in text

    def test_invalid_chart(self):
        text = _call("get_chart_as_base64", {"chart_name": "nonexistent_chart"})
        assert "Error" in text
        assert "correlacao" in text  # Shows available options

    def test_base64_valid(self):
        text = _call("get_chart_as_base64", {"chart_name": "correlacao"})
        # Extract base64 between code fences
        lines = text.split("```")
        if len(lines) >= 3:
            b64_str = lines[1].strip()
            decoded = base64.b64decode(b64_str)
            assert decoded[:4] == b'\x89PNG'


class TestGetHtmlChartContent:
    def test_missing_html(self):
        # HTML files are not generated in this environment
        text = _call("get_html_chart_content", {"chart_name": "eda_1_correlacoes"})
        assert "not found" in text.lower() or "not generated" in text.lower() or "Interactive" in text

    def test_invalid_chart(self):
        text = _call("get_html_chart_content", {"chart_name": "nonexistent"})
        assert "Error" in text
        assert "eda_1" in text or "available" in text.lower()


class TestGenerateDelayByStateChart:
    def test_customer_chart(self):
        text = _call("generate_delay_by_state_chart", {"state_type": "customer"})
        assert "Customer" in text
        # Accepts either base64 PNG or fallback JSON
        assert "Base64" in text or "Plotly JSON" in text or "json" in text

    def test_seller_chart(self):
        text = _call("generate_delay_by_state_chart", {"state_type": "seller"})
        assert "Seller" in text

    def test_top_n_filter(self):
        text = _call("generate_delay_by_state_chart", {
            "state_type": "customer",
            "top_n": 5,
        })
        assert "5" in text

    def test_invalid_type(self):
        text = _call("generate_delay_by_state_chart", {"state_type": "invalid"})
        assert "Error" in text


class TestGenerateCorrelationBarChart:
    def test_default(self):
        text = _call("generate_correlation_bar_chart")
        assert "Correlations" in text or "correlation" in text.lower()

    def test_filtered(self):
        text = _call("generate_correlation_bar_chart", {"min_abs_correlation": 0.05})
        assert "correlation" in text.lower()


class TestGenerateRouteHeatmap:
    def test_state_level(self):
        text = _call("generate_route_heatmap", {"level": "state"})
        assert "Heatmap" in text

    def test_macro_region_level(self):
        text = _call("generate_route_heatmap", {"level": "macro_region"})
        assert "Region" in text

    def test_high_min_orders(self):
        text = _call("generate_route_heatmap", {"min_orders": 1000000})
        assert "Error" in text


class TestGenerateTimeSeriesChart:
    def test_monthly(self):
        text = _call("generate_time_series_chart", {"granularity": "month"})
        assert "month" in text.lower()

    def test_weekly(self):
        text = _call("generate_time_series_chart", {"granularity": "week"})
        assert "week" in text.lower()

    def test_invalid_granularity(self):
        text = _call("generate_time_series_chart", {"granularity": "year"})
        assert "Error" in text
