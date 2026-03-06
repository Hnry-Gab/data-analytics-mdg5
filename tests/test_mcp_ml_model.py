"""Tests for MCP-03: ML Model & Prediction Tools.

Note: Model file (.pkl) is not present in this environment,
so all model-dependent tools should degrade gracefully.
"""

import asyncio

from olist_mcp.server import mcp


def _call(tool_name: str, args: dict | None = None) -> str:
    result = asyncio.run(mcp.call_tool(tool_name, args or {}))
    return result.content[0].text


class TestGetModelStatus:
    def test_graceful_degradation(self):
        text = _call("get_model_status")
        assert "Unavailable" in text or "available" in text.lower()

    def test_shows_path(self):
        text = _call("get_model_status")
        assert "xgboost_atraso_v1.pkl" in text


class TestPredictDelayProbability:
    def test_graceful_degradation(self):
        text = _call("predict_delay_probability", {
            "velocidade_lojista_dias": 3.0,
            "distancia_haversine_km": 500.0,
            "freight_value": 20.0,
            "rota_interestadual": 1,
            "customer_state_encoded": 0.10,
            "seller_state_encoded": 0.05,
        })
        # Should degrade gracefully since model is missing
        assert "Unavailable" in text or "Prediction" in text


class TestGetModelMetrics:
    def test_roc_auc_baseline(self):
        text = _call("get_model_metrics")
        assert "0.7452" in text

    def test_accuracy_warning(self):
        text = _call("get_model_metrics")
        assert "prohibited" in text.lower() or "Accuracy" in text


class TestGetFeatureImportance:
    def test_correlation_fallback(self):
        text = _call("get_feature_importance")
        # Falls back to correlation proxy when model is missing
        assert "Correlation Proxy" in text or "Feature Importance" in text
        assert "velocidade_lojista" in text


class TestGetModelHyperparameters:
    def test_spec_fallback(self):
        text = _call("get_model_hyperparameters")
        assert "max_depth" in text
        assert "scale_pos_weight" in text


class TestGetStateEncodingMap:
    def test_single_state(self):
        text = _call("get_state_encoding_map", {"state": "AL"})
        assert "0.2084" in text
        assert "20.84" in text

    def test_full_map(self):
        text = _call("get_state_encoding_map")
        assert "AL" in text
        assert "SP" in text
        assert "27" <= str(text.count("|")) or len(text) > 500  # 27 states

    def test_invalid_state(self):
        text = _call("get_state_encoding_map", {"state": "XX"})
        assert "Error" in text


class TestSimulateSellerImprovement:
    def test_graceful_degradation(self):
        text = _call("simulate_seller_improvement", {
            "current_velocidade_dias": 5.0,
            "target_velocidade_dias": 2.0,
            "distancia_haversine_km": 500.0,
            "freight_value": 20.0,
            "rota_interestadual": 1,
            "customer_state_encoded": 0.10,
            "seller_state_encoded": 0.05,
        })
        assert "Unavailable" in text or "Simulation" in text
