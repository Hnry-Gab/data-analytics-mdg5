"""Performance tests for MCP tools.

Validates that tools execute within acceptable time limits
with the dataset already cached in memory.
"""

import asyncio
import time

import pytest

from olist_mcp.cache import DataStore
from olist_mcp.server import mcp


@pytest.fixture(scope="module", autouse=True)
def _warm_cache():
    DataStore.df()


def _timed_call(tool_name: str, args: dict | None = None) -> tuple[str, float]:
    start = time.perf_counter()
    result = asyncio.run(mcp.call_tool(tool_name, args or {}))
    elapsed_ms = (time.perf_counter() - start) * 1000
    return result.content[0].text, elapsed_ms


NO_ARG_TOOLS = [
    "get_dataset_overview",
    "get_dataset_schema",
    "get_business_summary",
    "list_available_charts",
    "get_catboost_model_info",
]


class TestDataToolsPerformance:
    @pytest.mark.parametrize("tool_name", NO_ARG_TOOLS)
    def test_tool_under_500ms(self, tool_name):
        text, elapsed = _timed_call(tool_name)
        assert elapsed < 500, f"`{tool_name}` took {elapsed:.0f}ms (limit: 500ms)"
        assert len(text) > 0

    def test_dynamic_aggregate_under_500ms(self):
        _, elapsed = _timed_call("dynamic_aggregate", {"column": "price", "agg": "sum"})
        assert elapsed < 500

    def test_group_by_under_500ms(self):
        _, elapsed = _timed_call("group_by_metrics", {
            "group_by": "customer_state",
            "metrics": ["mean:foi_atraso"],
        })
        assert elapsed < 500

    def test_column_stats_under_500ms(self):
        _, elapsed = _timed_call("get_column_statistics", {"column_name": "price"})
        assert elapsed < 500


class TestChartGenerationPerformance:
    def test_delay_by_state_chart(self):
        _, elapsed = _timed_call("generate_delay_by_state_chart", {
            "state_type": "customer", "top_n": 5,
        })
        assert elapsed < 3000

    def test_correlation_bar_chart(self):
        _, elapsed = _timed_call("generate_correlation_bar_chart", {
            "min_abs_correlation": 0.05,
        })
        assert elapsed < 3000

    def test_time_series_chart(self):
        _, elapsed = _timed_call("generate_time_series_chart", {
            "granularity": "month",
        })
        assert elapsed < 3000
