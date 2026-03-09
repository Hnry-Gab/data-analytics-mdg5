"""MCP-01: Dynamic Query Tools (5 tools).

Gives the LLM full control over the dataset via parametrized
aggregate, group-by, top-N, and compare operations with arbitrary filters.
Also supports batch execution of multiple queries.
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd
from fastmcp import FastMCP

from olist_mcp.cache import DataStore

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_VALID_OPS = {"eq", "neq", "gt", "gte", "lt", "lte", "contains", "in", "notnull"}
_VALID_AGGS = {"mean", "sum", "count", "min", "max", "median", "std", "nunique", "value_counts"}
_MAX_DISPLAY_ROWS = 50

_MONEY_COLS = {"price", "freight_value", "valor_total_pedido"}
_RATE_COLS = {"foi_atraso", "frete_ratio", "historico_atraso_seller", "ticket_medio_alto", "compra_fds", "rota_interestadual"}
_DISTANCE_COLS = {"distancia_haversine_km"}
_DAYS_COLS = {"dias_diferenca", "velocidade_lojista_dias", "velocidade_transportadora_dias"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _apply_filters(df: pd.DataFrame, filters: list[dict] | None) -> tuple[pd.DataFrame, list[str]]:
    """Apply a list of filter dicts to a DataFrame.

    Returns (filtered_df, list of human-readable descriptions).
    """
    if not filters:
        return df, []

    descriptions: list[str] = []
    for f in filters:
        col = f.get("column") if f.get("column") is not None else f.get("col")
        op = f.get("op", "eq")
        val = f.get("value") if f.get("value") is not None else f.get("val")

        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found. Available: {sorted(df.columns.tolist())}")

        if op not in _VALID_OPS:
            raise ValueError(f"Invalid operator '{op}'. Use one of: {sorted(_VALID_OPS)}")

        if op == "eq":
            df = df[df[col] == val]
            descriptions.append(f"{col} = {val}")
        elif op == "neq":
            df = df[df[col] != val]
            descriptions.append(f"{col} ≠ {val}")
        elif op == "gt":
            df = df[df[col] > val]
            descriptions.append(f"{col} > {val}")
        elif op == "gte":
            df = df[df[col] >= val]
            descriptions.append(f"{col} ≥ {val}")
        elif op == "lt":
            df = df[df[col] < val]
            descriptions.append(f"{col} < {val}")
        elif op == "lte":
            df = df[df[col] <= val]
            descriptions.append(f"{col} ≤ {val}")
        elif op == "contains":
            df = df[df[col].astype(str).str.contains(str(val), case=False, na=False)]
            descriptions.append(f"{col} contains '{val}'")
        elif op == "in":
            if not isinstance(val, list):
                val = [val]
            df = df[df[col].isin(val)]
            descriptions.append(f"{col} in {val}")
        elif op == "notnull":
            df = df[df[col].notna()]
            descriptions.append(f"{col} is not null")

    return df, descriptions


def _parse_metric(metric_str: str) -> tuple[str, str]:
    """Parse 'agg:column' into (agg_name, column_name)."""
    parts = metric_str.split(":", 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid metric format '{metric_str}'. Use 'agg:column' (e.g. 'mean:price').")
    agg, col = parts
    if agg not in _VALID_AGGS:
        raise ValueError(f"Invalid aggregation '{agg}'. Use one of: {sorted(_VALID_AGGS)}")
    return agg, col


def _format_number(value: Any, column_name: str = "") -> str:
    """Format a number with type-aware context."""
    if pd.isna(value):
        return "N/A"
    if isinstance(value, (int,)):
        return f"{value:,}"
    if not isinstance(value, (float, int)):
        return str(value)

    col_lower = column_name.lower()
    if column_name in _MONEY_COLS or "price" in col_lower or "valor" in col_lower:
        return f"R$ {value:,.2f}"
    if column_name in _RATE_COLS:
        return f"{value:.2%}" if abs(value) <= 1 else f"{value:,.4f}"
    if column_name in _DISTANCE_COLS or "km" in col_lower:
        return f"{value:,.1f} km"
    if column_name in _DAYS_COLS or "dias" in col_lower:
        return f"{value:,.2f} days"
    if isinstance(value, float):
        return f"{value:,.4f}" if abs(value) < 1 else f"{value:,.2f}"
    return f"{value:,}"


def _filters_summary(descriptions: list[str], n_filtered: int, n_total: int) -> str:
    """Build a markdown summary of applied filters."""
    if not descriptions:
        return f"**Rows:** {n_total:,}\n"
    lines = [f"**Filters:** {', '.join(descriptions)}"]
    lines.append(f"**Rows:** {n_filtered:,} of {n_total:,}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Business Logic (Internal)
# ---------------------------------------------------------------------------


def _run_aggregate(
    column: str,
    agg: str = "mean",
    filters: list[dict] | None = None,
    limit: int | None = None,
) -> str:
    df = DataStore.df()
    n_total = len(df)

    if column not in df.columns:
        return f"**Error:** Column '{column}' not found."

    try:
        df_f, descs = _apply_filters(df, filters)
    except ValueError as e:
        return f"**Error:** {e}"

    if agg not in _VALID_AGGS:
        return f"**Error:** Invalid aggregation '{agg}'."

    n_filtered = len(df_f)
    if n_filtered == 0:
        return f"**No results.** Filters removed all rows.\n\n{_filters_summary(descs, 0, n_total)}"

    header = _filters_summary(descs, n_filtered, n_total)

    if agg == "value_counts":
        vc = df_f[column].value_counts()
        if limit:
            vc = vc.head(limit)
        result_df = vc.reset_index()
        result_df.columns = [column, "count"]
        table = result_df.head(_MAX_DISPLAY_ROWS).to_markdown(index=False)
        shown = min(len(result_df), _MAX_DISPLAY_ROWS)
        total_unique = len(vc)
        trunc = f"\n\n*Showing {shown} of {total_unique} unique values.*" if shown < total_unique else ""
        return f"### Value Counts: `{column}`\n\n{header}\n{table}{trunc}"

    series = df_f[column]
    result = getattr(series, agg)()
    formatted = _format_number(result, column)

    return f"### {agg.capitalize()}: `{column}`\n\n{header}\n**Result:** {formatted}"


def _run_group_by(
    group_by: str,
    metrics: list[str],
    filters: list[dict] | None = None,
    sort_by: str | None = None,
    sort_order: str = "desc",
    limit: int | None = None,
    min_count: int = 1,
) -> str:
    df = DataStore.df()
    n_total = len(df)

    if group_by not in df.columns:
        return f"**Error:** Column '{group_by}' not found."

    try:
        df_f, descs = _apply_filters(df, filters)
    except ValueError as e:
        return f"**Error:** {e}"

    n_filtered = len(df_f)
    if n_filtered == 0:
        return f"**No results.** Filters removed all rows.\n\n{_filters_summary(descs, 0, n_total)}"

    # Parse and validate metrics
    parsed_metrics: list[tuple[str, str]] = []
    for m in metrics:
        try:
            agg_name, col_name = _parse_metric(m)
        except ValueError as e:
            return f"**Error:** {e}"
        if col_name not in df.columns:
            return f"**Error:** Column '{col_name}' not found in metric '{m}'."
        parsed_metrics.append((agg_name, col_name))

    # Build aggregation dict
    agg_dict: dict[str, list] = {}
    for agg_name, col_name in parsed_metrics:
        agg_dict.setdefault(col_name, []).append(agg_name)

    grouped = df_f.groupby(group_by, observed=True).agg(agg_dict)
    grouped.columns = [f"{agg}:{col}" for col, agg in grouped.columns]
    grouped = grouped.reset_index()

    if min_count > 1:
        count_col = next((f"count:{c}" for a, c in parsed_metrics if a == "count"), None)
        if count_col and count_col in grouped.columns:
            grouped = grouped[grouped[count_col] >= min_count]
        else:
            sizes = df_f.groupby(group_by, observed=True).size()
            valid_groups = sizes[sizes >= min_count].index
            grouped = grouped[grouped[group_by].isin(valid_groups)]

    if sort_by:
        sort_col = sort_by if sort_by in grouped.columns else None
        if sort_col:
            grouped = grouped.sort_values(sort_col, ascending=(sort_order == "asc"))
    elif len(parsed_metrics) > 0:
        first_metric = f"{parsed_metrics[0][0]}:{parsed_metrics[0][1]}"
        if first_metric in grouped.columns:
            grouped = grouped.sort_values(first_metric, ascending=False)

    if limit:
        grouped = grouped.head(limit)

    header = _filters_summary(descs, n_filtered, n_total)
    n_groups = len(grouped)
    display_df = grouped.head(_MAX_DISPLAY_ROWS)
    table = display_df.to_markdown(index=False)
    trunc = f"\n\n*Showing {min(n_groups, _MAX_DISPLAY_ROWS)} of {n_groups} groups.*" if n_groups > _MAX_DISPLAY_ROWS else ""
    return f"### Group By: `{group_by}`\n\n{header}\n{table}{trunc}"


def _run_top_n(
    sort_by: str,
    n: int = 10,
    sort_order: str = "desc",
    filters: list[dict] | None = None,
    columns: list[str] | None = None,
    agg_column: str | None = None,
    agg: str = "sum",
) -> str:
    df = DataStore.df()
    n_total = len(df)

    if sort_by not in df.columns:
        return f"**Error:** Column '{sort_by}' not found."

    try:
        df_f, descs = _apply_filters(df, filters)
    except ValueError as e:
        return f"**Error:** {e}"

    n_filtered = len(df_f)
    if n_filtered == 0:
        return f"**No results.** Filters removed all rows.\n\n{_filters_summary(descs, 0, n_total)}"

    top = df_f.sort_values(sort_by, ascending=(sort_order == "asc")).head(n)
    header = _filters_summary(descs, n_filtered, n_total)
    order_label = "Bottom" if sort_order == "asc" else "Top"

    agg_summary = ""
    if agg_column:
        if agg_column not in df.columns:
            agg_summary = f"\n**Error:** agg_column '{agg_column}' not found.\n"
        elif agg not in _VALID_AGGS:
            agg_summary = f"\n**Error:** Invalid aggregation '{agg}'.\n"
        else:
            result = getattr(top[agg_column], agg)()
            formatted = _format_number(result, agg_column)
            agg_summary = f"\n**{agg.capitalize()}({agg_column}) over {order_label.lower()} {len(top):,}:** {formatted}\n"

    if columns:
        invalid = [c for c in columns if c not in df.columns]
        if invalid:
            return f"**Error:** Columns not found: {invalid}"
        display_cols = columns
    else:
        display_cols = [sort_by]
        for c in ["order_id", "customer_state", "product_category_name"]:
            if c in df.columns and c not in display_cols:
                display_cols.append(c)
                if len(display_cols) >= 5:
                    break

    display_df = top[display_cols].head(_MAX_DISPLAY_ROWS)
    table = display_df.to_markdown(index=False)
    trunc = f"\n\n*Showing {min(len(top), _MAX_DISPLAY_ROWS)} of {len(top)} rows.*" if len(top) > _MAX_DISPLAY_ROWS else ""
    return f"### {order_label} {len(top):,} by `{sort_by}`\n\n{header}{agg_summary}\n{table}{trunc}"


# ---------------------------------------------------------------------------
# Tool registration
# ---------------------------------------------------------------------------


def register(mcp: FastMCP) -> None:
    """Register 5 dynamic query tools on the MCP server."""

    @mcp.tool()
    def dynamic_aggregate(
        column: str,
        agg: str = "mean",
        filters: list[dict] | None = None,
        limit: int | None = None,
    ) -> str:
        """Aggregate a single column with optional filters.

        Supports: mean, sum, count, min, max, median, std, nunique, value_counts.
        Filter format: [{"column": "customer_state", "op": "eq", "value": "SP"}]
        """
        return _run_aggregate(column, agg, filters, limit)

    @mcp.tool()
    def group_by_metrics(
        group_by: str,
        metrics: list[str],
        filters: list[dict] | None = None,
        sort_by: str | None = None,
        sort_order: str = "desc",
        limit: int | None = None,
        min_count: int = 1,
    ) -> str:
        """Group data by a column and compute multiple metrics.

        metrics format: ["mean:foi_atraso", "sum:price", "count:order_id"]
        """
        return _run_group_by(group_by, metrics, filters, sort_by, sort_order, limit, min_count)

    @mcp.tool()
    def top_n_query(
        sort_by: str,
        n: int = 10,
        sort_order: str = "desc",
        filters: list[dict] | None = None,
        columns: list[str] | None = None,
        agg_column: str | None = None,
        agg: str = "sum",
    ) -> str:
        """Get top/bottom N rows sorted by a column, optionally aggregate over the result.

        Filter format: [{"column": "customer_state", "op": "eq", "value": "SP"}]
        """
        return _run_top_n(sort_by, n, sort_order, filters, columns, agg_column, agg)

    @mcp.tool()
    def batch_query(queries: list[dict]) -> str:
        """Execute multiple queries (aggregate, group_by, top_n) in a single call.

        'queries' is a list of dicts, each with a 'type' ("aggregate", "group_by", "top_n")
        and its corresponding arguments. Use this for complex multi-part analyses.
        """
        results = []
        for i, q in enumerate(queries, 1):
            q_type = q.get("type", "")
            # Accept tool names as aliases for query types
            q_type = {
                "dynamic_aggregate": "aggregate",
                "group_by_metrics": "group_by",
                "top_n_query": "top_n",
            }.get(q_type, q_type)
            try:
                if q_type == "aggregate":
                    res = _run_aggregate(
                        column=q["column"],
                        agg=q.get("agg", "mean"),
                        filters=q.get("filters"),
                        limit=q.get("limit"),
                    )
                elif q_type == "group_by":
                    res = _run_group_by(
                        group_by=q["group_by"],
                        metrics=q["metrics"],
                        filters=q.get("filters"),
                        sort_by=q.get("sort_by"),
                        sort_order=q.get("sort_order", "desc"),
                        limit=q.get("limit"),
                        min_count=q.get("min_count", 1),
                    )
                elif q_type == "top_n":
                    res = _run_top_n(
                        sort_by=q["sort_by"],
                        n=q.get("n", 10),
                        sort_order=q.get("sort_order", "desc"),
                        filters=q.get("filters"),
                        columns=q.get("columns"),
                        agg_column=q.get("agg_column"),
                        agg=q.get("agg", "sum"),
                    )
                else:
                    res = f"**Error:** Unsupported query type '{q_type}' in query {i}."
            except Exception as e:
                res = f"**Error:** Query {i} failed: {e}"

            results.append(f"--- QUERY {i} ({q_type}) ---\n{res}")

        return "\n\n".join(results)

    @mcp.tool()
    def compare_groups(
        group_a_filters: list[dict],
        group_b_filters: list[dict],
        metrics: list[str],
        group_a_label: str = "Group A",
        group_b_label: str = "Group B",
    ) -> str:
        """Compare two groups side-by-side on multiple metrics."""
        df = DataStore.df()

        try:
            df_a, descs_a = _apply_filters(df, group_a_filters)
            df_b, descs_b = _apply_filters(df, group_b_filters)
        except ValueError as e:
            return f"**Error:** {e}"

        if len(df_a) == 0:
            return f"**Error:** {group_a_label} has no rows after filtering."
        if len(df_b) == 0:
            return f"**Error:** {group_b_label} has no rows after filtering."

        parsed: list[tuple[str, str]] = []
        for m in metrics:
            try:
                agg_name, col_name = _parse_metric(m)
            except ValueError as e:
                return f"**Error:** {e}"
            if col_name not in df.columns:
                return f"**Error:** Column '{col_name}' not found in metric '{m}'."
            parsed.append((agg_name, col_name))

        rows = []
        for agg_name, col_name in parsed:
            val_a = getattr(df_a[col_name], agg_name)()
            val_b = getattr(df_b[col_name], agg_name)()

            fmt_a = _format_number(val_a, col_name)
            fmt_b = _format_number(val_b, col_name)

            if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)) and val_b != 0:
                diff = val_a - val_b
                pct = (diff / abs(val_b)) * 100
                fmt_diff = f"{diff:+,.4f} ({pct:+.1f}%)"
            else:
                fmt_diff = "N/A"

            rows.append({
                "Metric": f"{agg_name}:{col_name}",
                group_a_label: fmt_a,
                group_b_label: fmt_b,
                "Difference": fmt_diff,
            })

        result_df = pd.DataFrame(rows)
        table = result_df.to_markdown(index=False)
        header_a = f"**{group_a_label}:** {', '.join(descs_a) if descs_a else 'all'} ({len(df_a):,} rows)"
        header_b = f"**{group_b_label}:** {', '.join(descs_b) if descs_b else 'all'} ({len(df_b):,} rows)"

        return f"### Comparison: {group_a_label} vs {group_b_label}\n\n{header_a}\n{header_b}\n\n{table}"
