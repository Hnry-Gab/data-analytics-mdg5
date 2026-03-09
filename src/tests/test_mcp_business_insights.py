"""Tests for Business Insights Tools (2 tools)."""

import asyncio

from olist_mcp.cache import DataStore
from olist_mcp.server import mcp


def _call(tool_name: str, args: dict | None = None) -> str:
    result = asyncio.run(mcp.call_tool(tool_name, args or {}))
    return result.content[0].text


class TestBusinessSummary:
    def test_five_sections(self):
        text = _call("get_business_summary")
        assert "Geographic" in text
        assert "Route" in text
        assert "Feature" in text
        assert "CatBoost" in text

    def test_national_rate(self):
        text = _call("get_business_summary")
        assert "delay rate" in text.lower()


class TestSellerProfile:
    def test_valid_seller(self):
        df = DataStore.df()
        seller_id = df["seller_id"].value_counts().index[0]
        text = _call("get_seller_profile", {"seller_id": seller_id})
        assert "Seller Profile" in text
        assert "Historical delay rate" in text

    def test_invalid_seller(self):
        text = _call("get_seller_profile", {"seller_id": "nonexistent"})
        assert "Error" in text
