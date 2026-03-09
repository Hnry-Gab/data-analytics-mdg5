"""MCP-07: EDA & Visualization Tools (7 tools).

Provides access to pre-built EDA charts (static PNGs, interactive HTML)
and generates live charts via Plotly + Kaleido.
"""

import base64

import plotly.express as px
import plotly.graph_objects as go
from fastmcp import FastMCP

from olist_mcp.cache import DataStore
from olist_mcp.config import IMAGES_DIR, HTML_DIR


def _fig_to_base64(fig: go.Figure) -> str | None:
    """Convert a Plotly figure to base64 PNG. Returns None if kaleido is unavailable."""
    try:
        png_bytes = fig.to_image(format="png")
        return base64.b64encode(png_bytes).decode("utf-8")
    except Exception:
        return None

# Static chart registry: keyword → (filename, description)
_STATIC_CHARTS: dict[str, tuple[str, str]] = {
    "correlacao": (
        "Força da correlação entre feature candidata vs foi_atraso.png",
        "Feature correlations bar chart — velocidade_lojista_dias at top (~0.21)",
    ),
    "pie_atraso": (
        "Relação entre atrasados e entregues no prazo.png",
        "Pie chart: 93.23% on time vs 6.77% delayed",
    ),
    "rota": (
        "Taxa de atraso - Rota Intraestadual vs Interestadual.png",
        "Interstate (~8%) vs intrastate (~4.5%) delay rate comparison",
    ),
    "vendedor": (
        "Taxa de atraso por Estado DO VENDEDOR.png",
        "Bar chart: delay rate by seller state (27 UFs)",
    ),
    "cliente": (
        "Taxa de atraso por estado DO CLIENTE.png",
        "Bar chart: delay rate by customer state — AL=20.84% highlighted",
    ),
    "categorias": (
        "Top 10 categorias com maior taxa de atraso.png",
        "Top 10 highest-risk product categories",
    ),
}

# Interactive HTML chart registry
_HTML_CHARTS: dict[str, tuple[str, str]] = {
    "eda_1_correlacoes": (
        "eda_1_correlacoes.html",
        "Interactive bar chart of feature correlations",
    ),
    "eda_2_heatmap_features": (
        "eda_2_heatmap_features.html",
        "Full 16x16 feature correlation heatmap",
    ),
    "eda_3_piores_categorias": (
        "eda_3_piores_categorias.html",
        "Interactive bar chart of worst categories with hover details",
    ),
    "eda_4_heatmap_rotas": (
        "eda_4_heatmap_rotas.html",
        "Heatmap: seller_state x customer_state delay rates",
    ),
    "eda_5_heatmap_regioes": (
        "eda_5_heatmap_regioes.html",
        "Heatmap: macro-region x macro-region delay rates",
    ),
}


def register(mcp: FastMCP) -> None:
    """Register all 7 visualization tools on the MCP server."""

    @mcp.tool()
    def list_available_charts() -> str:
        """List all available EDA charts: static PNGs and interactive HTML files."""
        lines = ["## Available Charts\n"]

        # Static PNGs
        lines.append("### Static Charts (PNG)\n")
        lines.append(f"*Directory: `notebooks/final_analysis/images/`*\n")
        for i, (key, (filename, desc)) in enumerate(_STATIC_CHARTS.items(), 1):
            exists = (IMAGES_DIR / filename).exists()
            status = "available" if exists else "missing"
            lines.append(f"{i}. **`{key}`** — {desc}")
            lines.append(f"   - File: `{filename}` [{status}]")
            lines.append(f"   - Access: `get_chart_as_base64(chart_name=\"{key}\")`\n")

        # Interactive HTMLs
        lines.append("\n### Interactive Charts (HTML Plotly)\n")
        lines.append(f"*Directory: `notebooks/final_analysis/`*\n")
        for i, (key, (filename, desc)) in enumerate(_HTML_CHARTS.items(), 1):
            exists = (HTML_DIR / filename).exists()
            status = "available" if exists else "not generated"
            lines.append(f"{i}. **`{key}`** — {desc}")
            lines.append(f"   - File: `{filename}` [{status}]")
            lines.append(f"   - Access: `get_html_chart_content(chart_name=\"{key}\")`\n")

        # Live generation
        lines.append("\n### Live Generation (Plotly + Kaleido)\n")
        lines.append("Generate fresh charts from current data:\n")
        lines.append("- `generate_delay_by_state_chart(state_type, top_n)`")
        lines.append("- `generate_correlation_bar_chart(min_abs_correlation)`")
        lines.append("- `generate_route_heatmap(min_orders, level)`")
        lines.append("- `generate_time_series_chart(granularity)`")

        return "\n".join(lines)

    @mcp.tool()
    def get_chart_as_base64(chart_name: str) -> str:
        """Get a pre-built static EDA chart as a base64-encoded PNG. Supports partial matching on chart name keywords: correlacao, pie_atraso, rota, vendedor, cliente, categorias."""
        # Try exact match first
        match = _STATIC_CHARTS.get(chart_name)

        # Partial match fallback
        if match is None:
            matches = [
                (k, v) for k, v in _STATIC_CHARTS.items()
                if chart_name.lower() in k.lower()
            ]
            if len(matches) == 1:
                key, match = matches[0]
                chart_name = key
            elif len(matches) > 1:
                options = "\n".join(f"- `{k}`: {v[1]}" for k, v in matches)
                return (
                    f"**Multiple matches** for `{chart_name}`:\n\n{options}\n\n"
                    "Please use a more specific name."
                )
            else:
                available = "\n".join(
                    f"- `{k}`: {v[1]}" for k, v in _STATIC_CHARTS.items()
                )
                return (
                    f"**Error:** Chart `{chart_name}` not found.\n\n"
                    f"Available charts:\n{available}"
                )

        filename, description = match
        filepath = IMAGES_DIR / filename

        if not filepath.exists():
            return (
                f"**Error:** File not found: `{filepath}`\n\n"
                f"Chart `{chart_name}` is registered but the PNG file is missing."
            )

        png_bytes = filepath.read_bytes()
        b64 = base64.b64encode(png_bytes).decode("utf-8")

        return (
            f"## Chart: `{chart_name}`\n\n"
            f"- **Description:** {description}\n"
            f"- **File:** `{filename}`\n"
            f"- **MIME type:** image/png\n"
            f"- **Size:** {len(png_bytes):,} bytes\n\n"
            f"### Base64 PNG\n\n"
            f"```\n{b64}\n```"
        )

    @mcp.tool()
    def get_html_chart_content(chart_name: str) -> str:
        """Get the HTML content of an interactive Plotly chart. Available: eda_1_correlacoes, eda_2_heatmap_features, eda_3_piores_categorias, eda_4_heatmap_rotas, eda_5_heatmap_regioes."""
        match = _HTML_CHARTS.get(chart_name)

        if match is None:
            available = "\n".join(
                f"- `{k}`: {v[1]}" for k, v in _HTML_CHARTS.items()
            )
            return (
                f"**Error:** Chart `{chart_name}` not found.\n\n"
                f"Available interactive charts:\n{available}"
            )

        filename, description = match
        filepath = HTML_DIR / filename

        if not filepath.exists():
            return (
                f"**Error:** File not found: `{filepath}`\n\n"
                f"Chart `{chart_name}` is registered but the HTML file has not been generated.\n"
                f"Run the EDA notebook to generate interactive charts."
            )

        html_content = filepath.read_text(encoding="utf-8")

        return (
            f"## Interactive Chart: `{chart_name}`\n\n"
            f"- **Description:** {description}\n"
            f"- **File:** `{filename}`\n"
            f"- **Size:** {len(html_content):,} chars\n\n"
            f"### HTML Content\n\n"
            f"```html\n{html_content[:5000]}\n```\n\n"
            + (f"*Truncated — full file is {len(html_content):,} chars*"
               if len(html_content) > 5000 else "")
        )

    @mcp.tool()
    def generate_delay_by_state_chart(
        state_type: str = "customer",
        top_n: int = 27,
    ) -> str:
        """Generate a live horizontal bar chart of delay rate by state using Plotly. Returns base64 PNG."""
        df = DataStore.df()
        col = f"{state_type}_state"

        if col not in df.columns:
            return f"**Error:** Invalid state_type `{state_type}`. Use 'customer' or 'seller'."

        agg = df.groupby(col)["foi_atraso"].agg(["mean", "count"]).reset_index()
        agg.columns = ["state", "delay_rate", "total_orders"]
        agg["delay_rate"] = (agg["delay_rate"] * 100).round(2)
        agg = agg.sort_values("delay_rate", ascending=True).tail(top_n)

        fig = px.bar(
            agg,
            x="delay_rate",
            y="state",
            orientation="h",
            title=f"Delay Rate by {state_type.title()} State (Top {top_n})",
            labels={"delay_rate": "Delay Rate (%)", "state": "State"},
            color="delay_rate",
            color_continuous_scale="RdYlGn_r",
        )
        fig.update_layout(height=max(400, top_n * 25), width=800)

        b64 = _fig_to_base64(fig)
        if b64 is None:
            return (
                f"## Delay Rate by {state_type.title()} State\n\n"
                f"- **States shown:** {len(agg)}\n"
                f"- **Kaleido unavailable** — returning Plotly JSON\n\n"
                f"```json\n{fig.to_json()}\n```"
            )

        return (
            f"## Delay Rate by {state_type.title()} State\n\n"
            f"- **Chart format:** PNG (base64)\n"
            f"- **States shown:** {len(agg)}\n"
            f"- **Generated live** from current dataset\n\n"
            f"### Base64 PNG\n\n"
            f"```\n{b64}\n```"
        )

    @mcp.tool()
    def generate_correlation_bar_chart(
        min_abs_correlation: float = 0.0,
    ) -> str:
        """Generate a live bar chart of feature correlations with foi_atraso. Filters by minimum absolute correlation value."""
        df = DataStore.df()
        numeric = df.select_dtypes(include="number")
        if "foi_atraso" not in numeric.columns:
            return "**Error:** `foi_atraso` column not found in numeric columns."
        corr = numeric.corr()["foi_atraso"].drop("foi_atraso", errors="ignore")
        corr_df_plot = corr.reset_index()
        corr_df_plot.columns = ["feature", "correlation"]

        # Filter by minimum absolute correlation
        corr_df_plot = corr_df_plot[
            corr_df_plot["correlation"].abs() >= min_abs_correlation
        ]
        corr_df_plot = corr_df_plot.sort_values("correlation", ascending=True)

        fig = px.bar(
            corr_df_plot,
            x="correlation",
            y="feature",
            orientation="h",
            title=f"Feature Correlations with foi_atraso (|r| ≥ {min_abs_correlation})",
            labels={"correlation": "Pearson Correlation", "feature": "Feature"},
            color="correlation",
            color_continuous_scale="RdBu",
            range_color=[-0.3, 0.3],
        )
        fig.update_layout(height=max(400, len(corr_df_plot) * 30), width=800)

        b64 = _fig_to_base64(fig)
        if b64 is None:
            return (
                "## Feature Correlations with `foi_atraso`\n\n"
                f"- **Features shown:** {len(corr_df_plot)}\n"
                f"- **Kaleido unavailable** — returning Plotly JSON\n\n"
                f"```json\n{fig.to_json()}\n```"
            )

        return (
            "## Feature Correlations with `foi_atraso`\n\n"
            f"- **Features shown:** {len(corr_df_plot)}\n"
            f"- **Min |correlation|:** {min_abs_correlation}\n"
            f"- **Generated live** from current dataset\n\n"
            f"### Base64 PNG\n\n"
            f"```\n{b64}\n```"
        )

    @mcp.tool()
    def generate_route_heatmap(
        min_orders: int = 50,
        level: str = "state",
    ) -> str:
        """Generate a heatmap of delay rates by seller×customer location. Level can be 'state' or 'macro_region'."""
        df = DataStore.df()

        from olist_mcp.utils.state_mappings import STATE_TO_REGION

        if level == "macro_region":
            df = df.copy()
            df["seller_region"] = df["seller_state"].map(STATE_TO_REGION)
            df["customer_region"] = df["customer_state"].map(STATE_TO_REGION)
            idx_col, col_col = "seller_region", "customer_region"
            title = "Delay Rate Heatmap: Seller Region × Customer Region"
        else:
            idx_col, col_col = "seller_state", "customer_state"
            title = "Delay Rate Heatmap: Seller State × Customer State"

        # Filter by min_orders
        counts = df.groupby([idx_col, col_col]).size()
        valid_pairs = counts[counts >= min_orders].index
        filtered = df.set_index([idx_col, col_col])
        filtered = filtered[filtered.index.isin(valid_pairs)].reset_index()

        if filtered.empty:
            return (
                f"**Error:** No routes with ≥{min_orders} orders. "
                f"Try lowering `min_orders`."
            )

        pivot = filtered.pivot_table(
            index=idx_col,
            columns=col_col,
            values="foi_atraso",
            aggfunc="mean",
        ) * 100

        fig = px.imshow(
            pivot.round(2),
            color_continuous_scale="RdYlGn_r",
            title=title,
            labels={"color": "Delay Rate (%)"},
        )
        fig.update_layout(width=900, height=700)

        b64 = _fig_to_base64(fig)
        if b64 is None:
            return (
                f"## {title}\n\n"
                f"- **Minimum orders per route:** {min_orders}\n"
                f"- **Kaleido unavailable** — returning Plotly JSON\n\n"
                f"```json\n{fig.to_json()}\n```"
            )

        return (
            f"## {title}\n\n"
            f"- **Minimum orders per route:** {min_orders}\n"
            f"- **Routes shown:** {pivot.notna().sum().sum()}\n"
            f"- **Generated live** from current dataset\n\n"
            f"### Base64 PNG\n\n"
            f"```\n{b64}\n```"
        )

    @mcp.tool()
    def generate_time_series_chart(
        granularity: str = "month",
    ) -> str:
        """Generate a dual-axis time series chart: total orders + delay rate over time. Granularity: 'day', 'week', or 'month'."""
        df = DataStore.df()

        freq_map = {"day": "D", "week": "W", "month": "ME"}
        freq = freq_map.get(granularity)
        if freq is None:
            return (
                f"**Error:** Invalid granularity `{granularity}`. "
                f"Options: day, week, month."
            )

        ts = (
            df.set_index("order_purchase_timestamp")
            .resample(freq)[["order_id", "foi_atraso"]]
            .agg({"order_id": "count", "foi_atraso": "sum"})
        )
        ts.columns = ["total_orders", "delayed_orders"]
        ts["delay_rate"] = (ts["delayed_orders"] / ts["total_orders"] * 100).round(2)

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=ts.index, y=ts["total_orders"],
                name="Total Orders", yaxis="y",
                marker_color="steelblue", opacity=0.6,
            ),
        )
        fig.add_trace(
            go.Scatter(
                x=ts.index, y=ts["delay_rate"],
                name="Delay Rate (%)", yaxis="y2",
                line={"color": "red", "width": 2},
            ),
        )
        fig.update_layout(
            title=f"Orders & Delay Rate Over Time ({granularity}ly)",
            xaxis_title="Date",
            yaxis={"title": "Total Orders", "side": "left"},
            yaxis2={"title": "Delay Rate (%)", "overlaying": "y", "side": "right"},
            width=900, height=500,
            legend={"x": 0.01, "y": 0.99},
        )

        b64 = _fig_to_base64(fig)
        if b64 is None:
            return (
                f"## Time Series: Orders & Delay Rate ({granularity}ly)\n\n"
                f"- **Granularity:** {granularity}\n"
                f"- **Periods:** {len(ts)}\n"
                f"- **Kaleido unavailable** — returning Plotly JSON\n\n"
                f"```json\n{fig.to_json()}\n```"
            )

        return (
            f"## Time Series: Orders & Delay Rate ({granularity}ly)\n\n"
            f"- **Granularity:** {granularity}\n"
            f"- **Periods:** {len(ts)}\n"
            f"- **Generated live** from current dataset\n\n"
            f"### Base64 PNG\n\n"
            f"```\n{b64}\n```"
        )
