"""Tests for MCP-04: Business Insights Tools."""

import asyncio

from olist_mcp.cache import DataStore
from olist_mcp.server import mcp


def _call(tool_name: str, args: dict | None = None) -> str:
    result = asyncio.run(mcp.call_tool(tool_name, args or {}))
    return result.content[0].text


class TestTopWorstSellers:
    def test_returns_sellers(self):
        text = _call("get_top_worst_sellers", {"top_n": 5})
        assert "Worst Sellers" in text
        assert "seller_id" in text

    def test_audit_action(self):
        text = _call("get_top_worst_sellers")
        assert "audited" in text.lower()


class TestTopWorstCategories:
    def test_returns_categories(self):
        text = _call("get_top_worst_categories", {"top_n": 5})
        assert "Worst Categories" in text


class TestBusinessSummary:
    def test_five_sections(self):
        text = _call("get_business_summary")
        assert "Geographic" in text
        assert "Route" in text
        assert "Feature" in text
        assert "Model" in text

    def test_al_worst(self):
        text = _call("get_business_summary")
        assert "AL" in text
        assert "20.8" in text


class TestGrowthRecommendations:
    def test_four_priorities(self):
        text = _call("get_growth_recommendations")
        assert "Priority 1" in text
        assert "Priority 4" in text

    def test_actionable(self):
        text = _call("get_growth_recommendations")
        assert "Action" in text


class TestSellerProfile:
    def test_valid_seller(self):
        df = DataStore.df()
        seller_id = df["seller_id"].value_counts().index[0]
        text = _call("get_seller_profile", {"seller_id": seller_id})
        assert "Seller Profile" in text
        assert "State" in text
        assert "Delay rate" in text

    def test_invalid_seller(self):
        text = _call("get_seller_profile", {"seller_id": "nonexistent"})
        assert "Error" in text


class TestNationalDelayRate:
    def test_rate_value(self):
        text = _call("get_national_delay_rate")
        assert "6.59" in text

    def test_worst_and_best(self):
        text = _call("get_national_delay_rate")
        assert "Worst" in text
        assert "Best" in text


class TestPriceFreightAnalysis:
    def test_correlations(self):
        text = _call("get_price_freight_analysis")
        assert "0.0230" in text or "0.023" in text  # price
        assert "0.0467" in text  # freight

    def test_insight(self):
        text = _call("get_price_freight_analysis")
        assert "Insight" in text
