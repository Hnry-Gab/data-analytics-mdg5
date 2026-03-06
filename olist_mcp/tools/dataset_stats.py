"""MCP-01: Dataset & Statistics Tools (6 tools).

Exposes statistics from the unified Olist dataset and training data.
"""

from fastmcp import FastMCP

from olist_mcp.cache import DataStore
from olist_mcp.utils.formatters import format_json_safe, format_markdown_table

# Schema column groupings for get_dataset_schema
_DIRECT_COLUMNS = {
    "order_id": ("object", "Unique order identifier"),
    "customer_id": ("object", "Customer identifier (per order)"),
    "order_status": ("object", "Order status (all 'delivered' in this dataset)"),
    "order_purchase_timestamp": ("datetime64", "When the order was placed"),
    "order_approved_at": ("datetime64", "When payment was approved"),
    "order_delivered_carrier_date": ("datetime64", "When seller handed to carrier"),
    "order_delivered_customer_date": ("datetime64", "When customer received the order"),
    "order_estimated_delivery_date": ("datetime64", "Estimated delivery date shown to customer"),
    "customer_unique_id": ("object", "Unique customer across orders"),
    "customer_zip_code_prefix": ("str", "Customer ZIP code (5 digits, zero-padded)"),
    "customer_city": ("object", "Customer city name"),
    "customer_state": ("object", "Customer state (UF, 2 letters)"),
    "order_item_id": ("int64", "Sequential item number within the order"),
    "product_id": ("object", "Unique product identifier"),
    "seller_id": ("object", "Unique seller identifier"),
    "shipping_limit_date": ("datetime64", "Deadline for seller to ship"),
    "price": ("float64", "Product price in BRL"),
    "freight_value": ("float64", "Freight cost in BRL"),
    "product_category_name": ("object", "Product category (Portuguese)"),
    "product_name_lenght": ("float64", "Length of product title (chars)"),
    "product_description_lenght": ("float64", "Length of product description (chars)"),
    "product_photos_qty": ("float64", "Number of product photos"),
    "product_weight_g": ("float64", "Product weight in grams"),
    "product_length_cm": ("float64", "Product length in cm"),
    "product_height_cm": ("float64", "Product height in cm"),
    "product_width_cm": ("float64", "Product width in cm"),
    "seller_zip_code_prefix": ("str", "Seller ZIP code (5 digits, zero-padded)"),
    "seller_city": ("object", "Seller city name"),
    "seller_state": ("object", "Seller state (UF, 2 letters)"),
}

_ENGINEERED_COLUMNS = {
    "dias_diferenca": ("int64", "Days between estimated and actual delivery (negative = late)"),
    "foi_atraso": ("int64", "Target variable: 1 = delayed, 0 = on time"),
    "volume_cm3": ("float64", "Product volume (length × height × width) in cm³"),
    "frete_ratio": ("float64", "Freight / price ratio"),
    "velocidade_lojista_dias": ("float64", "Days between purchase and carrier handoff"),
    "dia_semana_compra": ("int64", "Day of week of purchase (0=Mon, 6=Sun)"),
    "rota_interestadual": ("int64", "1 if customer_state ≠ seller_state"),
    "customer_lat": ("float64", "Customer latitude (geocoded from ZIP)"),
    "customer_lng": ("float64", "Customer longitude (geocoded from ZIP)"),
    "seller_lat": ("float64", "Seller latitude (geocoded from ZIP)"),
    "seller_lng": ("float64", "Seller longitude (geocoded from ZIP)"),
    "distancia_haversine_km": ("float64", "Great-circle distance seller→customer in km"),
}


def register(mcp: FastMCP) -> None:
    """Register all 6 dataset statistics tools on the MCP server."""

    @mcp.tool()
    def get_dataset_overview() -> str:
        """Get a high-level overview of the Olist unified dataset: dimensions, date range, target distribution, unique counts, and memory usage."""
        df = DataStore.df()

        total = len(df)
        delayed = int(df["foi_atraso"].sum())
        on_time = total - delayed
        delay_pct = delayed / total * 100
        on_time_pct = 100 - delay_pct

        date_min = df["order_purchase_timestamp"].min()
        date_max = df["order_purchase_timestamp"].max()

        mem_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)

        return (
            "## Dataset Overview — Olist Brazilian E-Commerce\n\n"
            f"- **Dimensions:** {total:,} rows × {len(df.columns)} columns\n"
            f"- **Date range:** {date_min:%Y-%m-%d} to {date_max:%Y-%m-%d}\n"
            f"- **Memory usage:** {mem_mb:.1f} MB\n\n"
            "### Target Distribution (`foi_atraso`)\n\n"
            f"| Class | Count | Percentage |\n"
            f"|-------|------:|-----------:|\n"
            f"| 0 (on time) | {on_time:,} | {on_time_pct:.2f}% |\n"
            f"| 1 (delayed) | {delayed:,} | {delay_pct:.2f}% |\n\n"
            f"- **scale_pos_weight** (for XGBoost): {on_time / delayed:.2f}\n\n"
            "### Unique Counts\n\n"
            f"| Entity | Count |\n"
            f"|--------|------:|\n"
            f"| Customers (unique) | {df['customer_unique_id'].nunique():,} |\n"
            f"| Sellers | {df['seller_id'].nunique():,} |\n"
            f"| Products | {df['product_id'].nunique():,} |\n"
            f"| States | {df['customer_state'].nunique()} |\n"
            f"| Cities (customer) | {df['customer_city'].nunique():,} |\n"
        )

    @mcp.tool()
    def get_column_statistics(column_name: str) -> str:
        """Get detailed statistics for a single column. For numeric columns: count, mean, std, min, quartiles, max, nulls, nunique. For categorical: unique count, top-10 value counts, nulls."""
        df = DataStore.df()

        if column_name not in df.columns:
            available = ", ".join(sorted(df.columns))
            return f"**Error:** Column `{column_name}` not found.\n\nAvailable columns: {available}"

        col = df[column_name]
        null_count = int(col.isna().sum())
        null_pct = null_count / len(col) * 100
        nunique = col.nunique()

        header = f"## Column: `{column_name}`\n\n"

        if col.dtype in ("float64", "int64", "Float64", "Int64"):
            desc = col.describe()
            return (
                header
                + f"- **Type:** numeric (`{col.dtype}`)\n"
                f"- **Non-null count:** {int(desc['count']):,}\n"
                f"- **Null count:** {null_count:,} ({null_pct:.2f}%)\n"
                f"- **Unique values:** {nunique:,}\n\n"
                "### Descriptive Statistics\n\n"
                f"| Stat | Value |\n"
                f"|------|------:|\n"
                f"| mean | {desc['mean']:.4f} |\n"
                f"| std | {desc['std']:.4f} |\n"
                f"| min | {desc['min']:.4f} |\n"
                f"| 25% | {desc['25%']:.4f} |\n"
                f"| 50% | {desc['50%']:.4f} |\n"
                f"| 75% | {desc['75%']:.4f} |\n"
                f"| max | {desc['max']:.4f} |\n"
            )
        else:
            top_values = col.value_counts().head(10)
            rows = ""
            for val, count in top_values.items():
                pct = count / len(col) * 100
                rows += f"| {val} | {count:,} | {pct:.2f}% |\n"

            return (
                header
                + f"- **Type:** categorical (`{col.dtype}`)\n"
                f"- **Unique values:** {nunique:,}\n"
                f"- **Null count:** {null_count:,} ({null_pct:.2f}%)\n\n"
                "### Top 10 Values\n\n"
                f"| Value | Count | Percentage |\n"
                f"|-------|------:|-----------:|\n"
                + rows
            )

    @mcp.tool()
    def get_class_distribution() -> str:
        """Get the target variable (foi_atraso) class distribution with imbalance metrics. Important: accuracy is a prohibited metric due to class imbalance."""
        df = DataStore.df()
        vc = df["foi_atraso"].value_counts().sort_index()

        total = len(df)
        on_time = int(vc.get(0, 0))
        delayed = int(vc.get(1, 0))
        delay_rate = delayed / total * 100
        spw = on_time / delayed if delayed > 0 else 0

        return (
            "## Target Variable: `foi_atraso`\n\n"
            f"| Class | Label | Count | Percentage |\n"
            f"|------:|-------|------:|-----------:|\n"
            f"| 0 | On time | {on_time:,} | {100 - delay_rate:.2f}% |\n"
            f"| 1 | Delayed | {delayed:,} | {delay_rate:.2f}% |\n"
            f"| | **Total** | **{total:,}** | **100%** |\n\n"
            f"- **Imbalance ratio:** {on_time / delayed:.1f}:1\n"
            f"- **scale_pos_weight** (XGBoost): `{spw:.2f}`\n\n"
            "> **Note:** Accuracy is a prohibited metric for this dataset due to severe "
            "class imbalance. Use ROC-AUC, F1-score, or precision/recall instead.\n"
        )

    @mcp.tool()
    def get_correlation_table(
        sort_by: str = "absolute_value",
        min_correlation: float = 0.0,
    ) -> str:
        """Get the feature correlation ranking table (Pearson for numeric, Cramér's V for categorical). Options: sort by absolute_value (default), value, or feature_name; filter by minimum correlation."""
        corr = DataStore.correlations()

        # Filter by minimum correlation
        if min_correlation > 0:
            corr = corr[corr["|Valor|"] >= min_correlation]

        # Sort
        if sort_by == "absolute_value":
            corr = corr.sort_values("|Valor|", ascending=False)
        elif sort_by == "value":
            corr = corr.sort_values("Valor", ascending=False)
        elif sort_by == "feature_name":
            corr = corr.sort_values("Feature")

        if corr.empty:
            return f"No features with correlation >= {min_correlation}"

        header = "## Feature Correlation Ranking\n\n"
        if min_correlation > 0:
            header += f"*Filtered: |correlation| >= {min_correlation}*\n\n"

        return header + format_markdown_table(corr)

    @mcp.tool()
    def get_dataset_schema() -> str:
        """Get the complete dataset schema: all columns organized by group (direct from source vs engineered), with data types and descriptions."""
        lines = [
            "## Dataset Schema\n",
            f"**Total columns:** {len(_DIRECT_COLUMNS) + len(_ENGINEERED_COLUMNS)}\n",
            "### Direct Columns (from Olist source data)\n",
            "| Column | Type | Description |",
            "|--------|------|-------------|",
        ]
        for col, (dtype, desc) in _DIRECT_COLUMNS.items():
            lines.append(f"| `{col}` | {dtype} | {desc} |")

        lines.extend([
            "",
            "### Engineered Columns (feature engineering pipeline)\n",
            "| Column | Type | Description |",
            "|--------|------|-------------|",
        ])
        for col, (dtype, desc) in _ENGINEERED_COLUMNS.items():
            lines.append(f"| `{col}` | {dtype} | {desc} |")

        return "\n".join(lines)

    @mcp.tool()
    def get_training_dataset_info() -> str:
        """Get information about the training dataset used for the XGBoost delay prediction model: shape, columns, target distribution, encoding notes."""
        df_treino = DataStore.df_treino()

        total = len(df_treino)
        delayed = int(df_treino["foi_atraso"].sum())
        on_time = total - delayed
        delay_pct = delayed / total * 100

        cols_info = ""
        for col in df_treino.columns:
            dtype = df_treino[col].dtype
            nulls = int(df_treino[col].isna().sum())
            cols_info += f"| `{col}` | {dtype} | {nulls} |\n"

        return (
            "## Training Dataset\n\n"
            f"- **Shape:** {total:,} rows × {len(df_treino.columns)} columns\n"
            f"- **File:** `dataset_treino_v1.csv`\n\n"
            "### Columns\n\n"
            "| Column | Type | Nulls |\n"
            "|--------|------|------:|\n"
            + cols_info
            + "\n### Target Distribution\n\n"
            f"| Class | Count | Percentage |\n"
            f"|------:|------:|-----------:|\n"
            f"| 0 (on time) | {on_time:,} | {100 - delay_pct:.2f}% |\n"
            f"| 1 (delayed) | {delayed:,} | {delay_pct:.2f}% |\n\n"
            "### Encoding Notes\n\n"
            "- `customer_state_encoded` and `seller_state_encoded`: Target encoding "
            "(delay rate per state) applied to UF codes\n"
            "- No normalization applied (benchmark showed minimal delta)\n"
        )
