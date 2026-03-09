"""Tests for MCP-02: CatBoost ML Tools (4 tools)."""

import asyncio

import pytest
from fastmcp import FastMCP

from olist_mcp.tools.catboost_ml import (
    _derive_features,
    _risk_level,
    register,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def mcp_server():
    mcp = FastMCP(name="test-catboost-ml")
    register(mcp)
    return mcp


def _call(mcp, tool_name: str, args: dict) -> str:
    result = asyncio.get_event_loop().run_until_complete(mcp.call_tool(tool_name, args))
    return result.content[0].text


# ---------------------------------------------------------------------------
# Helper tests
# ---------------------------------------------------------------------------

class TestDeriveFeatures:
    def test_basic(self):
        f = _derive_features(
            velocidade_lojista_dias=3.0, freight_value=25.0, price=100.0,
            product_weight_g=500.0, volume_cm3=3000.0, total_itens_pedido=1,
            seller_state="SP", customer_state="RJ", product_category_name="outros",
            distancia_haversine_km=None, prazo_estimado_dias=15,
            historico_atraso_vendedor=0.07, qtd_pedidos_anteriores_vendedor=50,
            mes_compra=6, dia_semana_compra=3,
        )
        assert f["rota"] == "SP-RJ"
        assert f["frete_por_kg"] == 50.0  # 25 / 0.5
        assert f["semana_ano"] == 24  # 6 * 4
        assert f["eh_alta_temporada"] == 0

    def test_high_season(self):
        f = _derive_features(
            velocidade_lojista_dias=3.0, freight_value=25.0, price=100.0,
            product_weight_g=500.0, volume_cm3=3000.0, total_itens_pedido=1,
            seller_state="SP", customer_state="SP", product_category_name="outros",
            distancia_haversine_km=100.0, prazo_estimado_dias=15,
            historico_atraso_vendedor=0.07, qtd_pedidos_anteriores_vendedor=50,
            mes_compra=11, dia_semana_compra=3,
        )
        assert f["eh_alta_temporada"] == 1

    def test_zero_weight(self):
        f = _derive_features(
            velocidade_lojista_dias=3.0, freight_value=25.0, price=100.0,
            product_weight_g=0, volume_cm3=3000.0, total_itens_pedido=1,
            seller_state="SP", customer_state="SP", product_category_name="outros",
            distancia_haversine_km=100.0, prazo_estimado_dias=15,
            historico_atraso_vendedor=0.07, qtd_pedidos_anteriores_vendedor=50,
            mes_compra=6, dia_semana_compra=3,
        )
        assert f["frete_por_kg"] == 0.0

    def test_defaults_for_none(self):
        f = _derive_features(
            velocidade_lojista_dias=3.0, freight_value=25.0, price=100.0,
            product_weight_g=500.0, volume_cm3=3000.0, total_itens_pedido=1,
            seller_state="SP", customer_state="SP", product_category_name="outros",
            distancia_haversine_km=None, prazo_estimado_dias=15,
            historico_atraso_vendedor=0.07, qtd_pedidos_anteriores_vendedor=50,
            mes_compra=None, dia_semana_compra=None,
        )
        assert f["distancia_haversine_km"] == 431.94
        assert isinstance(f["mes_compra"], int)
        assert isinstance(f["dia_semana_compra"], int)


class TestRiskLevel:
    def test_low(self):
        assert _risk_level(0.10) == "Low"

    def test_medium(self):
        assert _risk_level(0.45) == "Medium"

    def test_high(self):
        assert _risk_level(0.80) == "High"


# ---------------------------------------------------------------------------
# predict_delay_catboost
# ---------------------------------------------------------------------------

class TestPredictDelay:
    def test_basic_prediction(self, mcp_server):
        result = _call(mcp_server, "predict_delay_catboost", {
            "velocidade_lojista_dias": 3.0,
            "freight_value": 25.0,
            "price": 100.0,
            "product_weight_g": 500.0,
            "volume_cm3": 3000.0,
        })
        assert "Probability" in result
        assert "Classification" in result
        assert "Risk Level" in result

    def test_high_risk_prediction(self, mcp_server):
        result = _call(mcp_server, "predict_delay_catboost", {
            "velocidade_lojista_dias": 10.0,
            "freight_value": 50.0,
            "price": 500.0,
            "product_weight_g": 10000.0,
            "volume_cm3": 50000.0,
            "seller_state": "SP",
            "customer_state": "AM",
            "distancia_haversine_km": 3000.0,
        })
        assert "Probability" in result
        assert "Features Used" in result

    def test_custom_states(self, mcp_server):
        result = _call(mcp_server, "predict_delay_catboost", {
            "velocidade_lojista_dias": 2.0,
            "freight_value": 15.0,
            "price": 50.0,
            "product_weight_g": 200.0,
            "volume_cm3": 1000.0,
            "seller_state": "MG",
            "customer_state": "BA",
        })
        assert "MG-BA" in result


# ---------------------------------------------------------------------------
# get_catboost_model_info
# ---------------------------------------------------------------------------

class TestModelInfo:
    def test_returns_metrics(self, mcp_server):
        result = _call(mcp_server, "get_catboost_model_info", {})
        assert "ROC-AUC" in result
        assert "0.8454" in result

    def test_returns_hyperparams(self, mcp_server):
        result = _call(mcp_server, "get_catboost_model_info", {})
        assert "depth" in result
        assert "iterations" in result

    def test_returns_features(self, mcp_server):
        result = _call(mcp_server, "get_catboost_model_info", {})
        assert "velocidade_lojista_dias" in result
        assert "seller_state" in result


# ---------------------------------------------------------------------------
# get_catboost_feature_importance
# ---------------------------------------------------------------------------

class TestFeatureImportance:
    def test_returns_ranking(self, mcp_server):
        result = _call(mcp_server, "get_catboost_feature_importance", {"top_n": 5})
        assert "Rank" in result
        assert "Importance" in result
        assert "% of Total" in result

    def test_top_feature(self, mcp_server):
        result = _call(mcp_server, "get_catboost_feature_importance", {"top_n": 1})
        assert "velocidade_lojista_dias" in result


# ---------------------------------------------------------------------------
# simulate_scenario
# ---------------------------------------------------------------------------

class TestSimulateScenario:
    def test_velocity_sweep(self, mcp_server):
        result = _call(mcp_server, "simulate_scenario", {
            "vary_feature": "velocidade_lojista_dias",
            "vary_values": [1, 3, 5, 10],
        })
        assert "Simulation" in result
        assert "velocidade_lojista_dias" in result
        assert "|" in result

    def test_categorical_sweep(self, mcp_server):
        result = _call(mcp_server, "simulate_scenario", {
            "vary_feature": "customer_state",
            "vary_values": ["SP", "RJ", "AM"],
        })
        assert "customer_state" in result

    def test_empty_values(self, mcp_server):
        result = _call(mcp_server, "simulate_scenario", {
            "vary_feature": "price",
            "vary_values": [],
        })
        assert "Error" in result

    def test_invalid_feature(self, mcp_server):
        result = _call(mcp_server, "simulate_scenario", {
            "vary_feature": "nonexistent_feature",
            "vary_values": [1, 2, 3],
        })
        assert "Error" in result
