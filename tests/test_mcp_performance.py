"""Performance tests for MCP tools.

Validates that all tools execute within acceptable time limits
with the dataset already cached in memory.

Thresholds:
- Data/analytics tools: <500ms (dataset cached)
- Chart generation tools (Plotly+Kaleido): <3000ms (image rendering)
"""

import asyncio
import time

import pytest

from olist_mcp.cache import DataStore
from olist_mcp.server import mcp


# Pre-warm caches before any test runs
@pytest.fixture(scope="module", autouse=True)
def _warm_cache():
    DataStore.df()
    DataStore.correlations()


def _timed_call(tool_name: str, args: dict | None = None) -> tuple[str, float]:
    """Call a tool and return (result_text, elapsed_ms)."""
    start = time.perf_counter()
    result = asyncio.run(mcp.call_tool(tool_name, args or {}))
    elapsed_ms = (time.perf_counter() - start) * 1000
    return result.content[0].text, elapsed_ms


# ---------- Tools with default/no args (<500ms threshold) ----------

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
    "get_feature_importance",
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


class TestDataToolsPerformance:
    """All data/analytics tools must complete in <500ms with cached dataset."""

    @pytest.mark.parametrize("tool_name", NO_ARG_TOOLS)
    def test_tool_under_500ms(self, tool_name):
        text, elapsed = _timed_call(tool_name)
        assert elapsed < 500, f"`{tool_name}` took {elapsed:.0f}ms (limit: 500ms)"
        assert len(text) > 0

    def test_filter_orders_under_500ms(self):
        _, elapsed = _timed_call("filter_orders", {"customer_state": "SP"})
        assert elapsed < 500

    def test_state_pair_under_500ms(self):
        _, elapsed = _timed_call("get_orders_by_state_pair", {
            "seller_state": "SP", "customer_state": "RJ",
        })
        assert elapsed < 500

    def test_category_dive_under_500ms(self):
        _, elapsed = _timed_call("get_category_deep_dive", {"category_name": "beleza"})
        assert elapsed < 500

    def test_compare_states_under_500ms(self):
        _, elapsed = _timed_call("compare_two_states", {"state_a": "SP", "state_b": "AL"})
        assert elapsed < 500

    def test_column_stats_under_500ms(self):
        _, elapsed = _timed_call("get_column_statistics", {"column_name": "price"})
        assert elapsed < 500

    def test_haversine_under_500ms(self):
        _, elapsed = _timed_call("calculate_haversine_distance", {
            "seller_lat": -23.55, "seller_lng": -46.63,
            "customer_lat": -22.91, "customer_lng": -43.17,
        })
        assert elapsed < 500

    def test_state_encoding_under_500ms(self):
        _, elapsed = _timed_call("get_state_encoding_map", {"state": "SP"})
        assert elapsed < 500

    def test_chart_base64_under_500ms(self):
        _, elapsed = _timed_call("get_chart_as_base64", {"chart_name": "correlacao"})
        assert elapsed < 500

    def test_worst_routes_under_500ms(self):
        _, elapsed = _timed_call("get_worst_routes", {"top_n": 5})
        assert elapsed < 500

    def test_orders_over_time_under_500ms(self):
        _, elapsed = _timed_call("get_orders_over_time")
        assert elapsed < 500


class TestChartGenerationPerformance:
    """Chart generation tools use Plotly+Kaleido — allowed up to 3000ms."""

    def test_delay_by_state_chart(self):
        _, elapsed = _timed_call("generate_delay_by_state_chart", {
            "state_type": "customer", "top_n": 5,
        })
        assert elapsed < 3000, f"delay_by_state took {elapsed:.0f}ms (limit: 3000ms)"

    def test_correlation_bar_chart(self):
        _, elapsed = _timed_call("generate_correlation_bar_chart", {
            "min_abs_correlation": 0.05,
        })
        assert elapsed < 3000, f"correlation_bar took {elapsed:.0f}ms (limit: 3000ms)"

    def test_route_heatmap(self):
        _, elapsed = _timed_call("generate_route_heatmap", {
            "min_orders": 100, "level": "state",
        })
        assert elapsed < 3000, f"route_heatmap took {elapsed:.0f}ms (limit: 3000ms)"

    def test_time_series_chart(self):
        _, elapsed = _timed_call("generate_time_series_chart", {
            "granularity": "month",
        })
        assert elapsed < 3000, f"time_series took {elapsed:.0f}ms (limit: 3000ms)"
