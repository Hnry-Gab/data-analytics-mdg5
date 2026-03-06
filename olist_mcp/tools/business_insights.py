"""MCP-04: Business Insights Tools (7 tools).

Exposes actionable business insights: seller/category rankings,
executive summary, growth recommendations, and pricing analysis.
"""

import pandas as pd
from fastmcp import FastMCP

from olist_mcp.cache import DataStore
from olist_mcp.utils.formatters import format_markdown_table
from olist_mcp.utils.state_mappings import STATE_TO_REGION


def register(mcp: FastMCP) -> None:
    """Register all 7 business insights tools on the MCP server."""

    @mcp.tool()
    def get_top_worst_sellers(
        top_n: int = 10,
        min_orders: int = 30,
    ) -> str:
        """Get the worst-performing sellers by delay rate. Only includes sellers with sufficient order volume for statistical validity."""
        df = DataStore.df()

        agg = df.groupby("seller_id").agg(
            seller_state=("seller_state", "first"),
            total_orders=("foi_atraso", "count"),
            delayed_orders=("foi_atraso", "sum"),
        )
        agg["delay_rate_pct"] = (agg["delayed_orders"] / agg["total_orders"] * 100).round(2)
        agg = agg[agg["total_orders"] >= min_orders]
        agg = agg.sort_values("delay_rate_pct", ascending=False).head(top_n)
        agg = agg.reset_index()

        header = (
            f"## Top {top_n} Worst Sellers (by delay rate)\n\n"
            f"*Minimum {min_orders} orders per seller*\n\n"
        )
        footer = (
            "\n\n> **Action:** These sellers should be audited operationally. "
            "Focus on dispatch speed (`velocidade_lojista_dias`) as the primary lever.\n"
        )
        return header + format_markdown_table(agg) + footer

    @mcp.tool()
    def get_top_worst_categories(
        top_n: int = 10,
        min_orders: int = 100,
    ) -> str:
        """Get the worst product categories by delay rate. Bulky/heavy categories (furniture, electronics) typically lead delays."""
        df = DataStore.df()

        agg = df.groupby("product_category_name")["foi_atraso"].agg(
            total_orders="count",
            delayed_orders="sum",
        )
        agg["delay_rate_pct"] = (agg["delayed_orders"] / agg["total_orders"] * 100).round(2)
        agg = agg[agg["total_orders"] >= min_orders]
        agg = agg.sort_values("delay_rate_pct", ascending=False).head(top_n)
        agg = agg.reset_index()

        header = (
            f"## Top {top_n} Worst Categories (by delay rate)\n\n"
            f"*Minimum {min_orders} orders per category*\n\n"
        )
        footer = (
            "\n\n> **Insight:** Bulky and specialty categories tend to have higher delay rates "
            "due to packaging complexity and carrier constraints.\n"
        )
        return header + format_markdown_table(agg) + footer

    @mcp.tool()
    def get_business_summary() -> str:
        """Get the 5 key business findings from the EDA analysis: geographic concentration, route impact, feature dominance, worst performers, and model readiness."""
        df = DataStore.df()

        national_rate = df["foi_atraso"].mean() * 100
        total = len(df)
        delayed = int(df["foi_atraso"].sum())

        # Geographic: worst state
        by_state = df.groupby("customer_state")["foi_atraso"].mean() * 100
        worst_state = by_state.idxmax()
        worst_rate = by_state.max()

        # Route impact
        inter = df[df["rota_interestadual"] == 1]["foi_atraso"].mean() * 100
        intra = df[df["rota_interestadual"] == 0]["foi_atraso"].mean() * 100
        inter_pct = (df["rota_interestadual"] == 1).mean() * 100

        # Feature
        pearson = df["velocidade_lojista_dias"].corr(df["foi_atraso"])

        return (
            "## Executive Business Summary\n\n"
            f"**National delay rate:** {national_rate:.2f}% "
            f"({delayed:,} / {total:,} orders)\n\n"
            "---\n\n"
            "### 1. Geographic Concentration\n\n"
            f"- **{worst_state}** leads with {worst_rate:.2f}% delay rate "
            f"— {worst_rate / national_rate:.1f}x the national average\n"
            f"- {worst_state}, MA, SE (Nordeste) are the worst-performing states\n\n"
            "### 2. Route Impact\n\n"
            f"- Interstate routes: **{inter:.2f}%** delay vs intrastate: **{intra:.2f}%**\n"
            f"- {inter_pct:.0f}% of orders are interstate\n\n"
            "### 3. Feature Dominance\n\n"
            f"- `velocidade_lojista_dias` is the strongest predictor (Pearson **{pearson:+.4f}**)\n"
            "- Reducing seller dispatch time is the primary business lever\n\n"
            "### 4. Worst Performers\n\n"
            "- Use `get_top_worst_sellers` and `get_top_worst_categories` for detailed rankings\n\n"
            "### 5. Model Readiness\n\n"
            "- XGBoost baseline ROC-AUC: **0.7452** (above 0.70 target)\n"
            "- Model ready for production after final validation\n"
        )

    @mcp.tool()
    def get_growth_recommendations() -> str:
        """Get a structured action plan with 4 prioritized recommendations for reducing delivery delays, from operational optimization to proactive prediction."""
        df = DataStore.df()
        avg_speed = df["velocidade_lojista_dias"].mean()

        return (
            "## Growth Recommendations — Logistics Optimization\n\n"
            "### Priority 1 — Operational Optimization (High Impact)\n\n"
            f"- Reduce average `velocidade_lojista_dias` from **{avg_speed:.1f} days** to <2 days\n"
            "- **Benefit:** Estimated -2pp in national delay rate\n"
            "- **Action:** Audit dispatch processes for top 20 worst sellers\n\n"
            "### Priority 2 — Regional Strategy (Medium Impact)\n\n"
            "- Create specific SLAs for interstate routes to Nordeste\n"
            "- **Benefit:** -2pp in delay rate for these routes\n"
            "- **Action:** Prioritize carriers for AL, MA, SE destinations\n\n"
            "### Priority 3 — Category Handling (Low Impact)\n\n"
            "- Review packaging and handling for bulky/heavy categories\n"
            "- **Benefit:** -0.5pp in delay rate for problematic categories\n"
            "- **Action:** Operator training, optimize packaging guidelines\n\n"
            "### Priority 4 — Proactive Prediction (Differentiator)\n\n"
            "- Implement alerts when `delay_probability > 40%`\n"
            "- **Benefit:** Early customer notification, reduced churn\n"
            "- **Action:** Integrate XGBoost model into fulfillment system\n"
        )

    @mcp.tool()
    def get_seller_profile(seller_id: str) -> str:
        """Get a detailed profile of a specific seller: state, order count, delay rate, ranking percentile, dispatch speed, freight, and top customer states."""
        df = DataStore.df()
        seller_data = df[df["seller_id"] == seller_id]

        if seller_data.empty:
            return (
                f"**Error:** Seller `{seller_id}` not found.\n\n"
                f"Total sellers in dataset: {df['seller_id'].nunique():,}"
            )

        total = len(seller_data)
        delayed = int(seller_data["foi_atraso"].sum())
        delay_rate = delayed / total * 100
        state = seller_data["seller_state"].iloc[0]
        region = STATE_TO_REGION.get(state, "Unknown")
        avg_speed = seller_data["velocidade_lojista_dias"].mean()
        avg_freight = seller_data["freight_value"].mean()

        # Ranking percentile among all sellers
        all_sellers = df.groupby("seller_id")["foi_atraso"].agg(["count", "mean"])
        all_sellers = all_sellers[all_sellers["count"] >= 10]
        if seller_id in all_sellers.index:
            rank = (all_sellers["mean"] <= all_sellers.loc[seller_id, "mean"]).mean() * 100
        else:
            rank = float("nan")

        # Top 5 customer states
        top_states = seller_data["customer_state"].value_counts().head(5)
        states_lines = ""
        for st, count in top_states.items():
            states_lines += f"| {st} | {count:,} | {count / total * 100:.1f}% |\n"

        # Check if on worst list
        worst_threshold = df.groupby("seller_id")["foi_atraso"].agg(["count", "mean"])
        worst_threshold = worst_threshold[worst_threshold["count"] >= 30]
        is_worst = False
        if seller_id in worst_threshold.index:
            top_10_rate = worst_threshold["mean"].nlargest(10).min()
            is_worst = worst_threshold.loc[seller_id, "mean"] >= top_10_rate

        status = "**On worst sellers list**" if is_worst else "Normal"

        return (
            f"## Seller Profile: `{seller_id[:12]}...`\n\n"
            f"- **State:** {state} ({region})\n"
            f"- **Total orders:** {total:,}\n"
            f"- **Delayed orders:** {delayed:,}\n"
            f"- **Delay rate:** {delay_rate:.2f}%\n"
            f"- **Ranking:** worse than {rank:.0f}% of sellers\n"
            f"- **Avg dispatch speed:** {avg_speed:.1f} days\n"
            f"- **Avg freight:** R${avg_freight:.2f}\n"
            f"- **Status:** {status}\n\n"
            "### Top 5 Customer States\n\n"
            "| State | Orders | % |\n"
            "|-------|-------:|--:|\n"
            + states_lines
        )

    @mcp.tool()
    def get_national_delay_rate() -> str:
        """Get the national delay rate with comparative context: best/worst states relative to national average."""
        df = DataStore.df()

        total = len(df)
        delayed = int(df["foi_atraso"].sum())
        on_time = total - delayed
        national = delayed / total * 100

        by_state = df.groupby("customer_state")["foi_atraso"].mean() * 100
        worst = by_state.nlargest(3)
        best = by_state.nsmallest(3)

        worst_lines = ""
        for state, rate in worst.items():
            worst_lines += f"- **{state}:** {rate:.2f}% ({rate / national:.2f}x national)\n"

        best_lines = ""
        for state, rate in best.items():
            best_lines += f"- **{state}:** {rate:.2f}% ({rate / national:.2f}x national)\n"

        return (
            "## National Delay Rate\n\n"
            f"- **Rate:** {national:.2f}%\n"
            f"- **Total orders:** {total:,}\n"
            f"- **Delayed:** {delayed:,}\n"
            f"- **On time:** {on_time:,}\n\n"
            "### Worst States\n\n"
            + worst_lines
            + "\n### Best States\n\n"
            + best_lines
        )

    @mcp.tool()
    def get_price_freight_analysis() -> str:
        """Analyze the relationship between price, freight cost, and delivery delays. Shows that price is a weak predictor of delay."""
        df = DataStore.df()

        by_class = df.groupby("foi_atraso")[["price", "freight_value", "frete_ratio"]].mean()
        on_time = by_class.loc[0]
        late = by_class.loc[1]

        p_price = df["price"].corr(df["foi_atraso"])
        p_freight = df["freight_value"].corr(df["foi_atraso"])
        p_ratio = df["frete_ratio"].corr(df["foi_atraso"])

        return (
            "## Price & Freight Analysis by Delay Class\n\n"
            "| Metric | On Time | Delayed | Difference |\n"
            "|--------|--------:|--------:|-----------:|\n"
            f"| Avg Price (R$) | {on_time['price']:.2f} | {late['price']:.2f} | "
            f"+{late['price'] - on_time['price']:.2f} |\n"
            f"| Avg Freight (R$) | {on_time['freight_value']:.2f} | {late['freight_value']:.2f} | "
            f"+{late['freight_value'] - on_time['freight_value']:.2f} |\n"
            f"| Freight/Price Ratio | {on_time['frete_ratio']:.2f} | {late['frete_ratio']:.2f} | "
            f"+{late['frete_ratio'] - on_time['frete_ratio']:.2f} |\n\n"
            "### Correlations with `foi_atraso`\n\n"
            f"- `price`: {p_price:+.4f} (weak)\n"
            f"- `freight_value`: {p_freight:+.4f} (weak)\n"
            f"- `frete_ratio`: {p_ratio:+.4f} (very weak)\n\n"
            "> **Insight:** More expensive products do NOT receive delivery priority. "
            "Price/freight correlations are minimal — focus optimization on dispatch speed instead.\n"
        )
