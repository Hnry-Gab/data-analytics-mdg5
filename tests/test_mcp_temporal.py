"""Tests for MCP-05: Temporal Analysis Tools."""

import asyncio

from olist_mcp.server import mcp


def _call(tool_name: str, args: dict | None = None) -> str:
    result = asyncio.run(mcp.call_tool(tool_name, args or {}))
    return result.content[0].text


class TestDelayRateByMonth:
    def test_peak_march(self):
        text = _call("get_delay_rate_by_month")
        assert "March" in text
        assert "14.50" in text

    def test_minimum_june(self):
        text = _call("get_delay_rate_by_month")
        assert "June" in text
        assert "1.75" in text


class TestDelayRateByWeekday:
    def test_weak_effect(self):
        text = _call("get_delay_rate_by_weekday")
        assert "weak" in text.lower()

    def test_all_days(self):
        text = _call("get_delay_rate_by_weekday")
        assert "Monday" in text
        assert "Sunday" in text


class TestOrdersOverTime:
    def test_monthly_granularity(self):
        text = _call("get_orders_over_time", {"granularity": "month"})
        assert "monthly" in text.lower() or "month" in text.lower()

    def test_date_filter(self):
        text = _call("get_orders_over_time", {
            "granularity": "month",
            "start_date": "2017-06-01",
            "end_date": "2017-12-31",
        })
        assert "2017" in text
        assert "2016" not in text.split("##")[-1]  # No 2016 in data table


class TestDateRange:
    def test_covers_2016_to_2018(self):
        text = _call("get_date_range")
        assert "2016" in text
        assert "2018" in text

    def test_purchase_and_delivery(self):
        text = _call("get_date_range")
        assert "Purchase" in text
        assert "Delivery" in text


class TestVelocidadeLojista:
    def test_pearson_value(self):
        text = _call("get_velocidade_lojista_distribution")
        assert "0.2143" in text

    def test_bins_present(self):
        text = _call("get_velocidade_lojista_distribution")
        assert "0-1" in text
        assert "14+" in text


class TestSeasonalAnalysis:
    def test_quarters(self):
        text = _call("get_seasonal_analysis")
        assert "Q1" in text
        assert "Q4" in text

    def test_year_filter(self):
        text = _call("get_seasonal_analysis", {"year": 2017})
        assert "2017" in text

    def test_anomalies(self):
        text = _call("get_seasonal_analysis")
        assert "November" in text or "December" in text
