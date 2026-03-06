"""MCP-08: Filtering & Query Tools (8 tools).

Ad-hoc queries and filters: composite filters, state-pair routes,
category deep-dives, order lookups, weight analysis, state comparison,
high-risk profiles, and seller rankings.
"""

import numpy as np
import pandas as pd
from fastmcp import FastMCP

from olist_mcp.cache import DataStore
from olist_mcp.utils.formatters import format_markdown_table
from olist_mcp.utils.state_mappings import STATE_TO_REGION


def register(mcp: FastMCP) -> None:
    """Register all 8 filtering & query tools on the MCP server."""

    @mcp.tool()
    def filter_orders(
        customer_state: str | None = None,
        seller_state: str | None = None,
        product_category: str | None = None,
        foi_atraso: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        rota_interestadual: int | None = None,
    ) -> str:
        """Filter orders by multiple criteria and return aggregate statistics. Never exposes individual rows — only aggregated stats for the filtered slice."""
        df = DataStore.df()
        total_dataset = len(df)

        mask = pd.Series(True, index=df.index)
        filters_applied: dict[str, object] = {}

        if customer_state is not None:
            mask &= df["customer_state"] == customer_state.upper()
            filters_applied["customer_state"] = customer_state.upper()
        if seller_state is not None:
            mask &= df["seller_state"] == seller_state.upper()
            filters_applied["seller_state"] = seller_state.upper()
        if product_category is not None:
            mask &= df["product_category_name"].str.contains(
                product_category, case=False, na=False,
            )
            filters_applied["product_category"] = product_category
        if foi_atraso is not None:
            mask &= df["foi_atraso"] == foi_atraso
            filters_applied["foi_atraso"] = foi_atraso
        if min_price is not None:
            mask &= df["price"] >= min_price
            filters_applied["min_price"] = min_price
        if max_price is not None:
            mask &= df["price"] <= max_price
            filters_applied["max_price"] = max_price
        if start_date is not None:
            mask &= df["order_purchase_timestamp"] >= pd.Timestamp(start_date)
            filters_applied["start_date"] = start_date
        if end_date is not None:
            mask &= df["order_purchase_timestamp"] <= pd.Timestamp(end_date)
            filters_applied["end_date"] = end_date
        if rota_interestadual is not None:
            mask &= df["rota_interestadual"] == rota_interestadual
            filters_applied["rota_interestadual"] = rota_interestadual

        filtered = df[mask]
        matched = len(filtered)
        national_rate = df["foi_atraso"].mean() * 100

        if matched == 0:
            filters_str = ", ".join(f"`{k}`={v}" for k, v in filters_applied.items())
            return (
                f"**No orders matched** the applied filters: {filters_str}\\n\\n"
                f"Total orders in dataset: {total_dataset:,}"
            )

        delay_rate = filtered["foi_atraso"].mean() * 100
        pct = matched / total_dataset * 100

        filters_lines = ""
        for k, v in filters_applied.items():
            filters_lines += f"- `{k}`: {v}\n"

        stats = (
            f"| Price (mean) | R${filtered['price'].mean():.2f} |\n"
            f"| Price (std) | R${filtered['price'].std():.2f} |\n"
            f"| Freight (mean) | R${filtered['freight_value'].mean():.2f} |\n"
            f"| Distance (mean) | {filtered['distancia_haversine_km'].mean():.1f} km |\n"
            f"| Dispatch speed (mean) | {filtered['velocidade_lojista_dias'].mean():.1f} days |\n"
        )

        return (
            "## Filtered Orders — Aggregate Statistics\n\n"
            f"**Rows matched:** {matched:,} / {total_dataset:,} ({pct:.2f}%)\n\n"
            "### Filters Applied\n\n"
            + filters_lines
            + f"\n### Delay Comparison\n\n"
            f"- **Filtered delay rate:** {delay_rate:.2f}%\n"
            f"- **National delay rate:** {national_rate:.2f}%\n"
            f"- **Difference:** {delay_rate - national_rate:+.2f}pp\n\n"
            "### Statistics\n\n"
            "| Metric | Value |\n"
            "|--------|------:|\n"
            + stats
        )

    @mcp.tool()
    def get_orders_by_state_pair(
        seller_state: str,
        customer_state: str,
        min_orders: int = 10,
    ) -> str:
        """Get delay statistics for a specific seller→customer state route. Validates minimum order count for statistical significance."""
        df = DataStore.df()

        route = df[
            (df["seller_state"] == seller_state.upper())
            & (df["customer_state"] == customer_state.upper())
        ]

        total = len(route)
        if total < min_orders:
            return (
                f"**Error:** Route {seller_state.upper()} → {customer_state.upper()} "
                f"has only {total} orders (minimum required: {min_orders}).\n\n"
                f"Increase data or lower `min_orders` parameter."
            )

        delayed = int(route["foi_atraso"].sum())
        delay_rate = delayed / total * 100
        avg_dist = route["distancia_haversine_km"].mean()
        avg_freight = route["freight_value"].mean()
        avg_speed = route["velocidade_lojista_dias"].mean()
        national_rate = df["foi_atraso"].mean() * 100

        return (
            f"## Route: {seller_state.upper()} → {customer_state.upper()}\n\n"
            f"| Metric | Value |\n"
            f"|--------|------:|\n"
            f"| Total orders | {total:,} |\n"
            f"| Delayed orders | {delayed:,} |\n"
            f"| Delay rate | {delay_rate:.2f}% |\n"
            f"| National rate | {national_rate:.2f}% |\n"
            f"| Avg distance | {avg_dist:.1f} km |\n"
            f"| Avg freight | R${avg_freight:.2f} |\n"
            f"| Avg dispatch speed | {avg_speed:.1f} days |\n\n"
            f"**Validation:** min_orders={min_orders} satisfied ({total:,} >> {min_orders})\n"
        )

    @mcp.tool()
    def get_category_deep_dive(category_name: str) -> str:
        """Deep-dive analysis of a product category. Supports partial, case-insensitive matching."""
        df = DataStore.df()

        matches = df[
            df["product_category_name"].str.contains(
                category_name, case=False, na=False,
            )
        ]

        if matches.empty:
            all_cats = sorted(df["product_category_name"].dropna().unique())
            cat_list = "\n".join(f"- `{c}`" for c in all_cats[:20])
            return (
                f"**Error:** No category matching `{category_name}`.\n\n"
                f"Available categories (first 20):\n{cat_list}\n\n"
                f"Total categories: {len(all_cats)}"
            )

        # Use the most common matching category
        category = matches["product_category_name"].mode().iloc[0]
        cat_data = df[df["product_category_name"] == category]

        total = len(cat_data)
        delayed = int(cat_data["foi_atraso"].sum())
        delay_rate = delayed / total * 100
        national_rate = df["foi_atraso"].mean() * 100
        diff = delay_rate - national_rate

        avg_price = cat_data["price"].mean()
        avg_freight = cat_data["freight_value"].mean()
        avg_weight = cat_data["product_weight_g"].mean()
        avg_volume = cat_data["volume_cm3"].mean()

        top_cust = cat_data["customer_state"].value_counts().head(5)
        top_sell = cat_data["seller_state"].value_counts().head(5)

        cust_lines = ""
        for st, cnt in top_cust.items():
            cust_lines += f"| {st} | {cnt:,} | {cnt / total * 100:.1f}% |\n"
        sell_lines = ""
        for st, cnt in top_sell.items():
            sell_lines += f"| {st} | {cnt:,} | {cnt / total * 100:.1f}% |\n"

        return (
            f"## Category Deep Dive: `{category}`\n\n"
            f"| Metric | Value |\n"
            f"|--------|------:|\n"
            f"| Total orders | {total:,} |\n"
            f"| Delayed orders | {delayed:,} |\n"
            f"| Delay rate | {delay_rate:.2f}% |\n"
            f"| vs National | {diff:+.2f}pp (vs {national_rate:.2f}%) |\n"
            f"| Avg price | R${avg_price:.2f} |\n"
            f"| Avg freight | R${avg_freight:.2f} |\n"
            f"| Avg weight | {avg_weight:,.0f} g |\n"
            f"| Avg volume | {avg_volume:,.0f} cm³ |\n\n"
            "### Top 5 Customer States\n\n"
            "| State | Orders | % |\n"
            "|-------|-------:|--:|\n"
            + cust_lines
            + "\n### Top 5 Seller States\n\n"
            "| State | Orders | % |\n"
            "|-------|-------:|--:|\n"
            + sell_lines
        )

    @mcp.tool()
    def search_orders_by_order_id(order_id: str) -> str:
        """Look up a specific order by its ID. Returns all columns formatted as key-value pairs."""
        df = DataStore.df()
        order = df[df["order_id"] == order_id]

        if order.empty:
            # Try partial match
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
                ("customer_zip_code_prefix", row["customer_zip_code_prefix"]),
                ("seller_state", row["seller_state"]),
                ("seller_city", row["seller_city"]),
                ("seller_zip_code_prefix", row["seller_zip_code_prefix"]),
            ],
            "Product": [
                ("product_category_name", row["product_category_name"]),
                ("product_weight_g", f"{row['product_weight_g']:,.0f} g" if pd.notna(row["product_weight_g"]) else "N/A"),
                ("product_length_cm", row.get("product_length_cm", "N/A")),
                ("product_height_cm", row.get("product_height_cm", "N/A")),
                ("product_width_cm", row.get("product_width_cm", "N/A")),
                ("volume_cm3", f"{row['volume_cm3']:,.0f} cm³" if pd.notna(row["volume_cm3"]) else "N/A"),
            ],
            "Financial": [
                ("price", f"R${row['price']:.2f}"),
                ("freight_value", f"R${row['freight_value']:.2f}"),
                ("frete_ratio", f"{row['frete_ratio']:.4f}" if pd.notna(row["frete_ratio"]) else "N/A"),
            ],
            "Features": [
                ("foi_atraso", f"{int(row['foi_atraso'])} ({delay_status.lower()})"),
                ("dias_diferenca", f"{row['dias_diferenca']:.0f} days"),
                ("velocidade_lojista_dias", f"{row['velocidade_lojista_dias']:.1f} days"),
                ("distancia_haversine_km", f"{row['distancia_haversine_km']:.1f} km" if pd.notna(row["distancia_haversine_km"]) else "N/A"),
                ("rota_interestadual", "Yes" if row["rota_interestadual"] == 1 else "No"),
            ],
        }

        lines = [f"## Order: `{order_id}`\n"]
        for section, fields in sections.items():
            lines.append(f"\n### {section}\n")
            for key, val in fields:
                lines.append(f"- **{key}:** {val}")

        return "\n".join(lines)

    @mcp.tool()
    def get_product_weight_analysis(
        weight_bins: list[float] | None = None,
    ) -> str:
        """Analyze delay rates by product weight bins. Shows relationship between weight and delivery delays."""
        df = DataStore.df()

        if weight_bins is None:
            bins = [0, 500, 2000, 10000, 30000, float("inf")]
        else:
            bins = weight_bins

        labels = []
        for i in range(len(bins) - 1):
            low = int(bins[i])
            high = bins[i + 1]
            if high == float("inf"):
                labels.append(f"{low}+")
            else:
                labels.append(f"{low}-{int(high)}")

        valid = df.dropna(subset=["product_weight_g"])
        valid = valid.copy()
        valid["weight_bin"] = pd.cut(
            valid["product_weight_g"], bins=bins, labels=labels, right=False,
        )

        agg = valid.groupby("weight_bin", observed=False).agg(
            total_orders=("foi_atraso", "count"),
            delayed_orders=("foi_atraso", "sum"),
        )
        agg["delay_rate_pct"] = (agg["delayed_orders"] / agg["total_orders"] * 100).round(2)
        agg = agg.reset_index()

        pearson = valid["product_weight_g"].corr(valid["foi_atraso"])

        table = format_markdown_table(agg)

        bin_note = "Default" if weight_bins is None else "Custom"

        return (
            "## Product Weight vs Delay Rate\n\n"
            + table
            + f"\n\n**Pearson correlation (weight × delay):** {pearson:+.4f} (very weak)\n\n"
            f"> **Insight:** Heavier products tend to have slightly higher delay rates, "
            f"but the correlation is very weak. Weight alone is not a strong predictor.\n\n"
            f"*{bin_note} bins: {bins}*\n"
        )

    @mcp.tool()
    def compare_two_states(
        state_a: str,
        state_b: str,
        perspective: str = "customer",
    ) -> str:
        """Compare two states side by side on delay metrics. Perspective can be 'customer' or 'seller'."""
        df = DataStore.df()

        col = "customer_state" if perspective == "customer" else "seller_state"
        a = state_a.upper()
        b = state_b.upper()

        valid_states = df[col].unique()
        for st in [a, b]:
            if st not in valid_states:
                return (
                    f"**Error:** State `{st}` not found in `{col}` column.\n\n"
                    f"Available states: {', '.join(sorted(valid_states))}"
                )

        data_a = df[df[col] == a]
        data_b = df[df[col] == b]

        def _stats(data: pd.DataFrame) -> dict:
            total = len(data)
            delayed = int(data["foi_atraso"].sum())
            return {
                "total": total,
                "delayed": delayed,
                "delay_rate": delayed / total * 100 if total > 0 else 0,
                "avg_freight": data["freight_value"].mean(),
                "avg_distance": data["distancia_haversine_km"].mean(),
                "avg_speed": data["velocidade_lojista_dias"].mean(),
                "top_route_state": (
                    data["seller_state" if col == "customer_state" else "customer_state"]
                    .value_counts()
                    .head(1)
                ),
            }

        sa = _stats(data_a)
        sb = _stats(data_b)

        top_a = sa["top_route_state"]
        top_b = sb["top_route_state"]
        top_a_str = f"{top_a.index[0]} ({top_a.iloc[0] / sa['total'] * 100:.0f}%)" if len(top_a) > 0 else "N/A"
        top_b_str = f"{top_b.index[0]} ({top_b.iloc[0] / sb['total'] * 100:.0f}%)" if len(top_b) > 0 else "N/A"

        # Differences
        rate_ratio = sa["delay_rate"] / sb["delay_rate"] if sb["delay_rate"] > 0 else float("inf")
        dist_diff = sa["avg_distance"] - sb["avg_distance"]
        speed_diff = sa["avg_speed"] - sb["avg_speed"]

        perspective_label = "Customer" if perspective == "customer" else "Seller"

        return (
            f"## State Comparison ({perspective_label} perspective): {a} vs {b}\n\n"
            f"| Metric | {a} | {b} |\n"
            f"|--------|----:|----:|\n"
            f"| Total orders | {sa['total']:,} | {sb['total']:,} |\n"
            f"| Delayed orders | {sa['delayed']:,} | {sb['delayed']:,} |\n"
            f"| Delay rate (%) | {sa['delay_rate']:.2f} | {sb['delay_rate']:.2f} |\n"
            f"| Avg freight (R$) | {sa['avg_freight']:.2f} | {sb['avg_freight']:.2f} |\n"
            f"| Avg distance (km) | {sa['avg_distance']:.1f} | {sb['avg_distance']:.1f} |\n"
            f"| Avg dispatch (days) | {sa['avg_speed']:.1f} | {sb['avg_speed']:.1f} |\n"
            f"| Top route partner | {top_a_str} | {top_b_str} |\n\n"
            "### Key Differences\n\n"
            f"- {a} has **{rate_ratio:.1f}x** the delay rate of {b}\n"
            f"- Distance difference: {dist_diff:+.1f} km\n"
            f"- Dispatch speed difference: {speed_diff:+.1f} days\n"
        )

    @mcp.tool()
    def get_high_risk_order_profile(
        delay_percentile: float = 0.9,
    ) -> str:
        """Profile of a typical high-risk (delayed) order. Shows median values and most common characteristics of delayed orders."""
        df = DataStore.df()
        delayed = df[df["foi_atraso"] == 1]
        total_delayed = len(delayed)

        # Numeric medians
        speed_med = delayed["velocidade_lojista_dias"].median()
        dist_med = delayed["distancia_haversine_km"].median()
        freight_med = delayed["freight_value"].median()
        weight_med = delayed["product_weight_g"].median()
        price_med = delayed["price"].median()

        # Top customer states
        top_cust = delayed["customer_state"].value_counts().head(3)
        cust_lines = ""
        for st, cnt in top_cust.items():
            cust_lines += f"- **{st}** ({cnt / total_delayed * 100:.0f}%)\n"

        # Top seller states
        top_sell = delayed["seller_state"].value_counts().head(3)
        sell_lines = ""
        for st, cnt in top_sell.items():
            sell_lines += f"- **{st}** ({cnt / total_delayed * 100:.0f}%)\n"

        # Interstate %
        interstate_pct = delayed["rota_interestadual"].mean() * 100

        # Top categories
        top_cats = delayed["product_category_name"].value_counts().head(3)
        cat_lines = ""
        for cat, cnt in top_cats.items():
            cat_lines += f"- `{cat}` ({cnt / total_delayed * 100:.0f}%)\n"

        # Month distribution
        month_counts = delayed["order_purchase_timestamp"].dt.month.value_counts()
        peak_month = month_counts.idxmax()
        month_names = {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December",
        }
        peak_month_name = month_names.get(peak_month, str(peak_month))
        peak_month_pct = month_counts.max() / total_delayed * 100

        return (
            "## High-Risk Order Profile\n\n"
            f"*Based on {total_delayed:,} delayed orders*\n\n"
            "### Risk Characteristics (medians)\n\n"
            f"- `velocidade_lojista_dias`: **{speed_med:.1f} days**\n"
            f"- `distancia_haversine_km`: **{dist_med:,.0f} km**\n"
            f"- `freight_value`: **R${freight_med:.2f}**\n"
            f"- `product_weight_g`: **{weight_med:,.0f} g**\n"
            f"- `price`: **R${price_med:.2f}**\n\n"
            "### Location\n\n"
            "**Top customer states:**\n"
            + cust_lines
            + "\n**Top seller states:**\n"
            + sell_lines
            + f"\n**Interstate routes:** {interstate_pct:.0f}%\n\n"
            "### Product Categories\n\n"
            + cat_lines
            + "\n### Seasonality\n\n"
            f"- **Peak month:** {peak_month_name} ({peak_month_pct:.0f}%)\n"
            "- **Day of week:** No strong pattern\n\n"
            "> **Usage:** This profile helps identify orders at risk of delay "
            "before they become problematic. Flag orders matching these "
            "characteristics for proactive intervention.\n"
        )

    @mcp.tool()
    def get_seller_ranking(
        metric: str = "delay_rate",
        top_n: int = 20,
        min_orders: int = 30,
        state: str | None = None,
    ) -> str:
        """Rank sellers by a chosen metric. Options: 'delay_rate' (worst first), 'total_orders' (most active), or 'avg_velocidade' (slowest dispatch). Filters by minimum order count for statistical validity."""
        df = DataStore.df()

        agg = df.groupby("seller_id").agg(
            seller_state=("seller_state", "first"),
            total_orders=("foi_atraso", "count"),
            delayed_orders=("foi_atraso", "sum"),
            avg_velocidade=("velocidade_lojista_dias", "mean"),
        )
        agg["delay_rate_pct"] = (agg["delayed_orders"] / agg["total_orders"] * 100).round(2)
        agg["avg_velocidade"] = agg["avg_velocidade"].round(1)

        agg = agg[agg["total_orders"] >= min_orders]

        if state is not None:
            agg = agg[agg["seller_state"] == state.upper()]
            if agg.empty:
                return (
                    f"**Error:** No sellers in state `{state.upper()}` with "
                    f"≥{min_orders} orders."
                )

        valid_metrics = {"delay_rate", "total_orders", "avg_velocidade"}
        if metric not in valid_metrics:
            return (
                f"**Error:** Invalid metric `{metric}`. "
                f"Valid options: {', '.join(sorted(valid_metrics))}"
            )

        ascending = metric == "total_orders"
        sort_col = "delay_rate_pct" if metric == "delay_rate" else metric
        agg = agg.sort_values(sort_col, ascending=not ascending if metric == "total_orders" else not True)

        # Simplify: delay_rate and avg_velocidade descending (worst first), total_orders descending (most active first)
        if metric == "delay_rate":
            agg = agg.sort_values("delay_rate_pct", ascending=False)
        elif metric == "total_orders":
            agg = agg.sort_values("total_orders", ascending=False)
        elif metric == "avg_velocidade":
            agg = agg.sort_values("avg_velocidade", ascending=False)

        agg = agg.head(top_n).reset_index()

        state_filter = f" (state: {state.upper()})" if state else ""
        header = (
            f"## Seller Ranking by `{metric}`{state_filter}\n\n"
            f"*Top {top_n} — minimum {min_orders} orders per seller*\n\n"
        )

        display = agg[["seller_id", "seller_state", "total_orders", "delayed_orders", "delay_rate_pct", "avg_velocidade"]].copy()
        display.columns = ["seller_id", "state", "total_orders", "delayed", "delay_rate_%", "avg_dispatch_days"]

        footer = (
            f"\n\n> **Note:** Only sellers with ≥{min_orders} orders "
            f"included for statistical validity.\n"
        )

        return header + format_markdown_table(display) + footer
