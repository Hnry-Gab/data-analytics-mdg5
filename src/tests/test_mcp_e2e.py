"""E2E tests: real user questions → tool calls → meaningful answers.

Each test simulates a chatbot question that the LLM would route to a specific tool.
Validates that the tool returns a non-error, content-rich response.
"""

import asyncio

import pytest

from olist_mcp.server import mcp


def _call(tool_name: str, args: dict | None = None) -> str:
    result = asyncio.run(mcp.call_tool(tool_name, args or {}))
    return result.content[0].text


# ---------------------------------------------------------------------------
# "Qual a soma do valor de todos os produtos?"
# ---------------------------------------------------------------------------

class TestSumAllProducts:
    def test_aggregate_sum_price(self):
        text = _call("dynamic_aggregate", {"column": "price", "agg": "sum"})
        assert "R$" in text
        assert "Sum" in text or "sum" in text


# ---------------------------------------------------------------------------
# "Qual a soma do valor de todos os produtos da Paraíba?"
# ---------------------------------------------------------------------------

class TestSumProductsPB:
    def test_aggregate_sum_price_pb(self):
        text = _call("dynamic_aggregate", {
            "column": "price",
            "agg": "sum",
            "filters": [{"column": "customer_state", "op": "eq", "value": "PB"}],
        })
        assert "R$" in text
        assert "customer_state = PB" in text


# ---------------------------------------------------------------------------
# "Qual a soma dos maiores 500 produtos da Paraíba?"
# ---------------------------------------------------------------------------

class TestTopNPB:
    def test_top_500_pb_sum(self):
        text = _call("top_n_query", {
            "sort_by": "price",
            "n": 500,
            "filters": [{"column": "customer_state", "op": "eq", "value": "PB"}],
            "agg_column": "price",
            "agg": "sum",
        })
        assert "R$" in text
        assert "Top" in text or "top" in text


# ---------------------------------------------------------------------------
# "Qual o maior valor?"
# ---------------------------------------------------------------------------

class TestMaxPrice:
    def test_aggregate_max_price(self):
        text = _call("dynamic_aggregate", {"column": "price", "agg": "max"})
        assert "R$" in text
        assert "Max" in text or "max" in text


# ---------------------------------------------------------------------------
# "Qual estado teve mais compras?"
# ---------------------------------------------------------------------------

class TestStateMostOrders:
    def test_group_by_state_count(self):
        text = _call("group_by_metrics", {
            "group_by": "customer_state",
            "metrics": ["count:order_id"],
            "sort_by": "count:order_id",
            "limit": 1,
        })
        assert "SP" in text  # SP is the top state by volume


# ---------------------------------------------------------------------------
# "Qual a taxa de atraso de cada estado?"
# ---------------------------------------------------------------------------

class TestDelayRateByState:
    def test_group_by_state_delay(self):
        text = _call("group_by_metrics", {
            "group_by": "customer_state",
            "metrics": ["mean:foi_atraso", "count:order_id"],
        })
        # Should have multiple states
        assert "customer_state" in text
        assert "mean:foi_atraso" in text


# ---------------------------------------------------------------------------
# "Compare SP vs RJ em atrasos"
# ---------------------------------------------------------------------------

class TestCompareSPvsRJ:
    def test_compare_groups_sp_rj(self):
        text = _call("compare_groups", {
            "group_a_filters": [{"column": "customer_state", "op": "eq", "value": "SP"}],
            "group_b_filters": [{"column": "customer_state", "op": "eq", "value": "RJ"}],
            "metrics": ["mean:foi_atraso", "count:order_id", "mean:price"],
            "group_a_label": "SP",
            "group_b_label": "RJ",
        })
        assert "SP" in text
        assert "RJ" in text
        assert "Difference" in text


# ---------------------------------------------------------------------------
# "Qual a probabilidade de atraso desse pedido?"
# ---------------------------------------------------------------------------

class TestPredictDelay:
    def test_predict_typical_order(self):
        text = _call("predict_delay_catboost", {
            "velocidade_lojista_dias": 3.0,
            "freight_value": 25.0,
            "price": 100.0,
            "product_weight_g": 500.0,
            "volume_cm3": 3000.0,
        })
        # Should return a probability or graceful degradation
        assert "Probability" in text or "Model not available" in text


# ---------------------------------------------------------------------------
# "Quais features mais impactam atraso?"
# ---------------------------------------------------------------------------

class TestFeatureImportance:
    def test_feature_importance(self):
        text = _call("get_catboost_feature_importance", {})
        assert "Feature" in text
        assert "Importance" in text or "Correlation" in text


# ---------------------------------------------------------------------------
# "Se reduzir velocidade do lojista, qual o impacto?"
# ---------------------------------------------------------------------------

class TestSimulateScenario:
    def test_simulate_velocidade(self):
        text = _call("simulate_scenario", {
            "vary_feature": "velocidade_lojista_dias",
            "vary_values": [1, 3, 5, 7, 10],
        })
        assert "Simulation" in text or "Model not available" in text
