"""Tests for MCP-01: Dynamic Query Tools (4 tools + helpers)."""

import asyncio

import pandas as pd
import pytest
from fastmcp import FastMCP

from olist_mcp.tools.dynamic_query import (
    _apply_filters,
    _format_number,
    _parse_metric,
    register,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def mcp_server():
    mcp = FastMCP(name="test-dynamic-query")
    register(mcp)
    return mcp


def _call(mcp, tool_name: str, args: dict) -> str:
    """Helper to call a tool and return the text content."""
    result = asyncio.get_event_loop().run_until_complete(mcp.call_tool(tool_name, args))
    return result.content[0].text


# ---------------------------------------------------------------------------
# _apply_filters tests
# ---------------------------------------------------------------------------

class TestApplyFilters:
    def test_no_filters(self):
        df = pd.DataFrame({"a": [1, 2, 3]})
        result, descs = _apply_filters(df, None)
        assert len(result) == 3
        assert descs == []

    def test_empty_filters(self):
        df = pd.DataFrame({"a": [1, 2, 3]})
        result, descs = _apply_filters(df, [])
        assert len(result) == 3

    def test_eq(self):
        df = pd.DataFrame({"state": ["SP", "RJ", "SP"]})
        result, descs = _apply_filters(df, [{"column": "state", "op": "eq", "value": "SP"}])
        assert len(result) == 2
        assert "state = SP" in descs[0]

    def test_neq(self):
        df = pd.DataFrame({"state": ["SP", "RJ", "SP"]})
        result, _ = _apply_filters(df, [{"column": "state", "op": "neq", "value": "SP"}])
        assert len(result) == 1

    def test_gt(self):
        df = pd.DataFrame({"price": [10, 20, 30]})
        result, _ = _apply_filters(df, [{"column": "price", "op": "gt", "value": 15}])
        assert len(result) == 2

    def test_gte(self):
        df = pd.DataFrame({"price": [10, 20, 30]})
        result, _ = _apply_filters(df, [{"column": "price", "op": "gte", "value": 20}])
        assert len(result) == 2

    def test_lt(self):
        df = pd.DataFrame({"price": [10, 20, 30]})
        result, _ = _apply_filters(df, [{"column": "price", "op": "lt", "value": 25}])
        assert len(result) == 2

    def test_lte(self):
        df = pd.DataFrame({"price": [10, 20, 30]})
        result, _ = _apply_filters(df, [{"column": "price", "op": "lte", "value": 20}])
        assert len(result) == 2

    def test_contains(self):
        df = pd.DataFrame({"city": ["São Paulo", "Rio de Janeiro", "São José"]})
        result, _ = _apply_filters(df, [{"column": "city", "op": "contains", "value": "São"}])
        assert len(result) == 2

    def test_in(self):
        df = pd.DataFrame({"state": ["SP", "RJ", "MG", "BA"]})
        result, _ = _apply_filters(df, [{"column": "state", "op": "in", "value": ["SP", "RJ"]}])
        assert len(result) == 2

    def test_notnull(self):
        df = pd.DataFrame({"x": [1, None, 3]})
        result, _ = _apply_filters(df, [{"column": "x", "op": "notnull"}])
        assert len(result) == 2

    def test_invalid_column(self):
        df = pd.DataFrame({"a": [1]})
        with pytest.raises(ValueError, match="not found"):
            _apply_filters(df, [{"column": "zzz", "op": "eq", "value": 1}])

    def test_invalid_op(self):
        df = pd.DataFrame({"a": [1]})
        with pytest.raises(ValueError, match="Invalid operator"):
            _apply_filters(df, [{"column": "a", "op": "like", "value": 1}])

    def test_col_alias(self):
        """Accept 'col' as alias for 'column'."""
        df = pd.DataFrame({"state": ["SP", "RJ"]})
        result, _ = _apply_filters(df, [{"col": "state", "op": "eq", "value": "SP"}])
        assert len(result) == 1


# ---------------------------------------------------------------------------
# _parse_metric tests
# ---------------------------------------------------------------------------

class TestParseMetric:
    def test_valid(self):
        assert _parse_metric("mean:price") == ("mean", "price")
        assert _parse_metric("sum:freight_value") == ("sum", "freight_value")

    def test_invalid_format(self):
        with pytest.raises(ValueError, match="Invalid metric format"):
            _parse_metric("mean_price")

    def test_invalid_agg(self):
        with pytest.raises(ValueError, match="Invalid aggregation"):
            _parse_metric("average:price")


# ---------------------------------------------------------------------------
# _format_number tests
# ---------------------------------------------------------------------------

class TestFormatNumber:
    def test_money(self):
        assert "R$" in _format_number(123.45, "price")

    def test_rate(self):
        assert "%" in _format_number(0.0677, "foi_atraso")

    def test_distance(self):
        assert "km" in _format_number(350.0, "distancia_haversine_km")

    def test_days(self):
        assert "days" in _format_number(3.5, "dias_diferenca")

    def test_nan(self):
        assert _format_number(float("nan")) == "N/A"

    def test_integer(self):
        assert "1,000" in _format_number(1000)


# ---------------------------------------------------------------------------
# dynamic_aggregate tests
# ---------------------------------------------------------------------------

class TestDynamicAggregate:
    def test_sum_price(self, mcp_server):
        result = _call(mcp_server, "dynamic_aggregate", {"column": "price", "agg": "sum"})
        assert "R$" in result
        assert "Sum" in result

    def test_mean_with_filter(self, mcp_server):
        result = _call(mcp_server, "dynamic_aggregate", {
            "column": "price",
            "agg": "mean",
            "filters": [{"column": "customer_state", "op": "eq", "value": "SP"}],
        })
        assert "R$" in result
        assert "customer_state = SP" in result

    def test_count(self, mcp_server):
        result = _call(mcp_server, "dynamic_aggregate", {"column": "order_id", "agg": "count"})
        assert "Count" in result
        assert "109" in result  # ~109K rows

    def test_nunique(self, mcp_server):
        result = _call(mcp_server, "dynamic_aggregate", {"column": "customer_state", "agg": "nunique"})
        assert "Nunique" in result

    def test_value_counts(self, mcp_server):
        result = _call(mcp_server, "dynamic_aggregate", {"column": "customer_state", "agg": "value_counts", "limit": 5})
        assert "Value Counts" in result
        assert "SP" in result

    def test_invalid_column(self, mcp_server):
        result = _call(mcp_server, "dynamic_aggregate", {"column": "nonexistent", "agg": "sum"})
        assert "Error" in result

    def test_invalid_agg(self, mcp_server):
        result = _call(mcp_server, "dynamic_aggregate", {"column": "price", "agg": "average"})
        assert "Error" in result


# ---------------------------------------------------------------------------
# group_by_metrics tests
# ---------------------------------------------------------------------------

class TestGroupByMetrics:
    def test_by_state(self, mcp_server):
        result = _call(mcp_server, "group_by_metrics", {
            "group_by": "customer_state",
            "metrics": ["mean:foi_atraso", "count:order_id"],
        })
        assert "SP" in result
        assert "Group By" in result

    def test_with_sort_limit(self, mcp_server):
        result = _call(mcp_server, "group_by_metrics", {
            "group_by": "customer_state",
            "metrics": ["count:order_id"],
            "sort_by": "count:order_id",
            "limit": 3,
        })
        assert "Group By" in result
        # Should only have ~3 data rows (plus header)
        lines = [l for l in result.split("\n") if "|" in l]
        assert len(lines) <= 5  # header + separator + 3 data rows

    def test_min_count(self, mcp_server):
        result = _call(mcp_server, "group_by_metrics", {
            "group_by": "product_category_name",
            "metrics": ["mean:foi_atraso"],
            "min_count": 1000,
            "sort_by": "mean:foi_atraso",
            "sort_order": "desc",
            "limit": 5,
        })
        assert "min_count=1000" in result

    def test_invalid_group_column(self, mcp_server):
        result = _call(mcp_server, "group_by_metrics", {
            "group_by": "nonexistent",
            "metrics": ["count:order_id"],
        })
        assert "Error" in result

    def test_invalid_metric(self, mcp_server):
        result = _call(mcp_server, "group_by_metrics", {
            "group_by": "customer_state",
            "metrics": ["bad_format"],
        })
        assert "Error" in result


# ---------------------------------------------------------------------------
# top_n_query tests
# ---------------------------------------------------------------------------

class TestTopNQuery:
    def test_top_10_price(self, mcp_server):
        result = _call(mcp_server, "top_n_query", {"sort_by": "price", "n": 10})
        assert "Top 10" in result
        assert "|" in result

    def test_with_agg(self, mcp_server):
        result = _call(mcp_server, "top_n_query", {
            "sort_by": "price",
            "n": 100,
            "filters": [{"column": "customer_state", "op": "eq", "value": "PB"}],
            "agg_column": "price",
            "agg": "sum",
        })
        assert "R$" in result
        assert "customer_state = PB" in result

    def test_bottom_n(self, mcp_server):
        result = _call(mcp_server, "top_n_query", {
            "sort_by": "freight_value",
            "n": 5,
            "sort_order": "asc",
        })
        assert "Bottom 5" in result

    def test_custom_columns(self, mcp_server):
        result = _call(mcp_server, "top_n_query", {
            "sort_by": "price",
            "n": 5,
            "columns": ["order_id", "price", "customer_state"],
        })
        assert "order_id" in result
        assert "customer_state" in result

    def test_n_capped(self, mcp_server):
        result = _call(mcp_server, "top_n_query", {"sort_by": "price", "n": 9999})
        assert "Top 500" in result

    def test_invalid_sort_column(self, mcp_server):
        result = _call(mcp_server, "top_n_query", {"sort_by": "nonexistent"})
        assert "Error" in result


# ---------------------------------------------------------------------------
# compare_groups tests
# ---------------------------------------------------------------------------

class TestCompareGroups:
    def test_sp_vs_rj(self, mcp_server):
        result = _call(mcp_server, "compare_groups", {
            "group_a_filters": [{"column": "customer_state", "op": "eq", "value": "SP"}],
            "group_b_filters": [{"column": "customer_state", "op": "eq", "value": "RJ"}],
            "metrics": ["mean:foi_atraso", "count:order_id", "mean:price"],
            "group_a_label": "SP",
            "group_b_label": "RJ",
        })
        assert "SP" in result
        assert "RJ" in result
        assert "Comparison" in result
        assert "Difference" in result

    def test_interstate_vs_intrastate(self, mcp_server):
        result = _call(mcp_server, "compare_groups", {
            "group_a_filters": [{"column": "rota_interestadual", "op": "eq", "value": 1}],
            "group_b_filters": [{"column": "rota_interestadual", "op": "eq", "value": 0}],
            "metrics": ["mean:foi_atraso"],
            "group_a_label": "Interstate",
            "group_b_label": "Intrastate",
        })
        assert "Interstate" in result
        assert "Intrastate" in result

    def test_empty_group(self, mcp_server):
        result = _call(mcp_server, "compare_groups", {
            "group_a_filters": [{"column": "customer_state", "op": "eq", "value": "ZZ"}],
            "group_b_filters": [{"column": "customer_state", "op": "eq", "value": "SP"}],
            "metrics": ["mean:price"],
        })
        assert "Error" in result
