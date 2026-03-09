"""Thread-safe DataStore singleton with lazy-loading."""

import json
import threading
from typing import Optional

import pandas as pd

from .config import (
    CATBOOST_CONFIG,
    CATBOOST_MODEL,
    DATASET_V1,
    TIMESTAMP_COLS,
    ZIP_DTYPE,
)


class DataStore:
    """Singleton cache for dataset and CatBoost model. Thread-safe with double-checked locking."""

    _lock = threading.Lock()
    _df: Optional[pd.DataFrame] = None
    _catboost_model: Optional[object] = None
    _catboost_config: Optional[dict] = None
    _catboost_loaded: bool = False

    @classmethod
    def df(cls) -> pd.DataFrame:
        """Load and cache the main unified dataset."""
        if cls._df is None:
            with cls._lock:
                if cls._df is None:
                    cls._df = pd.read_csv(
                        DATASET_V1,
                        dtype=ZIP_DTYPE,
                        parse_dates=TIMESTAMP_COLS,
                    )
        return cls._df

    @classmethod
    def catboost(cls) -> tuple:
        """Load CatBoost model + config. Returns (model, config) or (None, None) on failure."""
        if not cls._catboost_loaded:
            with cls._lock:
                if not cls._catboost_loaded:
                    try:
                        from catboost import CatBoostClassifier

                        model = CatBoostClassifier()
                        model.load_model(str(CATBOOST_MODEL))
                        with open(CATBOOST_CONFIG, "r") as f:
                            config = json.load(f)
                        cls._catboost_model = model
                        cls._catboost_config = config
                    except (FileNotFoundError, Exception):
                        cls._catboost_model = None
                        cls._catboost_config = None
                    cls._catboost_loaded = True
        return cls._catboost_model, cls._catboost_config

    @classmethod
    def reset(cls) -> None:
        """Reset all cached data. Useful for testing."""
        with cls._lock:
            cls._df = None
            cls._catboost_model = None
            cls._catboost_config = None
            cls._catboost_loaded = False
