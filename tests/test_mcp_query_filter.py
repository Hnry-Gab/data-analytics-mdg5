"""Tests for MCP-08: Filtering & Query Tools."""

import asyncio

from olist_mcp.cache import DataStore
from olist_mcp.server import mcp


def _call(tool_name: str, args: dict | None = None) -> str:
    result = asyncio.run(mcp.call_tool(tool_name, args or {}))
    return result.content[0].text


class TestFilterOrders:
    def test_single_filter(self):
        text = _call("filter_orders", {"customer_state": "SP"})
        assert "Filtered" in text
        assert "SP" in text
        assert "delay" in text.lower()

    def test_multiple_filters(self):
        text = _call("filter_orders", {
            "customer_state": "SP",
            "foi_atraso": 1,
            "min_price": 50.0,
        })
        assert "SP" in text
        assert "foi_atraso" in text
        assert "min_price" in text

    def test_no_match(self):
        text = _call("filter_orders", {
            "customer_state": "SP",
            "max_price": 0.01,
        })
        assert "No orders matched" in text or "Filtered" in text

    def test_date_filter(self):
        text = _call("filter_orders", {
            "start_date": "2017-06-01",
            "end_date": "2017-12-31",
        })
        assert "Filtered" in text

    def test_never_exposes_rows(self):
        text = _call("filter_orders", {"customer_state": "SP"})
        # Should show aggregate stats, not individual order IDs
        assert "Aggregate" in text or "Statistics" in text


class TestGetOrdersByStatePair:
    def test_valid_route(self):
        text = _call("get_orders_by_state_pair", {
            "seller_state": "SP",
            "customer_state": "RJ",
        })
        assert "Route" in text
        assert "SP" in text
        assert "RJ" in text
        assert "Delay rate" in text

    def test_min_orders_validation(self):
        text = _call("get_orders_by_state_pair", {
            "seller_state": "AC",
            "customer_state": "AC",
            "min_orders": 100000,
        })
        assert "Error" in text


class TestGetCategoryDeepDive:
    def test_exact_category(self):
        text = _call("get_category_deep_dive", {"category_name": "cama_mesa_banho"})
        assert "cama_mesa_banho" in text
        assert "Delay rate" in text

    def test_partial_match(self):
        text = _call("get_category_deep_dive", {"category_name": "beleza"})
        assert "beleza" in text.lower()

    def test_invalid_category(self):
        text = _call("get_category_deep_dive", {"category_name": "zzz_nonexistent_zzz"})
        assert "Error" in text

    def test_shows_states(self):
        text = _call("get_category_deep_dive", {"category_name": "cama_mesa_banho"})
        assert "Customer States" in text
        assert "Seller States" in text


class TestSearchOrdersByOrderId:
    def test_valid_order(self):
        df = DataStore.df()
        order_id = df["order_id"].iloc[0]
        text = _call("search_orders_by_order_id", {"order_id": order_id})
        assert "Order" in text
        assert order_id in text
        assert "Identification" in text
        assert "Dates" in text
        assert "Location" in text

    def test_invalid_order(self):
        text = _call("search_orders_by_order_id", {"order_id": "nonexistent_order_id"})
        assert "Error" in text


class TestProductWeightAnalysis:
    def test_default_bins(self):
        text = _call("get_product_weight_analysis")
        assert "0-500" in text
        assert "30000+" in text
        assert "Pearson" in text

    def test_custom_bins(self):
        text = _call("get_product_weight_analysis", {
            "weight_bins": [0, 1000, 5000, 50000],
        })
        assert "0-1000" in text
        assert "Custom" in text


class TestCompareTwoStates:
    def test_sp_vs_al(self):
        text = _call("compare_two_states", {
            "state_a": "SP",
            "state_b": "AL",
        })
        assert "SP" in text
        assert "AL" in text
        assert "Delay rate" in text
        assert "Key Differences" in text

    def test_seller_perspective(self):
        text = _call("compare_two_states", {
            "state_a": "SP",
            "state_b": "RJ",
            "perspective": "seller",
        })
        assert "Seller" in text

    def test_invalid_state(self):
        text = _call("compare_two_states", {
            "state_a": "SP",
            "state_b": "XX",
        })
        assert "Error" in text


class TestHighRiskOrderProfile:
    def test_profile_content(self):
        text = _call("get_high_risk_order_profile")
        assert "High-Risk" in text
        assert "velocidade_lojista_dias" in text
        assert "Interstate" in text or "interstate" in text

    def test_categories(self):
        text = _call("get_high_risk_order_profile")
        assert "Categories" in text

    def test_seasonality(self):
        text = _call("get_high_risk_order_profile")
        assert "Seasonality" in text or "Peak month" in text


class TestSellerRanking:
    def test_delay_rate_ranking(self):
        text = _call("get_seller_ranking", {"metric": "delay_rate", "top_n": 5})
        assert "delay_rate" in text
        assert "seller_id" in text

    def test_total_orders_ranking(self):
        text = _call("get_seller_ranking", {"metric": "total_orders", "top_n": 5})
        assert "total_orders" in text

    def test_state_filter(self):
        text = _call("get_seller_ranking", {
            "metric": "delay_rate",
            "top_n": 5,
            "state": "SP",
        })
        assert "SP" in text

    def test_invalid_metric(self):
        text = _call("get_seller_ranking", {"metric": "invalid_metric"})
        assert "Error" in text

    def test_min_orders_note(self):
        text = _call("get_seller_ranking")
        assert "30" in text or "min" in text.lower()
