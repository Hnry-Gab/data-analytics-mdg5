"""Output formatting utilities for MCP tool responses."""

import json
import math
from typing import Any

import numpy as np
import pandas as pd


def format_markdown_table(df: pd.DataFrame, max_rows: int = 50) -> str:
    """Convert a DataFrame to a markdown table string.

    Args:
        df: DataFrame to convert.
        max_rows: Maximum rows to include. If exceeded, shows first max_rows with a note.

    Returns:
        Markdown-formatted table string.
    """
    if len(df) > max_rows:
        table = df.head(max_rows).to_markdown(index=False)
        return f"{table}\n\n*Showing {max_rows} of {len(df)} rows.*"
    return df.to_markdown(index=False)


def _sanitize_value(v: Any) -> Any:
    """Make a single value JSON-safe (handle NaN, Inf, numpy types)."""
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v) if not (math.isnan(v) or math.isinf(v)) else None
    if isinstance(v, np.bool_):
        return bool(v)
    if isinstance(v, (np.ndarray,)):
        return v.tolist()
    if isinstance(v, pd.Timestamp):
        return v.isoformat()
    return v


def format_json_safe(obj: Any) -> dict | list | str:
    """Serialize an object to a JSON-safe structure.

    Handles NaN, Inf, numpy types, and Timestamps.
    """
    if isinstance(obj, dict):
        return {k: format_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [format_json_safe(v) for v in obj]
    if isinstance(obj, pd.DataFrame):
        return json.loads(obj.to_json(orient="records", date_format="iso"))
    if isinstance(obj, pd.Series):
        return json.loads(obj.to_json(date_format="iso"))
    return _sanitize_value(obj)
