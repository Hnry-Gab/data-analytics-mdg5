"""MCP-02: Geographic Analysis Tools (8 tools).

Analyzes delivery delays by state, route, distance, and macro-region.
"""

import pandas as pd
from fastmcp import FastMCP

from olist_mcp.cache import DataStore
from olist_mcp.utils.formatters import format_json_safe, format_markdown_table
from olist_mcp.utils.haversine import haversine_distance
from olist_mcp.utils.state_mappings import STATE_TO_REGION


def _delay_by_group(df: pd.DataFrame, group_col: str, min_orders: int, ascending: bool) -> pd.DataFrame:
    """Compute delay rate grouped by a column, with min_orders filter."""
    agg = df.groupby(group_col)["foi_atraso"].agg(
        total_orders="count",
        delayed_orders="sum",
    )
    agg["delay_rate_pct"] = (agg["delayed_orders"] / agg["total_orders"] * 100).round(2)
    agg = agg[agg["total_orders"] >= min_orders]
    agg = agg.sort_values("delay_rate_pct", ascending=ascending)
    agg = agg.reset_index()
    agg["region"] = agg[group_col].map(STATE_TO_REGION)
    return agg


def register(mcp: FastMCP) -> None:
    """Register all 8 geographic analysis tools on the MCP server."""

    @mcp.tool()
    def get_delay_rate_by_customer_state(
        min_orders: int = 10,
        sort_order: str = "desc",
    ) -> str:
        """Get delay rate by customer state (UF). Shows total orders, delayed count, delay rate %, and macro-region for each of 27 states."""
        df = DataStore.df()
        ascending = sort_order == "asc"
        result = _delay_by_group(df, "customer_state", min_orders, ascending)

        national_rate = df["foi_atraso"].mean() * 100

        header = (
            "## Delay Rate by Customer State\n\n"
            f"**National average:** {national_rate:.2f}%\n\n"
        )
        return header + format_markdown_table(result)

    @mcp.tool()
    def get_delay_rate_by_seller_state(
        min_orders: int = 10,
        sort_order: str = "desc",
    ) -> str:
        """Get delay rate by seller state (UF). Shows total orders, delayed count, delay rate %, and macro-region for each seller origin state."""
        df = DataStore.df()
        ascending = sort_order == "asc"
        result = _delay_by_group(df, "seller_state", min_orders, ascending)

        national_rate = df["foi_atraso"].mean() * 100

        header = (
            "## Delay Rate by Seller State\n\n"
            f"**National average:** {national_rate:.2f}%\n\n"
        )
        return header + format_markdown_table(result)

    @mcp.tool()
    def get_interstate_vs_intrastate_analysis() -> str:
        """Compare delay rates, freight costs, and distances between interstate (seller_state != customer_state) and intrastate routes."""
        df = DataStore.df()

        groups = df.groupby("rota_interestadual").agg(
            total_orders=("foi_atraso", "count"),
            delayed_orders=("foi_atraso", "sum"),
            avg_freight=("freight_value", "mean"),
            avg_distance_km=("distancia_haversine_km", "mean"),
        )
        groups["delay_rate_pct"] = (groups["delayed_orders"] / groups["total_orders"] * 100).round(2)
        groups["avg_freight"] = groups["avg_freight"].round(2)
        groups["avg_distance_km"] = groups["avg_distance_km"].round(1)

        total = len(df)
        interstate_count = int(groups.loc[1, "total_orders"])
        interstate_pct = interstate_count / total * 100

        intra = groups.loc[0]
        inter = groups.loc[1]

        return (
            "## Interstate vs Intrastate Route Analysis\n\n"
            f"| Metric | Intrastate | Interstate |\n"
            f"|--------|----------:|-----------:|\n"
            f"| Total orders | {int(intra['total_orders']):,} | {int(inter['total_orders']):,} |\n"
            f"| Delayed orders | {int(intra['delayed_orders']):,} | {int(inter['delayed_orders']):,} |\n"
            f"| Delay rate | {intra['delay_rate_pct']:.2f}% | {inter['delay_rate_pct']:.2f}% |\n"
            f"| Avg freight (BRL) | R${intra['avg_freight']:.2f} | R${inter['avg_freight']:.2f} |\n"
            f"| Avg distance (km) | {intra['avg_distance_km']:.1f} | {inter['avg_distance_km']:.1f} |\n\n"
            f"- **{interstate_pct:.1f}%** of orders are interstate\n"
            f"- Interstate routes have **{inter['delay_rate_pct'] - intra['delay_rate_pct']:.1f}pp** higher delay rate\n"
        )

    @mcp.tool()
    def get_route_heatmap_data(
        min_orders: int = 50,
        seller_state: str | None = None,
        customer_state: str | None = None,
    ) -> str:
        """Get a seller_state × customer_state delay rate pivot table for heatmap visualization. Filter by min_orders, seller_state, or customer_state."""
        df = DataStore.df()

        if seller_state:
            df = df[df["seller_state"] == seller_state.upper()]
        if customer_state:
            df = df[df["customer_state"] == customer_state.upper()]

        # Build pivot with counts for filtering
        pivot_count = pd.pivot_table(
            df, index="seller_state", columns="customer_state",
            values="foi_atraso", aggfunc="count", fill_value=0,
        )
        pivot_rate = pd.pivot_table(
            df, index="seller_state", columns="customer_state",
            values="foi_atraso", aggfunc="mean", fill_value=None,
        )

        # Mask cells with fewer than min_orders
        mask = pivot_count < min_orders
        pivot_rate = pivot_rate.where(~mask)
        pivot_rate = (pivot_rate * 100).round(2)

        # Drop columns/rows that are all NaN
        pivot_rate = pivot_rate.dropna(axis=0, how="all").dropna(axis=1, how="all")

        if pivot_rate.empty:
            return f"No routes found with >= {min_orders} orders."

        header = (
            "## Route Delay Rate Heatmap (seller → customer)\n\n"
            f"*Minimum {min_orders} orders per route*\n\n"
        )
        return header + pivot_rate.to_markdown()

    @mcp.tool()
    def get_macro_region_analysis() -> str:
        """Get delay rate analysis by macro-region (Norte, Nordeste, Sudeste, Sul, Centro-Oeste), from both customer and seller perspectives."""
        df = DataStore.df()

        # Map states to macro regions
        cust_region = df["customer_state"].map(STATE_TO_REGION)
        sell_region = df["seller_state"].map(STATE_TO_REGION)

        results = []
        for perspective, region_col, label in [
            ("Customer", cust_region, "Destination"),
            ("Seller", sell_region, "Origin"),
        ]:
            agg = df.groupby(region_col)["foi_atraso"].agg(
                total_orders="count",
                delayed_orders="sum",
            )
            agg["delay_rate_pct"] = (agg["delayed_orders"] / agg["total_orders"] * 100).round(2)
            agg = agg.sort_values("delay_rate_pct", ascending=False).reset_index()
            agg = agg.rename(columns={agg.columns[0]: "macro_region"})
            results.append((label, agg))

        lines = ["## Macro-Region Analysis\n"]
        for label, agg in results:
            lines.append(f"### By {label} Region\n")
            lines.append(format_markdown_table(agg))
            lines.append("")

        return "\n".join(lines)

    @mcp.tool()
    def get_distance_analysis(n_bins: int = 10) -> str:
        """Analyze delay rates by distance bins (haversine km). Shows how delivery distance correlates with delay probability."""
        df = DataStore.df()
        valid = df.dropna(subset=["distancia_haversine_km"])
        nan_count = len(df) - len(valid)

        bins = pd.cut(valid["distancia_haversine_km"], bins=n_bins)
        agg = valid.groupby(bins, observed=True)["foi_atraso"].agg(
            total_orders="count",
            delayed_orders="sum",
        )
        agg["delay_rate_pct"] = (agg["delayed_orders"] / agg["total_orders"] * 100).round(2)
        agg = agg.reset_index()
        agg["distancia_haversine_km"] = agg["distancia_haversine_km"].astype(str)

        pearson = valid["distancia_haversine_km"].corr(valid["foi_atraso"])

        header = (
            "## Distance vs Delay Analysis\n\n"
            f"- **Pearson correlation:** {pearson:.4f}\n"
            f"- **Rows with NaN distance:** {nan_count:,}\n\n"
        )
        return header + format_markdown_table(agg)

    @mcp.tool()
    def get_worst_routes(
        top_n: int = 15,
        min_orders: int = 50,
    ) -> str:
        """Get the worst seller→customer state routes by delay rate. Only includes routes with sufficient order volume (min_orders)."""
        df = DataStore.df()

        route_col = df["seller_state"] + " → " + df["customer_state"]
        agg = df.groupby(route_col)["foi_atraso"].agg(
            total_orders="count",
            delayed_orders="sum",
        )
        agg["delay_rate_pct"] = (agg["delayed_orders"] / agg["total_orders"] * 100).round(2)
        agg = agg[agg["total_orders"] >= min_orders]
        agg = agg.sort_values("delay_rate_pct", ascending=False).head(top_n)
        agg = agg.reset_index()
        agg = agg.rename(columns={agg.columns[0]: "route"})

        header = (
            f"## Top {top_n} Worst Routes (by delay rate)\n\n"
            f"*Minimum {min_orders} orders per route*\n\n"
        )
        return header + format_markdown_table(agg)

    @mcp.tool()
    def calculate_haversine_distance(
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
