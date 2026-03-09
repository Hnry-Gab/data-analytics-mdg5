"""Tests for Dataset Statistics Tools (5 tools)."""

import asyncio

import pytest

from olist_mcp.server import mcp


def _call(tool_name: str, args: dict | None = None) -> str:
    result = asyncio.run(mcp.call_tool(tool_name, args or {}))
    return result.content[0].text


class TestGetDatasetOverview:
    def test_returns_markdown(self):
        text = _call("get_dataset_overview")
        assert "## Dataset Overview" in text

    def test_contains_dimensions(self):
        text = _call("get_dataset_overview")
        assert "109" in text  # ~109K rows
        assert "columns" in text

    def test_contains_target_distribution(self):
        text = _call("get_dataset_overview")
        assert "foi_atraso" in text

    def test_contains_catboost_ref(self):
        text = _call("get_dataset_overview")
        assert "CatBoost" in text


class TestGetColumnStatistics:
    def test_numeric_column(self):
        text = _call("get_column_statistics", {"column_name": "freight_value"})
        assert "numeric" in text
        assert "mean" in text

    def test_categorical_column(self):
        text = _call("get_column_statistics", {"column_name": "customer_state"})
        assert "categorical" in text
        assert "SP" in text

    def test_invalid_column_error(self):
        text = _call("get_column_statistics", {"column_name": "nonexistent"})
        assert "Error" in text


class TestGetDatasetSchema:
    def test_has_columns(self):
        text = _call("get_dataset_schema")
        assert "order_id" in text
        assert "foi_atraso" in text
        assert "valor_total_pedido" in text

    def test_has_groups(self):
        text = _call("get_dataset_schema")
        assert "Direct Columns" in text
        assert "Engineered Columns" in text


class TestSearchOrders:
    def test_valid_order(self):
        from olist_mcp.cache import DataStore
        df = DataStore.df()
        oid = df["order_id"].iloc[0]
        text = _call("search_orders_by_order_id", {"order_id": oid})
        assert "Order:" in text
        assert "Identification" in text
        assert "Location" in text

    def test_invalid_order(self):
        text = _call("search_orders_by_order_id", {"order_id": "fake_order_xyz"})
        assert "Error" in text or "not found" in text.lower()


class TestHaversineDistance:
    def test_sp_to_rj(self):
        text = _call("calculate_haversine_distance_tool", {
            "seller_lat": -23.55, "seller_lng": -46.63,
            "customer_lat": -22.91, "customer_lng": -43.17,
        })
        assert "km" in text
        assert "360" in text  # ~360 km
