"""Tests for MCP-02: Geographic Analysis Tools."""

import asyncio

import pytest

from olist_mcp.server import mcp


def _call(tool_name: str, args: dict | None = None) -> str:
    result = asyncio.run(mcp.call_tool(tool_name, args or {}))
    return result.content[0].text


class TestDelayRateByCustomerState:
    def test_returns_all_states(self):
        text = _call("get_delay_rate_by_customer_state")
        assert "AL" in text
        assert "SP" in text

    def test_al_is_worst(self):
        text = _call("get_delay_rate_by_customer_state")
        assert "20.84" in text  # AL delay rate

    def test_national_average(self):
        text = _call("get_delay_rate_by_customer_state")
        assert "6.59" in text

    def test_sort_asc(self):
        text = _call("get_delay_rate_by_customer_state", {"sort_order": "asc"})
        lines = text.split("\n")
        # First data row should NOT be AL (worst)
        first_data = [l for l in lines if "| " in l and "customer_state" not in l and "---" not in l]
        assert first_data[0].find("AL") == -1 or "20.84" not in first_data[0]


class TestDelayRateBySellerState:
    def test_returns_markdown(self):
        text = _call("get_delay_rate_by_seller_state")
        assert "Seller State" in text
        assert "delay_rate" in text


class TestInterstateAnalysis:
    def test_intrastate_lower(self):
        text = _call("get_interstate_vs_intrastate_analysis")
        assert "Intrastate" in text
        assert "Interstate" in text
        assert "4.45" in text or "4.4" in text  # intrastate ~4.45%

    def test_interstate_percentage(self):
        text = _call("get_interstate_vs_intrastate_analysis")
        assert "63" in text or "64" in text  # ~63.8% interstate


class TestRouteHeatmap:
    def test_returns_pivot(self):
        text = _call("get_route_heatmap_data")
        assert "Heatmap" in text

    def test_filter_by_seller(self):
        text = _call("get_route_heatmap_data", {"seller_state": "SP"})
        assert "SP" in text

    def test_high_min_orders_reduces_data(self):
        text = _call("get_route_heatmap_data", {"min_orders": 10000})
        # Very few routes have 10k+ orders
        assert len(text) < 2000


class TestMacroRegionAnalysis:
    def test_five_regions(self):
        text = _call("get_macro_region_analysis")
        for region in ["Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"]:
            assert region in text

    def test_both_perspectives(self):
        text = _call("get_macro_region_analysis")
        assert "Destination" in text
        assert "Origin" in text


class TestDistanceAnalysis:
    def test_pearson_value(self):
        text = _call("get_distance_analysis")
        assert "0.0753" in text

    def test_nan_count(self):
        text = _call("get_distance_analysis")
        assert "536" in text  # NaN rows


class TestWorstRoutes:
    def test_returns_routes(self):
        text = _call("get_worst_routes", {"top_n": 5})
        assert "→" in text
        assert "Worst Routes" in text


class TestHaversineCalculation:
    def test_sp_to_rj(self):
        text = _call("calculate_haversine_distance", {
            "seller_lat": -23.5505, "seller_lng": -46.6333,
            "customer_lat": -22.9068, "customer_lng": -43.1729,
        })
        assert "360" in text  # ~360.75 km
