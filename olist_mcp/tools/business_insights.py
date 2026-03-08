"""Business Insights Tools (2 tools).

Executive summary and seller profiling.
"""

import pandas as pd
from fastmcp import FastMCP

from olist_mcp.cache import DataStore
from olist_mcp.utils.state_mappings import STATE_TO_REGION


def register(mcp: FastMCP) -> None:
    """Register 2 business insights tools on the MCP server."""

    @mcp.tool()
    def get_business_summary() -> str:
        """Get the 5 key business findings from the EDA analysis: geographic concentration, route impact, feature dominance, model performance, and actionable recommendations."""
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
            "### 4. CatBoost V5 Model\n\n"
            "- ROC-AUC: **0.8454** (19 features, threshold 0.54)\n"
            "- Use `predict_delay_catboost` for individual predictions\n"
            "- Use `get_catboost_model_info` for full metrics\n\n"
            "### 5. Actionable Recommendations\n\n"
            "- Audit top worst sellers (`group_by_metrics` by seller_id + mean:foi_atraso)\n"
            "- Create SLAs for interstate routes to Nordeste\n"
            "- Integrate delay prediction into fulfillment alerts\n"
        )

    @mcp.tool()
    def get_seller_profile(seller_id: str) -> str:
        """Get a detailed profile of a specific seller: state, order count, delay rate, ranking percentile, dispatch speed, freight, historical delay rate, and top customer states."""
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

        # Historical delay rate from dataset
        hist_delay = seller_data["historico_atraso_seller"].iloc[0]
        hist_str = f"{hist_delay:.2%}" if pd.notna(hist_delay) else "N/A"

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

        return (
            f"## Seller Profile: `{seller_id[:12]}...`\n\n"
            f"- **State:** {state} ({region})\n"
            f"- **Total orders:** {total:,}\n"
            f"- **Delayed orders:** {delayed:,}\n"
            f"- **Delay rate:** {delay_rate:.2f}%\n"
            f"- **Historical delay rate:** {hist_str}\n"
            f"- **Ranking:** worse than {rank:.0f}% of sellers\n"
            f"- **Avg dispatch speed:** {avg_speed:.1f} days\n"
            f"- **Avg freight:** R${avg_freight:.2f}\n\n"
            "### Top 5 Customer States\n\n"
            "| State | Orders | % |\n"
            "|-------|-------:|--:|\n"
            + states_lines
        )
