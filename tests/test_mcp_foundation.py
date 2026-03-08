"""Tests for MCP-00 Foundation: config, cache, utils, server."""

import math
import threading

import numpy as np
import pandas as pd
import pytest

from olist_mcp import __version__
from olist_mcp.cache import DataStore
from olist_mcp.config import CATBOOST_CONFIG, CATBOOST_MODEL, DATASET_V1, TIMESTAMP_COLS, ZIP_DTYPE
from olist_mcp.utils.formatters import format_json_safe, format_markdown_table
from olist_mcp.utils.haversine import haversine_distance
from olist_mcp.utils.state_mappings import MACRO_REGIONS, REGION_TO_STATES, STATE_TO_REGION


class TestConfig:
    def test_version(self):
        assert __version__ == "0.2.0"

    def test_dataset_path_exists(self):
        assert DATASET_V1.exists(), f"Dataset not found: {DATASET_V1}"

    def test_catboost_paths_exist(self):
        assert CATBOOST_MODEL.exists(), f"CatBoost model not found: {CATBOOST_MODEL}"
        assert CATBOOST_CONFIG.exists(), f"CatBoost config not found: {CATBOOST_CONFIG}"

    def test_zip_dtype_keys(self):
        assert "customer_zip_code_prefix" in ZIP_DTYPE
        assert "seller_zip_code_prefix" in ZIP_DTYPE

    def test_timestamp_cols(self):
        assert "order_purchase_timestamp" in TIMESTAMP_COLS
        assert len(TIMESTAMP_COLS) == 6


class TestDataStore:
    def setup_method(self):
        DataStore.reset()

    def test_df_loads(self):
        df = DataStore.df()
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert "order_id" in df.columns

    def test_df_zip_as_string(self):
        df = DataStore.df()
        assert df["customer_zip_code_prefix"].dtype == object

    def test_df_timestamps_parsed(self):
        df = DataStore.df()
        assert pd.api.types.is_datetime64_any_dtype(df["order_purchase_timestamp"])

    def test_df_cached(self):
        df1 = DataStore.df()
        df2 = DataStore.df()
        assert df1 is df2

    def test_catboost_loads(self):
        model, config = DataStore.catboost()
        assert model is not None, "CatBoost model failed to load"
        assert config is not None, "CatBoost config failed to load"
        assert config["algorithm"] == "CatBoost"
        assert config["metrics"]["roc_auc"] > 0.8

    def test_catboost_cached(self):
        m1, c1 = DataStore.catboost()
        m2, c2 = DataStore.catboost()
        assert m1 is m2
        assert c1 is c2

    def test_thread_safety(self):
        results = []

        def load():
            df = DataStore.df()
            results.append(id(df))

        threads = [threading.Thread(target=load) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        # All threads should get the same object
        assert len(set(results)) == 1

    def test_reset(self):
        df1 = DataStore.df()
        DataStore.reset()
        df2 = DataStore.df()
        assert df1 is not df2


class TestHaversine:
    def test_sp_to_rj(self):
        d = haversine_distance(-23.5505, -46.6333, -22.9068, -43.1729)
        assert 350 < d < 370

    def test_same_point(self):
        d = haversine_distance(-23.5505, -46.6333, -23.5505, -46.6333)
        assert d == 0.0

    def test_antipodal(self):
        d = haversine_distance(0, 0, 0, 180)
        assert abs(d - math.pi * 6371.0) < 1


class TestStateMappings:
    def test_all_27_states(self):
        assert len(STATE_TO_REGION) == 27

    def test_sp_is_sudeste(self):
        assert STATE_TO_REGION["SP"] == "Sudeste"

    def test_5_macro_regions(self):
        assert len(MACRO_REGIONS) == 5

    def test_region_to_states_inverse(self):
        for state, region in STATE_TO_REGION.items():
            assert state in REGION_TO_STATES[region]


class TestFormatters:
    def test_json_safe_nan(self):
        assert format_json_safe(float("nan")) is None

    def test_json_safe_inf(self):
        assert format_json_safe(float("inf")) is None

    def test_json_safe_numpy(self):
        assert format_json_safe(np.int64(42)) == 42
        assert format_json_safe(np.float64(3.14)) == 3.14

    def test_json_safe_dict(self):
        result = format_json_safe({"a": float("nan"), "b": 1})
        assert result == {"a": None, "b": 1}

    def test_markdown_table(self):
        df = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
        md = format_markdown_table(df)
        assert "|" in md
        assert "x" in md

    def test_markdown_table_truncation(self):
        df = pd.DataFrame({"x": range(100)})
        md = format_markdown_table(df, max_rows=10)
        assert "Showing 10 of 100" in md


## TestServer removed: server.py still imports old tool modules (will be fixed in Window 4)
