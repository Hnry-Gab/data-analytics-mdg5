"""Thread-safe DataStore singleton with lazy-loading."""

import threading
from typing import Optional

import joblib
import pandas as pd

from .config import (
    CORRELATIONS_CSV,
    DATASET_TREINO,
    DATASET_V1,
    MODEL_PKL,
    TIMESTAMP_COLS,
    ZIP_DTYPE,
)


class DataStore:
    """Singleton cache for datasets and model. Thread-safe with double-checked locking."""

    _lock = threading.Lock()
    _df: Optional[pd.DataFrame] = None
    _df_treino: Optional[pd.DataFrame] = None
    _correlations: Optional[pd.DataFrame] = None
    _model: Optional[object] = None
    _model_loaded: bool = False

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
    def df_treino(cls) -> pd.DataFrame:
        """Load and cache the training dataset."""
        if cls._df_treino is None:
            with cls._lock:
                if cls._df_treino is None:
                    cls._df_treino = pd.read_csv(DATASET_TREINO)
        return cls._df_treino

    @classmethod
    def correlations(cls) -> pd.DataFrame:
        """Load and cache the correlations summary table."""
        if cls._correlations is None:
            with cls._lock:
                if cls._correlations is None:
                    cls._correlations = pd.read_csv(CORRELATIONS_CSV)
        return cls._correlations

    @classmethod
    def model(cls) -> Optional[object]:
        """Load the XGBoost model. Returns None if file is missing (graceful degradation)."""
        if not cls._model_loaded:
            with cls._lock:
                if not cls._model_loaded:
                    try:
                        cls._model = joblib.load(MODEL_PKL)
                    except FileNotFoundError:
                        cls._model = None
                    cls._model_loaded = True
        return cls._model

    @classmethod
    def reset(cls) -> None:
        """Reset all cached data. Useful for testing."""
        with cls._lock:
            cls._df = None
            cls._df_treino = None
            cls._correlations = None
            cls._model = None
            cls._model_loaded = False
