"""Tests for MCP-01: Dataset Statistics Tools."""

import asyncio

import pytest

from olist_mcp.server import mcp


def _call(tool_name: str, args: dict | None = None) -> str:
    """Helper to call an MCP tool synchronously and return its text."""
    result = asyncio.run(mcp.call_tool(tool_name, args or {}))
    return result.content[0].text


class TestGetDatasetOverview:
    def test_returns_markdown(self):
        text = _call("get_dataset_overview")
        assert "## Dataset Overview" in text

    def test_contains_dimensions(self):
        text = _call("get_dataset_overview")
        assert "110,189" in text
        assert "41 columns" in text

    def test_contains_target_distribution(self):
        text = _call("get_dataset_overview")
        assert "foi_atraso" in text
        assert "on time" in text.lower() or "On time" in text
        assert "delayed" in text.lower() or "Delayed" in text

    def test_contains_unique_counts(self):
        text = _call("get_dataset_overview")
        assert "Sellers" in text
        assert "Products" in text


class TestGetColumnStatistics:
    def test_numeric_column(self):
        text = _call("get_column_statistics", {"column_name": "freight_value"})
        assert "numeric" in text
        assert "mean" in text
        assert "std" in text

    def test_categorical_column(self):
        text = _call("get_column_statistics", {"column_name": "customer_state"})
        assert "categorical" in text
        assert "SP" in text  # most common state

    def test_invalid_column_error(self):
        text = _call("get_column_statistics", {"column_name": "nonexistent"})
        assert "Error" in text
        assert "not found" in text
        assert "order_id" in text  # suggests available columns


class TestGetClassDistribution:
    def test_returns_target_info(self):
        text = _call("get_class_distribution")
        assert "foi_atraso" in text
        assert "scale_pos_weight" in text

    def test_accuracy_warning(self):
        text = _call("get_class_distribution")
        assert "prohibited" in text.lower() or "Accuracy" in text


class TestGetCorrelationTable:
    def test_default_sort(self):
        text = _call("get_correlation_table")
        assert "velocidade_lojista" in text  # strongest feature

    def test_min_correlation_filter(self):
        text = _call("get_correlation_table", {"min_correlation": 0.1})
        assert "velocidade_lojista" in text
        # Weak features should be filtered out
        assert "dia_semana_compra" not in text

    def test_empty_filter(self):
        text = _call("get_correlation_table", {"min_correlation": 0.99})
        assert "No features" in text


class TestGetDatasetSchema:
    def test_has_all_columns(self):
        text = _call("get_dataset_schema")
        assert "41" in text
        assert "order_id" in text
        assert "foi_atraso" in text
        assert "distancia_haversine_km" in text

    def test_has_groups(self):
        text = _call("get_dataset_schema")
        assert "Direct Columns" in text
        assert "Engineered Columns" in text


class TestGetTrainingDatasetInfo:
    def test_returns_training_info(self):
        text = _call("get_training_dataset_info")
        assert "Training Dataset" in text
        assert "7 columns" in text

    def test_mentions_encoding(self):
        text = _call("get_training_dataset_info")
        assert "encoding" in text.lower() or "Encoding" in text
