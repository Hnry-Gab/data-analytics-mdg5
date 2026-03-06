"""MCP-05: Time Series & Temporal Analysis Tools (6 tools).

Analyzes delivery delay patterns across time: monthly, weekly,
seasonal trends, and seller dispatch speed distribution.
"""

import pandas as pd
from fastmcp import FastMCP

from olist_mcp.cache import DataStore
from olist_mcp.utils.formatters import format_json_safe, format_markdown_table

_WEEKDAY_NAMES = {
    0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
    4: "Friday", 5: "Saturday", 6: "Sunday",
}

_MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December",
}


def register(mcp: FastMCP) -> None:
    """Register all 6 temporal analysis tools on the MCP server."""

    @mcp.tool()
    def get_delay_rate_by_month() -> str:
        """Get delay rate by month (1-12) across all years. Shows monthly patterns and identifies peak/minimum delay months."""
        df = DataStore.df()
        month = df["order_purchase_timestamp"].dt.month

        agg = df.groupby(month)["foi_atraso"].agg(
            total_orders="count",
            delayed_orders="sum",
        )
        agg["delay_rate_pct"] = (agg["delayed_orders"] / agg["total_orders"] * 100).round(2)
        agg = agg.reset_index()
        agg = agg.rename(columns={"order_purchase_timestamp": "month"})
        agg["month_name"] = agg["month"].map(_MONTH_NAMES)

        peak = agg.loc[agg["delay_rate_pct"].idxmax()]
        minimum = agg.loc[agg["delay_rate_pct"].idxmin()]

        header = (
            "## Delay Rate by Month\n\n"
            f"- **Peak:** {peak['month_name']} ({peak['delay_rate_pct']:.2f}%)\n"
            f"- **Minimum:** {minimum['month_name']} ({minimum['delay_rate_pct']:.2f}%)\n\n"
        )
        return header + format_markdown_table(agg)

    @mcp.tool()
    def get_delay_rate_by_weekday() -> str:
        """Get delay rate by day of week (0=Monday to 6=Sunday). Confirms the weekend effect is weak (~1pp difference)."""
        df = DataStore.df()

        agg = df.groupby("dia_semana_compra")["foi_atraso"].agg(
            total_orders="count",
            delayed_orders="sum",
        )
        agg["delay_rate_pct"] = (agg["delayed_orders"] / agg["total_orders"] * 100).round(2)
        agg = agg.reset_index()
        agg["weekday_name"] = agg["dia_semana_compra"].map(_WEEKDAY_NAMES)

        spread = agg["delay_rate_pct"].max() - agg["delay_rate_pct"].min()

        header = (
            "## Delay Rate by Day of Week\n\n"
            f"- **Spread (max - min):** {spread:.2f}pp\n"
            f"- **Conclusion:** Weekend effect is {'weak' if spread < 2 else 'moderate'} "
            f"({spread:.1f}pp difference)\n\n"
        )
        return header + format_markdown_table(agg)

    @mcp.tool()
    def get_orders_over_time(
        granularity: str = "month",
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> str:
        """Get order volume and delay rate over time. Granularity: day, week, or month. Optional date filters (ISO format: YYYY-MM-DD)."""
        df = DataStore.df().set_index("order_purchase_timestamp").sort_index()

        if start_date:
            df = df[df.index >= start_date]
        if end_date:
            df = df[df.index <= end_date]

        freq_map = {"day": "D", "week": "W", "month": "ME"}
        freq = freq_map.get(granularity, "ME")

        resampled = df.resample(freq)["foi_atraso"].agg(
            total_orders="count",
            delayed_orders="sum",
        )
        resampled = resampled[resampled["total_orders"] > 0]
        resampled["delay_rate_pct"] = (
            resampled["delayed_orders"] / resampled["total_orders"] * 100
        ).round(2)
        resampled = resampled.reset_index()
        resampled["period"] = resampled["order_purchase_timestamp"].dt.strftime(
            "%Y-%m-%d" if granularity == "day" else "%Y-%m-%d" if granularity == "week" else "%Y-%m"
        )
        result = resampled[["period", "total_orders", "delayed_orders", "delay_rate_pct"]]

        avg = result["delay_rate_pct"].mean()
        min_row = result.loc[result["delay_rate_pct"].idxmin()]
        max_row = result.loc[result["delay_rate_pct"].idxmax()]

        header = (
            f"## Orders Over Time ({granularity}ly)\n\n"
            f"- **Average delay rate:** {avg:.2f}%\n"
            f"- **Min:** {min_row['period']} ({min_row['delay_rate_pct']:.2f}%)\n"
            f"- **Max:** {max_row['period']} ({max_row['delay_rate_pct']:.2f}%)\n\n"
        )
        return header + format_markdown_table(result)

    @mcp.tool()
    def get_date_range() -> str:
        """Get the temporal coverage of the dataset: first/last purchase dates, first/last delivery dates, and total period span."""
        df = DataStore.df()

        purchase_min = df["order_purchase_timestamp"].min()
        purchase_max = df["order_purchase_timestamp"].max()
        delivery_min = df["order_delivered_customer_date"].min()
        delivery_max = df["order_delivered_customer_date"].max()

        months_span = (purchase_max.year - purchase_min.year) * 12 + (
            purchase_max.month - purchase_min.month
        )

        return (
            "## Dataset Temporal Coverage\n\n"
            "### Purchase Dates\n\n"
            f"- **First order:** {purchase_min:%Y-%m-%d}\n"
            f"- **Last order:** {purchase_max:%Y-%m-%d}\n"
            f"- **Period:** {months_span} months\n\n"
            "### Delivery Dates\n\n"
            f"- **First delivery:** {delivery_min:%Y-%m-%d}\n"
            f"- **Last delivery:** {delivery_max:%Y-%m-%d}\n"
        )

    @mcp.tool()
    def get_velocidade_lojista_distribution() -> str:
        """Get the distribution of seller dispatch speed (velocidade_lojista_dias) with delay rates per bin. This is the strongest predictor (Pearson +0.2143)."""
        df = DataStore.df()
        valid = df.dropna(subset=["velocidade_lojista_dias"])

        bins = [float("-inf"), 1, 3, 7, 14, float("inf")]
        labels = ["0-1", "1-3", "3-7", "7-14", "14+"]

        valid = valid.copy()
        valid["speed_bin"] = pd.cut(
            valid["velocidade_lojista_dias"], bins=bins, labels=labels, include_lowest=True,
        )

        agg = valid.groupby("speed_bin", observed=True)["foi_atraso"].agg(
            total_orders="count",
            delayed_orders="sum",
        )
        agg["delay_rate_pct"] = (agg["delayed_orders"] / agg["total_orders"] * 100).round(2)
        agg = agg.reset_index()
        agg = agg.rename(columns={"speed_bin": "days_to_dispatch"})

        pearson = valid["velocidade_lojista_dias"].corr(valid["foi_atraso"])

        header = (
            "## Seller Dispatch Speed Distribution\n\n"
            f"- **Pearson correlation** with delay: **{pearson:.4f}**\n"
            "- **Insight:** Seller dispatch speed is the strongest single predictor of delay\n\n"
        )
        return header + format_markdown_table(agg)

    @mcp.tool()
    def get_seasonal_analysis(year: int | None = None) -> str:
        """Get quarterly seasonal patterns. Shows delay rates by quarter and highlights anomalies like Black Friday and holiday season. Optional year filter."""
        df = DataStore.df()

        if year is not None:
            df = df[df["order_purchase_timestamp"].dt.year == year]
            if df.empty:
                return f"No data for year {year}. Dataset covers 2016-2018."

        ts = df["order_purchase_timestamp"]
        quarter = ts.dt.quarter
        month = ts.dt.month

        # Quarterly analysis
        q_agg = df.groupby(quarter)["foi_atraso"].agg(
            total_orders="count",
            delayed_orders="sum",
        )
        q_agg["delay_rate_pct"] = (q_agg["delayed_orders"] / q_agg["total_orders"] * 100).round(2)
        q_agg = q_agg.reset_index()
        q_agg = q_agg.rename(columns={"order_purchase_timestamp": "quarter"})
        q_agg["quarter"] = q_agg["quarter"].apply(lambda q: f"Q{q}")

        # Monthly anomalies: November (Black Friday) and December (holidays)
        m_agg = df.groupby(month)["foi_atraso"].agg(
            total_orders="count",
            delayed_orders="sum",
        )
        m_agg["delay_rate_pct"] = (m_agg["delayed_orders"] / m_agg["total_orders"] * 100).round(2)

        national_rate = df["foi_atraso"].mean() * 100

        anomalies = []
        if 11 in m_agg.index:
            nov = m_agg.loc[11]
            anomalies.append(
                f"- **November (Black Friday):** {int(nov['total_orders']):,} orders, "
                f"{nov['delay_rate_pct']:.2f}% delay rate"
            )
        if 12 in m_agg.index:
            dec = m_agg.loc[12]
            anomalies.append(
                f"- **December (Holidays):** {int(dec['total_orders']):,} orders, "
                f"{dec['delay_rate_pct']:.2f}% delay rate"
            )

        year_label = f" ({year})" if year else " (2016-2018)"
        header = (
            f"## Seasonal Analysis{year_label}\n\n"
            f"**National delay rate:** {national_rate:.2f}%\n\n"
            "### By Quarter\n\n"
        )
        result = header + format_markdown_table(q_agg)

        if anomalies:
            result += "\n\n### Notable Periods\n\n" + "\n".join(anomalies) + "\n"

        return result
