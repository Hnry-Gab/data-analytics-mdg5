"""Error handling tests for the Olist MCP server.

Validates graceful degradation when:
- XGBoost model file (.pkl) is absent
- Invalid inputs are provided
- Edge cases are encountered
"""

import asyncio

from olist_mcp.cache import DataStore
from olist_mcp.server import mcp


def _call(tool_name: str, args: dict | None = None) -> str:
    result = asyncio.run(mcp.call_tool(tool_name, args or {}))
    return result.content[0].text


# ---------- Model Graceful Degradation ----------

class TestModelGracefulDegradation:
    """All model-dependent tools must degrade gracefully when .pkl is absent."""

    def test_model_is_absent(self):
        """Confirm model is actually absent in this environment."""
        assert DataStore.model() is None

    def test_get_model_status_degradation(self):
        text = _call("get_model_status")
        assert "Unavailable" in text
        assert "Alternative Tools" in text

    def test_predict_delay_degradation(self):
        """predict_delay_probability must return helpful message, not crash."""
        text = _call("predict_delay_probability", {
            "velocidade_lojista_dias": 5.0,
            "distancia_haversine_km": 500.0,
            "freight_value": 30.0,
            "rota_interestadual": 1,
            "customer_state_encoded": 0.10,
            "seller_state_encoded": 0.05,
        })
        assert "Unavailable" in text
        assert "Alternative" in text

    def test_simulate_seller_improvement_degradation(self):
        text = _call("simulate_seller_improvement", {
            "current_velocidade_dias": 7.0,
            "target_velocidade_dias": 3.0,
            "distancia_haversine_km": 500.0,
            "freight_value": 30.0,
            "rota_interestadual": 1,
            "customer_state_encoded": 0.10,
            "seller_state_encoded": 0.05,
        })
        assert "Unavailable" in text
        assert "Alternative" in text

    def test_feature_importance_falls_back_to_correlation(self):
        """Feature importance should use correlation proxy when model absent."""
        text = _call("get_feature_importance")
        assert "Correlation Proxy" in text or "Pearson" in text

    def test_hyperparameters_uses_spec_fallback(self):
        """Hyperparameters should use spec-defined values when model absent."""
        text = _call("get_model_hyperparameters")
        assert "model_spec.md" in text or "spec" in text.lower()
        assert "binary:logistic" in text

    def test_model_metrics_always_works(self):
        """Model metrics are hardcoded baselines — should always work."""
        text = _call("get_model_metrics")
        assert "0.7452" in text
        assert "ROC-AUC" in text

    def test_state_encoding_always_works(self):
        """State encoding is computed from data, not model — should always work."""
        text = _call("get_state_encoding_map")
        assert "AL" in text
        assert "SP" in text


# ---------- Invalid Input Handling ----------

class TestInvalidInputHandling:
    """Tools must handle invalid inputs gracefully without crashing."""

    def test_invalid_state_encoding(self):
        text = _call("get_state_encoding_map", {"state": "XX"})
        assert "Error" in text
        assert "Valid states" in text or "not found" in text.lower()

    def test_invalid_chart_name(self):
        text = _call("get_chart_as_base64", {"chart_name": "nonexistent_zzz"})
        assert "Error" in text
        assert "Available" in text.lower() or "correlacao" in text

    def test_invalid_html_chart_name(self):
        text = _call("get_html_chart_content", {"chart_name": "nonexistent"})
        assert "Error" in text

    def test_invalid_category(self):
        text = _call("get_category_deep_dive", {"category_name": "zzz_nothing_zzz"})
        assert "Error" in text

    def test_invalid_order_id(self):
        text = _call("search_orders_by_order_id", {"order_id": "fake_order_id_xyz"})
        assert "Error" in text or "not found" in text.lower()

    def test_invalid_state_comparison(self):
        text = _call("compare_two_states", {"state_a": "SP", "state_b": "XX"})
        assert "Error" in text

    def test_invalid_seller_ranking_metric(self):
        text = _call("get_seller_ranking", {"metric": "invalid_metric"})
        assert "Error" in text

    def test_invalid_chart_state_type(self):
        text = _call("generate_delay_by_state_chart", {"state_type": "invalid"})
        assert "Error" in text

    def test_invalid_timeseries_granularity(self):
        text = _call("generate_time_series_chart", {"granularity": "year"})
        assert "Error" in text

    def test_heatmap_impossible_min_orders(self):
        text = _call("generate_route_heatmap", {"min_orders": 99999999})
        assert "Error" in text

    def test_state_pair_below_min_orders(self):
        text = _call("get_orders_by_state_pair", {
            "seller_state": "AC",
            "customer_state": "AC",
            "min_orders": 100000,
        })
        assert "Error" in text

    def test_filter_no_match(self):
        text = _call("filter_orders", {
            "customer_state": "SP",
            "max_price": 0.001,
        })
        assert "No orders matched" in text or "0" in text


# ---------- Edge Cases ----------

class TestEdgeCases:
    """Edge cases that should not crash the server."""

    def test_empty_seller_ranking_state(self):
        """Filtering sellers by a rare state with high min_orders."""
        text = _call("get_seller_ranking", {
            "metric": "delay_rate",
            "state": "AC",
            "min_orders": 1000,
        })
        assert "Error" in text or "No sellers" in text

    def test_column_stats_nonexistent(self):
        """Requesting stats for a column that doesn't exist."""
        text = _call("get_column_statistics", {"column_name": "nonexistent_col"})
        assert "Error" in text or "not found" in text.lower() or "nonexistent" in text.lower()

    def test_worst_routes_top_1(self):
        """Edge case: requesting only top 1 worst route."""
        text = _call("get_worst_routes", {"top_n": 1})
        assert len(text) > 10  # Should return something valid

    def test_product_weight_custom_bins(self):
        """Custom bins with only 2 breakpoints."""
        text = _call("get_product_weight_analysis", {
            "weight_bins": [0, 5000, 100000],
        })
        assert "0-5000" in text

    def test_correlation_chart_high_threshold(self):
        """Filter correlations so high nothing matches — should still not crash."""
        text = _call("generate_correlation_bar_chart", {"min_abs_correlation": 0.99})
        # Either returns empty chart or an error message
        assert len(text) > 10

    def test_seasonal_analysis_year_filter(self):
        """Filter to a specific year."""
        text = _call("get_seasonal_analysis", {"year": 2017})
        assert "2017" in text or "Q" in text
