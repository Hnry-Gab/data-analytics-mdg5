"""MCP-03: ML Model & Prediction Tools (7 tools).

Provides model status, predictions, metrics, feature importance,
hyperparameters, state encoding, and seller improvement simulation.
All tools degrade gracefully when the model file is unavailable.
"""

from fastmcp import FastMCP

from olist_mcp.cache import DataStore
from olist_mcp.config import DATASET_TREINO, MODEL_PKL
from olist_mcp.utils.formatters import format_json_safe, format_markdown_table

# Spec-defined baseline hyperparameters (from spec/model_spec.md)
_SPEC_HYPERPARAMETERS = {
    "objective": "binary:logistic",
    "eval_metric": "auc",
    "scale_pos_weight": 13.76,
    "max_depth": 6,
    "learning_rate": 0.1,
    "n_estimators": 200,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "random_state": 42,
}

# Training feature order (must match model training)
_FEATURE_ORDER = [
    "velocidade_lojista_dias",
    "distancia_haversine_km",
    "freight_value",
    "rota_interestadual",
    "customer_state_encoded",
    "seller_state_encoded",
]


def _model_unavailable_msg() -> str:
    """Standard response when model file is not available."""
    return (
        "## Model Unavailable\n\n"
        f"Model file not found at: `{MODEL_PKL.relative_to(MODEL_PKL.parent.parent)}`\n\n"
        "### How to Train\n\n"
        f"Training dataset available at: `{DATASET_TREINO.name}` "
        f"({DATASET_TREINO.exists() and 'exists' or 'missing'})\n\n"
        "### Alternative Tools (no model needed)\n\n"
        "- `get_correlation_table` — Pearson ranking as feature importance proxy\n"
        "- `get_delay_rate_by_customer_state` — Geographic risk assessment\n"
        "- `get_state_encoding_map` — Target-encoded state values\n"
        "- `get_business_summary` — Executive insights from EDA\n"
    )


def _get_state_encoding() -> dict[str, float]:
    """Compute and return state → delay_rate mapping (target encoding)."""
    df = DataStore.df()
    return df.groupby("customer_state")["foi_atraso"].mean().to_dict()


def _risk_level(prob: float) -> str:
    """Classify delay probability into risk levels."""
    if prob < 0.1:
        return "Low"
    if prob < 0.3:
        return "Medium-Low"
    if prob < 0.5:
        return "Medium"
    if prob < 0.7:
        return "Medium-High"
    return "High"


def register(mcp: FastMCP) -> None:
    """Register all 7 ML model tools on the MCP server."""

    @mcp.tool()
    def get_model_status() -> str:
        """Get the XGBoost model status: availability, file path, class, and hyperparameters. Degrades gracefully if model file is missing."""
        model = DataStore.model()

        if model is None:
            return _model_unavailable_msg()

        import os

        file_size = os.path.getsize(MODEL_PKL) / (1024 * 1024)
        params = model.get_params() if hasattr(model, "get_params") else _SPEC_HYPERPARAMETERS

        params_lines = ""
        for k, v in sorted(params.items()):
            params_lines += f"| `{k}` | `{v}` |\n"

        return (
            "## Model Status: Available\n\n"
            f"- **File:** `{MODEL_PKL.relative_to(MODEL_PKL.parent.parent)}`\n"
            f"- **Size:** {file_size:.1f} MB\n"
            f"- **Class:** `{type(model).__name__}`\n\n"
            "### Hyperparameters\n\n"
            "| Parameter | Value |\n"
            "|-----------|-------|\n"
            + params_lines
        )

    @mcp.tool()
    def predict_delay_probability(
        velocidade_lojista_dias: float,
        distancia_haversine_km: float,
        freight_value: float,
        rota_interestadual: int,
        customer_state_encoded: float,
        seller_state_encoded: float,
    ) -> str:
        """Predict delay probability for a single order. Requires 6 features. Returns probability, risk level, and preventive actions. Degrades gracefully if model unavailable."""
        model = DataStore.model()

        if model is None:
            return _model_unavailable_msg()

        import numpy as np

        features = np.array([[
            velocidade_lojista_dias,
            distancia_haversine_km,
            freight_value,
            rota_interestadual,
            customer_state_encoded,
            seller_state_encoded,
        ]])

        prob = float(model.predict_proba(features)[0, 1])
        binary = int(prob >= 0.5)
        risk = _risk_level(prob)

        actions = []
        if velocidade_lojista_dias > 3:
            actions.append("Reduce seller dispatch time to under 3 days")
        if rota_interestadual == 1:
            actions.append("Consider priority routing for interstate shipment")
        if distancia_haversine_km > 1000:
            actions.append("Use express carrier for long-distance route")
        if customer_state_encoded > 0.10:
            actions.append("High-risk destination state — monitor closely")
        if not actions:
            actions.append("No immediate actions required — low risk profile")

        return (
            "## Delay Prediction\n\n"
            f"- **Probability:** {prob:.2%}\n"
            f"- **Binary prediction:** {binary} ({'DELAYED' if binary else 'ON TIME'})\n"
            f"- **Risk level:** {risk}\n\n"
            "### Input Features\n\n"
            "| Feature | Value |\n"
            "|---------|------:|\n"
            f"| velocidade_lojista_dias | {velocidade_lojista_dias:.2f} |\n"
            f"| distancia_haversine_km | {distancia_haversine_km:.1f} |\n"
            f"| freight_value | R${freight_value:.2f} |\n"
            f"| rota_interestadual | {rota_interestadual} |\n"
            f"| customer_state_encoded | {customer_state_encoded:.4f} |\n"
            f"| seller_state_encoded | {seller_state_encoded:.4f} |\n\n"
            "### Preventive Actions\n\n"
            + "\n".join(f"- {a}" for a in actions) + "\n"
        )

    @mcp.tool()
    def get_model_metrics() -> str:
        """Get the baseline model metrics from EDA benchmarks: ROC-AUC, Recall, F1-Score targets and actual values."""
        return (
            "## Model Metrics\n\n"
            "| Metric | Baseline (EDA) | Minimum Target |\n"
            "|--------|---------------:|---------------:|\n"
            "| ROC-AUC | **0.7452** | ≥ 0.70 |\n"
            "| Recall | 55-70% (est.) | ≥ 0.60 |\n"
            "| F1-Score | ~0.50 (est.) | ≥ 0.50 |\n\n"
            "### Notes\n\n"
            "- Baseline from notebook-02 (normalization study)\n"
            "- `scale_pos_weight=13.76` used for class balancing\n"
            "- Normalization showed minimal delta (+0.0014 ROC-AUC) — not applied\n"
            "- Final metrics pending training on complete dataset\n\n"
            "> **Important:** Accuracy is a prohibited metric due to class imbalance (93.4% / 6.6%).\n"
        )

    @mcp.tool()
    def get_feature_importance(top_n: int = 10) -> str:
        """Get feature importance ranking. Uses model feature_importances_ if available, falls back to Pearson correlation ranking from EDA."""
        model = DataStore.model()

        if model is not None and hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
            total = sum(importances)
            rows = sorted(
                zip(_FEATURE_ORDER, importances),
                key=lambda x: x[1],
                reverse=True,
            )[:top_n]

            lines = ["## Feature Importance (from trained model)\n"]
            lines.append("| Rank | Feature | Importance | % of Total |")
            lines.append("|-----:|---------|----------:|-----------:|")
            for i, (feat, imp) in enumerate(rows, 1):
                lines.append(f"| {i} | `{feat}` | {imp:.4f} | {imp / total * 100:.1f}% |")
            return "\n".join(lines)

        # Fallback: use correlation table as proxy
        corr = DataStore.correlations()
        corr_sorted = corr.sort_values("|Valor|", ascending=False).head(top_n)

        lines = [
            "## Feature Importance (Correlation Proxy)\n",
            "*Model not available — using Pearson/Cramér's V as importance proxy*\n",
        ]
        lines.append(format_markdown_table(corr_sorted))
        return "\n".join(lines)

    @mcp.tool()
    def get_model_hyperparameters() -> str:
        """Get the XGBoost model hyperparameters. Returns actual params from trained model if available, otherwise returns spec-defined baseline values."""
        model = DataStore.model()

        if model is not None and hasattr(model, "get_params"):
            params = model.get_params()
            source = "trained model"
        else:
            params = _SPEC_HYPERPARAMETERS
            source = "spec/model_spec.md (model not loaded)"

        lines = [
            f"## XGBoost Hyperparameters\n",
            f"*Source: {source}*\n",
            "| Parameter | Value |",
            "|-----------|------:|",
        ]
        for k, v in sorted(params.items()):
            lines.append(f"| `{k}` | {v} |")

        return "\n".join(lines)

    @mcp.tool()
    def get_state_encoding_map(state: str | None = None) -> str:
        """Get the target-encoding map (delay rate per state). Used as input features for the ML model. Optionally filter to a single state."""
        encoding = _get_state_encoding()

        if state is not None:
            state = state.upper().strip()
            if state not in encoding:
                valid = ", ".join(sorted(encoding.keys()))
                return f"**Error:** State `{state}` not found. Valid states: {valid}"
            return (
                f"## State Encoding: {state}\n\n"
                f"- **Delay rate (target encoding):** {encoding[state]:.4f} "
                f"({encoding[state] * 100:.2f}%)\n"
            )

        # Full map sorted by delay rate desc
        sorted_enc = sorted(encoding.items(), key=lambda x: x[1], reverse=True)

        lines = [
            "## State Target Encoding Map\n",
            "*Values = delay rate per state, used as model input features*\n",
            "| State | Encoded Value | Delay Rate (%) |",
            "|-------|-------------:|---------------:|",
        ]
        for st, val in sorted_enc:
            lines.append(f"| {st} | {val:.4f} | {val * 100:.2f}% |")

        return "\n".join(lines)

    @mcp.tool()
    def simulate_seller_improvement(
        current_velocidade_dias: float,
        target_velocidade_dias: float,
        distancia_haversine_km: float,
        freight_value: float,
        rota_interestadual: int,
        customer_state_encoded: float,
        seller_state_encoded: float,
    ) -> str:
        """Simulate the impact of reducing seller dispatch time on delay probability. Shows current vs target probability and business impact narrative."""
        model = DataStore.model()

        if model is None:
            return _model_unavailable_msg()

        import numpy as np

        def _predict(speed: float) -> float:
            features = np.array([[
                speed, distancia_haversine_km, freight_value,
                rota_interestadual, customer_state_encoded, seller_state_encoded,
            ]])
            return float(model.predict_proba(features)[0, 1])

        current_prob = _predict(current_velocidade_dias)
        target_prob = _predict(target_velocidade_dias)
        reduction_pp = (current_prob - target_prob) * 100
        prevented_per_10k = int(reduction_pp / 100 * 10000)

        return (
            "## Seller Improvement Simulation\n\n"
            f"### Dispatch Speed Change: {current_velocidade_dias:.1f} → "
            f"{target_velocidade_dias:.1f} days\n\n"
            "| Metric | Current | Target | Change |\n"
            "|--------|--------:|-------:|-------:|\n"
            f"| Delay probability | {current_prob:.2%} | {target_prob:.2%} | "
            f"{'-' if reduction_pp > 0 else '+'}{abs(reduction_pp):.1f}pp |\n"
            f"| Risk level | {_risk_level(current_prob)} | {_risk_level(target_prob)} | — |\n\n"
            f"**Narrative:** Reducing dispatch time from {current_velocidade_dias:.1f} to "
            f"{target_velocidade_dias:.1f} days would lower delay probability from "
            f"{current_prob:.0%} to {target_prob:.0%} ({'-' if reduction_pp > 0 else '+'}"
            f"{abs(reduction_pp):.1f}pp)\n\n"
            f"**Business impact:** Preventing ~{prevented_per_10k:,} delays per 10,000 orders\n"
        )
