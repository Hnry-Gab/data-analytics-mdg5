"""MCP-02: CatBoost ML Tools (4 tools).

Exposes CatBoost V5 delay prediction model with 19 features (15 numeric + 4 categorical).
ROC-AUC 0.8454, threshold 0.54.
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd
from fastmcp import FastMCP

from olist_mcp.cache import DataStore

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_MEDIAN_DISTANCE_KM = 431.94
_DEFAULT_MES = 6
_DEFAULT_DIA_SEMANA = 3

_RISK_LEVELS = [
    (0.20, "Low"),
    (0.40, "Medium-Low"),
    (0.54, "Medium"),
    (0.70, "Medium-High"),
    (1.01, "High"),
]


def _risk_level(prob: float) -> str:
    for threshold, label in _RISK_LEVELS:
        if prob < threshold:
            return label
    return "High"


def _derive_features(
    velocidade_lojista_dias: float,
    freight_value: float,
    price: float,
    product_weight_g: float,
    volume_cm3: float,
    total_itens_pedido: int,
    seller_state: str,
    customer_state: str,
    product_category_name: str,
    distancia_haversine_km: float | None,
    prazo_estimado_dias: int,
    historico_atraso_vendedor: float,
    qtd_pedidos_anteriores_vendedor: int,
    mes_compra: int | None,
    dia_semana_compra: int | None,
) -> dict:
    """Derive all 19 features from user inputs, computing internal features automatically."""
    if distancia_haversine_km is None:
        distancia_haversine_km = _MEDIAN_DISTANCE_KM
    if mes_compra is None:
        mes_compra = datetime.now().month
    if dia_semana_compra is None:
        dia_semana_compra = datetime.now().weekday()

    weight_kg = product_weight_g / 1000.0
    frete_por_kg = freight_value / weight_kg if weight_kg > 0 else 0.0
    semana_ano = mes_compra * 4
    eh_alta_temporada = 1 if mes_compra in (11, 12) else 0
    rota = f"{seller_state}-{customer_state}"

    return {
        "velocidade_lojista_dias": velocidade_lojista_dias,
        "distancia_haversine_km": distancia_haversine_km,
        "freight_value": freight_value,
        "volume_cm3": volume_cm3,
        "product_weight_g": product_weight_g,
        "price": price,
        "total_itens_pedido": total_itens_pedido,
        "prazo_estimado_dias": prazo_estimado_dias,
        "historico_atraso_vendedor": historico_atraso_vendedor,
        "qtd_pedidos_anteriores_vendedor": qtd_pedidos_anteriores_vendedor,
        "frete_por_kg": frete_por_kg,
        "mes_compra": mes_compra,
        "semana_ano": semana_ano,
        "dia_semana_compra": dia_semana_compra,
        "eh_alta_temporada": eh_alta_temporada,
        "seller_state": seller_state,
        "customer_state": customer_state,
        "rota": rota,
        "product_category_name": product_category_name,
    }


def _predict_single(features: dict, model, config: dict) -> tuple[float, str, str]:
    """Run a single prediction. Returns (probability, class_label, risk_level)."""
    feature_order = config["features_all"]
    row = [features[f] for f in feature_order]
    df_input = pd.DataFrame([row], columns=feature_order)

    cat_indices = config["cat_feature_indices"]
    for idx in cat_indices:
        col = feature_order[idx]
        df_input[col] = df_input[col].astype(str)

    prob = model.predict_proba(df_input)[0][1]
    threshold = config["threshold"]
    label = "Atrasado" if prob >= threshold else "No Prazo"
    risk = _risk_level(prob)
    return float(prob), label, risk


# ---------------------------------------------------------------------------
# Tool registration
# ---------------------------------------------------------------------------


def register(mcp: FastMCP) -> None:
    """Register 4 CatBoost ML tools on the MCP server."""

    @mcp.tool()
    def predict_delay_catboost(
        velocidade_lojista_dias: float,
        freight_value: float,
        price: float,
        product_weight_g: float,
        volume_cm3: float,
        total_itens_pedido: int = 1,
        seller_state: str = "SP",
        customer_state: str = "SP",
        product_category_name: str = "outros",
        distancia_haversine_km: float | None = None,
        prazo_estimado_dias: int = 15,
        historico_atraso_vendedor: float = 0.07,
        qtd_pedidos_anteriores_vendedor: int = 50,
        mes_compra: int | None = None,
        dia_semana_compra: int | None = None,
    ) -> str:
        """Predict delay probability for a single order using CatBoost V5 model.

        Required: velocidade_lojista_dias, freight_value, price, product_weight_g, volume_cm3.
        Optional parameters have sensible defaults. Derived features (frete_por_kg, semana_ano,
        eh_alta_temporada, rota) are computed automatically.
        """
        model, config = DataStore.catboost()
        if model is None:
            return (
                "**Error:** CatBoost V5 model file not found.\n\n"
                "Use `get_catboost_model_info` or `dynamic_aggregate` with "
                "`column='foi_atraso'` for delay statistics instead."
            )

        features = _derive_features(
            velocidade_lojista_dias, freight_value, price, product_weight_g,
            volume_cm3, total_itens_pedido, seller_state, customer_state,
            product_category_name, distancia_haversine_km, prazo_estimado_dias,
            historico_atraso_vendedor, qtd_pedidos_anteriores_vendedor,
            mes_compra, dia_semana_compra,
        )

        prob, label, risk = _predict_single(features, model, config)
        confidence = max(prob, 1 - prob)

        # Build output
        lines = [
            f"### Delay Prediction (CatBoost V5)\n",
            f"**Probability:** {prob:.1%}",
            f"**Classification:** {label} (threshold: {config['threshold']:.2f})",
            f"**Confidence:** {confidence:.1%}",
            f"**Risk Level:** {risk}\n",
            "#### Features Used\n",
            "| Feature | Value |",
            "|---------|-------|",
        ]
        for k, v in features.items():
            if isinstance(v, float):
                lines.append(f"| {k} | {v:,.4f} |")
            else:
                lines.append(f"| {k} | {v} |")

        # Contextual tips
        lines.append("\n#### Preventive Actions")
        if prob >= 0.54:
            if features["velocidade_lojista_dias"] > 3:
                lines.append("- Reduce seller processing time (currently {:.1f} days)".format(features["velocidade_lojista_dias"]))
            if features["distancia_haversine_km"] > 500:
                lines.append("- Consider closer fulfillment center ({:.0f} km route)".format(features["distancia_haversine_km"]))
            if features["eh_alta_temporada"] == 1:
                lines.append("- High season (Nov/Dec): add buffer to estimated delivery")
        else:
            lines.append("- Low risk — standard fulfillment recommended")

        return "\n".join(lines)

    @mcp.tool()
    def get_catboost_model_info() -> str:
        """Get complete CatBoost V5 model information: metrics, hyperparameters, features, and SMOTE config."""
        _, config = DataStore.catboost()
        if config is None:
            return "**Error:** CatBoost config file not found."

        m = config["metrics"]
        hp = config["best_params"]
        cm = config["confusion_matrix"]
        smote = config["smote"]

        lines = [
            "### CatBoost V5 Model Info\n",
            f"**Algorithm:** {config['algorithm']} {config['version']}",
            f"**Threshold:** {config['threshold']:.2f}\n",
            "#### Performance Metrics\n",
            "| Metric | Value |",
            "|--------|-------|",
            f"| ROC-AUC | {m['roc_auc']:.4f} |",
            f"| Recall | {m['recall']:.4f} |",
            f"| Precision | {m['precision']:.4f} |",
            f"| F1-Score | {m['f1_score']:.4f} |",
            f"| Accuracy | {m['accuracy']:.4f} |",
            f"| Multiplier vs Random | {m['multiplicador_vs_acaso']:.2f}x |\n",
            "#### Confusion Matrix\n",
            "| | Predicted No Delay | Predicted Delay |",
            "|---|---|---|",
            f"| **Actual No Delay** | TN: {cm['TN']:,} | FP: {cm['FP']:,} |",
            f"| **Actual Delay** | FN: {cm['FN']:,} | TP: {cm['TP']:,} |\n",
            "#### Hyperparameters\n",
            "| Param | Value |",
            "|-------|-------|",
            f"| depth | {hp['depth']} |",
            f"| iterations | {hp['iterations']} |",
            f"| learning_rate | {hp['learning_rate']} |",
            f"| l2_leaf_reg | {hp['l2_leaf_reg']} |\n",
            "#### Features ({} total)\n".format(config['n_features']),
            "**Numeric ({}):** {}".format(len(config['features_num']), ", ".join(config['features_num'])),
            "**Categorical ({}):** {}".format(len(config['features_cat']), ", ".join(config['features_cat'])),
            "\n#### SMOTE Oversampling\n",
            f"- Strategy: {smote['strategy']}",
            f"- Synthetic samples: {smote['synthetic_samples']:,}",
        ]
        return "\n".join(lines)

    @mcp.tool()
    def get_catboost_feature_importance(top_n: int = 19) -> str:
        """Get ranked feature importance from CatBoost V5 model.

        Falls back to Pearson correlation with foi_atraso if model is unavailable.
        """
        model, config = DataStore.catboost()

        if model is not None:
            importances = model.get_feature_importance()
            feature_names = config["features_all"]
            pairs = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)
            total = sum(importances)

            pairs = pairs[:top_n]
            lines = [
                "### CatBoost V5 Feature Importance\n",
                "| Rank | Feature | Importance | % of Total |",
                "|------|---------|------------|------------|",
            ]
            for i, (name, imp) in enumerate(pairs, 1):
                pct = (imp / total * 100) if total > 0 else 0
                lines.append(f"| {i} | {name} | {imp:.4f} | {pct:.1f}% |")

            return "\n".join(lines)

        # Fallback: Pearson correlation
        df = DataStore.df()
        numeric_cols = df.select_dtypes(include="number").columns
        if "foi_atraso" in numeric_cols:
            corr = df[numeric_cols].corr()["foi_atraso"].drop("foi_atraso", errors="ignore").abs()
            corr = corr.sort_values(ascending=False).head(top_n)
            lines = [
                "### Feature Importance (Pearson Correlation Fallback)\n",
                "*CatBoost model not available. Showing |correlation| with foi_atraso.*\n",
                "| Rank | Feature | |Correlation| |",
                "|------|---------|--------------|",
            ]
            for i, (name, val) in enumerate(corr.items(), 1):
                lines.append(f"| {i} | {name} | {val:.4f} |")
            return "\n".join(lines)

        return "**Error:** Neither model nor correlation data available."

    @mcp.tool()
    def simulate_scenario(
        vary_feature: str,
        vary_values: list,
        velocidade_lojista_dias: float = 3.0,
        freight_value: float = 25.0,
        price: float = 100.0,
        product_weight_g: float = 500.0,
        volume_cm3: float = 3000.0,
        total_itens_pedido: int = 1,
        seller_state: str = "SP",
        customer_state: str = "SP",
        product_category_name: str = "outros",
        distancia_haversine_km: float | None = None,
        prazo_estimado_dias: int = 15,
        historico_atraso_vendedor: float = 0.07,
        qtd_pedidos_anteriores_vendedor: int = 50,
        mes_compra: int | None = None,
        dia_semana_compra: int | None = None,
    ) -> str:
        """Simulate how varying one feature affects delay probability.

        Example: vary_feature="velocidade_lojista_dias", vary_values=[1, 2, 3, 5, 7, 10]
        All other parameters are held constant at their defaults or provided values.
        """
        model, config = DataStore.catboost()
        if model is None:
            return "**Error:** CatBoost V5 model file not found."

        if not vary_values:
            return "**Error:** vary_values must be a non-empty list."

        # Validate vary_feature is a known model feature
        all_features = config["features_all"]
        # Also accept the user-facing param names that map to derived features
        valid_vary = set(all_features) | {
            "velocidade_lojista_dias", "freight_value", "price",
            "product_weight_g", "volume_cm3", "total_itens_pedido",
            "seller_state", "customer_state", "product_category_name",
            "distancia_haversine_km", "prazo_estimado_dias",
            "historico_atraso_vendedor", "qtd_pedidos_anteriores_vendedor",
            "mes_compra", "dia_semana_compra",
        }
        if vary_feature not in valid_vary:
            return f"**Error:** Unknown feature '{vary_feature}'. Valid: {sorted(valid_vary)}"

        # Build base kwargs
        base_kwargs = {
            "velocidade_lojista_dias": velocidade_lojista_dias,
            "freight_value": freight_value,
            "price": price,
            "product_weight_g": product_weight_g,
            "volume_cm3": volume_cm3,
            "total_itens_pedido": total_itens_pedido,
            "seller_state": seller_state,
            "customer_state": customer_state,
            "product_category_name": product_category_name,
            "distancia_haversine_km": distancia_haversine_km,
            "prazo_estimado_dias": prazo_estimado_dias,
            "historico_atraso_vendedor": historico_atraso_vendedor,
            "qtd_pedidos_anteriores_vendedor": qtd_pedidos_anteriores_vendedor,
            "mes_compra": mes_compra,
            "dia_semana_compra": dia_semana_compra,
        }

        rows = []
        for val in vary_values:
            kwargs = dict(base_kwargs)
            kwargs[vary_feature] = val
            features = _derive_features(**kwargs)
            prob, label, risk = _predict_single(features, model, config)
            rows.append({
                vary_feature: val,
                "Probability": f"{prob:.1%}",
                "Class": label,
                "Risk": risk,
            })

        result_df = pd.DataFrame(rows)
        table = result_df.to_markdown(index=False)

        return f"### Scenario Simulation: Varying `{vary_feature}`\n\n{table}"
