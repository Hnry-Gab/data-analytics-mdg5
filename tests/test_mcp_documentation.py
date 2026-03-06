"""Tests for MCP-06: Documentation Tools."""

import asyncio

import pytest

from olist_mcp.server import mcp


def _call(tool_name: str, args: dict | None = None) -> str:
    result = asyncio.run(mcp.call_tool(tool_name, args or {}))
    return result.content[0].text


class TestGetColumnDefinition:
    def test_engineered_column(self):
        text = _call("get_column_definition", {"column_name": "velocidade_lojista_dias"})
        assert "Engineered" in text
        assert "Fórmula" in text or "formula" in text.lower()

    def test_source_column(self):
        text = _call("get_column_definition", {"column_name": "order_id"})
        assert "Origem" in text
        assert "Pedidos" in text

    def test_invalid_column(self):
        text = _call("get_column_definition", {"column_name": "nonexistent"})
        assert "Error" in text


class TestGetDataDictionary:
    def test_section_customers(self):
        text = _call("get_data_dictionary", {"section": "customers"})
        assert "customer_id" in text
        assert "Clientes" in text

    def test_section_engineered(self):
        text = _call("get_data_dictionary", {"section": "engineered"})
        assert "velocidade_lojista_dias" in text
        assert "distancia_haversine_km" in text

    def test_section_all(self):
        text = _call("get_data_dictionary", {"section": "all"})
        assert "Clientes" in text
        assert "Engineered" in text

    def test_invalid_section(self):
        text = _call("get_data_dictionary", {"section": "invalid"})
        assert "Error" in text


class TestDocFileTools:
    def test_project_spec(self):
        text = _call("get_project_spec")
        assert "Olist" in text
        assert len(text) > 500

    def test_model_spec(self):
        text = _call("get_model_spec")
        assert "XGBoost" in text
        assert "ROC-AUC" in text or "roc_auc" in text.lower()

    def test_feature_engineering_plan(self):
        text = _call("get_feature_engineering_plan")
        assert "Feature Engineering" in text

    def test_viability_report(self):
        text = _call("get_viability_report")
        assert "Viabilidade" in text or "viabilidade" in text

    def test_eda_report(self):
        text = _call("get_eda_report")
        assert "EDA" in text or "Relatório" in text


class TestGetTaskDetails:
    def test_valid_task(self):
        text = _call("get_task_details", {"task_id": "ALPHA-01"})
        assert "ALPHA-01" in text
        assert "Merge" in text or "merge" in text.lower()

    def test_invalid_format(self):
        text = _call("get_task_details", {"task_id": "INVALID"})
        assert "Error" in text
        assert "ALPHA" in text  # suggests valid formats


class TestListAllTasks:
    def test_all_squads(self):
        text = _call("list_all_tasks")
        assert "ALPHA" in text
        assert "DELTA" in text
        assert "OMEGA" in text

    def test_filter_squad(self):
        text = _call("list_all_tasks", {"squad": "delta"})
        assert "DELTA" in text
        assert "ALPHA-" not in text

    def test_invalid_squad(self):
        text = _call("list_all_tasks", {"squad": "invalid"})
        assert "Error" in text


class TestGetAlgorithmExplanation:
    def test_xgboost(self):
        text = _call("get_algorithm_explanation", {"algorithm": "xgboost"})
        assert "XGBoost" in text
        assert "árvore" in text.lower() or "tree" in text.lower()

    def test_pearson(self):
        text = _call("get_algorithm_explanation", {"algorithm": "pearson"})
        assert "Pearson" in text

    def test_invalid_algorithm(self):
        text = _call("get_algorithm_explanation", {"algorithm": "invalid"})
        assert "Error" in text


class TestGetStackInfo:
    def test_returns_stack(self):
        text = _call("get_stack_info")
        assert "Python" in text
        assert "requirements.txt" in text or "pandas" in text
