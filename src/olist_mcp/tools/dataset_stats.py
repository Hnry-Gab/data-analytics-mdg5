"""Dataset & Statistics Tools (5 tools).

Exposes statistics from the unified Olist dataset (~96K rows × 53 columns).
"""

from fastmcp import FastMCP

from ..cache import DataStore
from ..utils.haversine import haversine_distance

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
    "seller_lat": ("float64", "Seller latitude (geocoded from ZIP)"),
    "seller_lng": ("float64", "Seller longitude (geocoded from ZIP)"),
    "customer_lat": ("float64", "Customer latitude (geocoded from ZIP)"),
    "customer_lng": ("float64", "Customer longitude (geocoded from ZIP)"),
}

_ENGINEERED_COLUMNS = {
    "tipo_pagamento_principal": ("object", "Primary payment method"),
    "dias_diferenca": ("int64", "Days between estimated and actual delivery (negative = late)"),
    "foi_atraso": ("int64", "Target variable: 1 = delayed, 0 = on time"),
    "volume_cm3": ("float64", "Product volume (length × height × width) in cm³"),
    "frete_ratio": ("float64", "Freight / price ratio"),
    "velocidade_lojista_dias": ("float64", "Days between purchase and carrier handoff"),
    "dia_semana_compra": ("int64", "Day of week of purchase (0=Mon, 6=Sun)"),
    "rota_interestadual": ("int64", "1 if customer_state ≠ seller_state"),
    "distancia_haversine_km": ("float64", "Great-circle distance seller→customer in km"),
    "total_itens_pedido": ("int64", "Total items in the order"),
    "ticket_medio_alto": ("int64", "1 if order value above median"),
    "seller_regiao": ("object", "Seller macro-region (Norte/Nordeste/etc.)"),
    "customer_regiao": ("object", "Customer macro-region"),
    "historico_atraso_seller": ("float64", "Seller historical delay rate"),
    "velocidade_transportadora_dias": ("float64", "Days from carrier pickup to delivery"),
    "compra_fds": ("int64", "1 if purchased on weekend"),
    "mes_compra": ("int64", "Month of purchase (1-12)"),
    "valor_total_pedido": ("float64", "Total order value in BRL"),
    "destino_tipo": ("object", "Destination type: capital/interior"),
    "ano_compra": ("int64", "Year of purchase"),
}


def register(mcp: FastMCP) -> None:
    """Register 5 dataset statistics tools on the MCP server."""

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
            "### Unique Counts\n\n"
            f"| Entity | Count |\n"
            f"|--------|------:|\n"
            f"| Customers (unique) | {df['customer_unique_id'].nunique():,} |\n"
            f"| Sellers | {df['seller_id'].nunique():,} |\n"
            f"| Products | {df['product_id'].nunique():,} |\n"
            f"| States | {df['customer_state'].nunique()} |\n"
            f"| Cities (customer) | {df['customer_city'].nunique():,} |\n\n"
            "### ML Model\n\n"
            "- **CatBoost V5:** ROC-AUC 0.8454, 19 features, threshold 0.54\n"
            "- Use `get_catboost_model_info` for full details\n"
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
    def search_orders_by_order_id(order_id: str) -> str:
        """Look up a specific order by its ID. Returns all key fields formatted as sections."""
        df = DataStore.df()
        order = df[df["order_id"] == order_id]

        if order.empty:
            partial = df[df["order_id"].str.contains(order_id[:8], na=False)]
            n_partial = len(partial)
            return (
                f"**Error:** Order `{order_id}` not found.\n\n"
                f"Partial matches (first 8 chars): {n_partial}\n"
                f"Total orders in dataset: {df['order_id'].nunique():,}"
            )

        row = order.iloc[0]
        delay_status = "DELAYED" if row["foi_atraso"] == 1 else "On Time"

        sections = {
            "Identification": [
                ("order_id", row["order_id"]),
                ("customer_id", row["customer_id"]),
                ("seller_id", row["seller_id"]),
                ("order_status", row["order_status"]),
            ],
            "Dates": [
                ("order_purchase_timestamp", row["order_purchase_timestamp"]),
                ("order_approved_at", row["order_approved_at"]),
                ("order_delivered_carrier_date", row["order_delivered_carrier_date"]),
                ("order_delivered_customer_date", f"{row['order_delivered_customer_date']} ({delay_status})"),
                ("order_estimated_delivery_date", row["order_estimated_delivery_date"]),
            ],
            "Location": [
                ("customer_state", row["customer_state"]),
                ("customer_city", row["customer_city"]),
                ("seller_state", row["seller_state"]),
                ("seller_city", row["seller_city"]),
                ("distancia_haversine_km", f"{row['distancia_haversine_km']:.1f} km"),
                ("rota_interestadual", "Yes" if row["rota_interestadual"] == 1 else "No"),
            ],
            "Product & Pricing": [
                ("product_category_name", row["product_category_name"]),
                ("price", f"R$ {row['price']:.2f}"),
                ("freight_value", f"R$ {row['freight_value']:.2f}"),
                ("valor_total_pedido", f"R$ {row.get('valor_total_pedido', 0):.2f}"),
                ("tipo_pagamento_principal", row.get("tipo_pagamento_principal", "N/A")),
                ("product_weight_g", f"{row['product_weight_g']:.0f} g"),
                ("volume_cm3", f"{row['volume_cm3']:.0f} cm³"),
            ],
            "Delivery Metrics": [
                ("foi_atraso", delay_status),
                ("dias_diferenca", f"{row['dias_diferenca']} days"),
                ("velocidade_lojista_dias", f"{row['velocidade_lojista_dias']:.1f} days"),
            ],
        }

        lines = [f"## Order: `{order_id}`\n"]
        for section, fields in sections.items():
            lines.append(f"### {section}\n")
            lines.append("| Field | Value |")
            lines.append("|-------|-------|")
            for field, value in fields:
                lines.append(f"| {field} | {value} |")
            lines.append("")

        return "\n".join(lines)

    @mcp.tool()
    def calculate_haversine_distance_tool(
        seller_lat: float,
        seller_lng: float,
        customer_lat: float,
        customer_lng: float,
    ) -> str:
        """Calculate the great-circle distance between two coordinates (seller and customer) in kilometers using the Haversine formula."""
        distance = haversine_distance(seller_lat, seller_lng, customer_lat, customer_lng)
        return (
            f"## Haversine Distance\n\n"
            f"- **Seller:** ({seller_lat:.4f}, {seller_lng:.4f})\n"
            f"- **Customer:** ({customer_lat:.4f}, {customer_lng:.4f})\n"
            f"- **Distance:** {distance:.2f} km\n"
        )
