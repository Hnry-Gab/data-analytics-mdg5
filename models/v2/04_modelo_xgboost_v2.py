# %% [markdown]
# # Modelo XGBoost v2 — Tuning + Calibração de Threshold
# **Card:** ALPHA-09 (Otimização de Hiperparâmetros)
#
# **Branch:** `feat/alpha-07-08-baseline-xgboost`
#
# **Objetivo:** Melhorar a Precision do modelo (v1 = 15%) sem destruir
# o Recall (v1 = 62%), encontrando o equilíbrio ideal entre as duas métricas.
#
# **Estratégia:**
# 1. GridSearchCV — testar combinações de hiperparâmetros com validação cruzada
# 2. Threshold Optimization — encontrar o limiar ótimo de decisão (não usar 0.5 cego)
# 3. Comparar v1 vs v2 lado a lado

# %% [markdown]
# ---
# ## Seção 1 — Carga e Split (idêntico à v1)

# %%
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
import time

df = pd.read_csv('../../notebooks/final_analysis/dataset_treino_v1.csv')

from sklearn.model_selection import train_test_split

FEATURES = [col for col in df.columns if col != 'foi_atraso']
TARGET = 'foi_atraso'
X = df[FEATURES]
y = df[TARGET]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

print("=" * 60)
print("  CARGA E SPLIT — IDENTICO A V1")
print("=" * 60)
print(f"  Treino: {X_train.shape[0]:,} | Teste: {X_test.shape[0]:,}")
print(f"  Taxa de atraso: {y.mean():.2%}")

# %% [markdown]
# ---
# ## Seção 2 — GridSearchCV (Tuning de Hiperparâmetros)
# Testar várias combinações de hiperparâmetros usando validação cruzada 5-fold.
# O GridSearch encontrará a melhor combinação automaticamente.
#
# ### Por que reduzir o `scale_pos_weight`?
# Na v1, usamos `scale_pos_weight=13.76` (proporção exata 93/7).
# Isso fez o modelo ser agressivo demais, gerando muitos falsos positivos.
# Vamos testar valores menores para encontrar o balanço ideal.

# %%
from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV

print("\n" + "=" * 60)
print("  GRIDSEARCH CV — TUNING DE HIPERPARAMETROS")
print("=" * 60)

# Grade de hiperparâmetros para testar
param_grid = {
    'max_depth': [4, 6, 8],
    'n_estimators': [200, 300, 500],
    'learning_rate': [0.05, 0.1],
    'scale_pos_weight': [3, 7, 13.76],
    'min_child_weight': [1, 5],
}

total_combinacoes = 1
for v in param_grid.values():
    total_combinacoes *= len(v)
print(f"  Total de combinações: {total_combinacoes}")
print(f"  Com 5-fold CV: {total_combinacoes * 5} fits")

base_model = XGBClassifier(
    objective='binary:logistic',
    eval_metric='auc',
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    use_label_encoder=False
)

inicio = time.time()

grid_search = GridSearchCV(
    estimator=base_model,
    param_grid=param_grid,
    scoring='roc_auc',
    cv=5,
    n_jobs=-1,
    verbose=1
)

grid_search.fit(X_train, y_train)

tempo_grid = time.time() - inicio
print(f"\n  GridSearch concluído em {tempo_grid:.1f} segundos!")
print(f"\n  MELHORES HIPERPARÂMETROS ENCONTRADOS:")
for param, valor in grid_search.best_params_.items():
    print(f"    {param:25s} = {valor}")
print(f"\n  Melhor ROC-AUC (CV): {grid_search.best_score_:.4f}")

# %%
# Extrair o melhor modelo
best_model = grid_search.best_estimator_

# %% [markdown]
# ---
# ## Seção 3 — Threshold Optimization
# O modelo retorna uma probabilidade (ex: 0.35). Por padrão,
# se prob > 0.50 → prevê atraso. Mas esse limiar (threshold) pode
# não ser o ideal para dados desbalanceados.
#
# Vamos varrer todos os thresholds de 0.05 a 0.95 e encontrar
# o que maximiza o F1-Score (equilíbrio entre Precision e Recall).

# %%
from sklearn.metrics import (
    f1_score, precision_score, recall_score, roc_auc_score,
    classification_report, confusion_matrix, roc_curve
)

# Probabilidades no conjunto de teste
y_proba = best_model.predict_proba(X_test)[:, 1]

print("\n" + "=" * 60)
print("  THRESHOLD OPTIMIZATION")
print("=" * 60)

# Varrer thresholds
thresholds = np.arange(0.05, 0.96, 0.01)
resultados = []

for t in thresholds:
    y_pred_t = (y_proba >= t).astype(int)
    p = precision_score(y_test, y_pred_t, zero_division=0)
    r = recall_score(y_test, y_pred_t, zero_division=0)
    f = f1_score(y_test, y_pred_t, zero_division=0)
    resultados.append({'threshold': t, 'precision': p, 'recall': r, 'f1': f})

df_thresh = pd.DataFrame(resultados)

# Encontrar o threshold com melhor F1
melhor = df_thresh.loc[df_thresh['f1'].idxmax()]
threshold_otimo = melhor['threshold']

print(f"\n  THRESHOLD ÓTIMO (max F1): {threshold_otimo:.2f}")
print(f"  Precision nesse ponto:   {melhor['precision']:.4f}")
print(f"  Recall nesse ponto:      {melhor['recall']:.4f}")
print(f"  F1-Score nesse ponto:    {melhor['f1']:.4f}")

# Mostrar a tabela em alguns pontos-chave
print(f"\n  {'Threshold':>10} {'Precision':>10} {'Recall':>10} {'F1':>10}")
print(f"  {'-'*42}")
for _, row in df_thresh[df_thresh['threshold'].isin([0.10, 0.20, 0.30, 0.40, 0.50, threshold_otimo, 0.60, 0.70, 0.80])].iterrows():
    marca = " <<<" if row['threshold'] == threshold_otimo else ""
    print(f"  {row['threshold']:>10.2f} {row['precision']:>10.4f} {row['recall']:>10.4f} {row['f1']:>10.4f}{marca}")

# %% [markdown]
# ---
# ## Seção 4 — Avaliação Final do Modelo v2
# Usar o threshold ótimo para gerar as métricas definitivas.

# %%
# Aplicar o threshold ótimo
y_pred_v2 = (y_proba >= threshold_otimo).astype(int)

roc_auc_v2 = roc_auc_score(y_test, y_proba)
recall_v2 = recall_score(y_test, y_pred_v2)
precision_v2 = precision_score(y_test, y_pred_v2)
f1_v2 = f1_score(y_test, y_pred_v2)

print("\n" + "=" * 60)
print("  AVALIAÇÃO FINAL — MODELO v2 (Tuned + Threshold Ótimo)")
print("=" * 60)
print(f"\n  {'MÉTRICA':<25} {'V1':>10} {'V2':>10} {'DELTA':>10}")
print(f"  {'='*55}")
print(f"  {'ROC-AUC':<25} {'0.7527':>10} {roc_auc_v2:>10.4f} {roc_auc_v2 - 0.7527:>+10.4f}")
print(f"  {'Recall':<25} {'0.6180':>10} {recall_v2:>10.4f} {recall_v2 - 0.6180:>+10.4f}")
print(f"  {'Precision':<25} {'0.1523':>10} {precision_v2:>10.4f} {precision_v2 - 0.1523:>+10.4f}")
print(f"  {'F1-Score':<25} {'0.2443':>10} {f1_v2:>10.4f} {f1_v2 - 0.2443:>+10.4f}")
print(f"  {'Threshold':<25} {'0.50':>10} {threshold_otimo:>10.2f}")
print(f"  {'='*55}")

# Classification Report
print(f"\n  Classification Report (v2):")
print(classification_report(y_test, y_pred_v2, target_names=['No Prazo (0)', 'Atrasou (1)']))

# Matriz de Confusão
cm_v2 = confusion_matrix(y_test, y_pred_v2)
tn, fp, fn, tp = cm_v2.ravel()
print(f"  Verdadeiros Negativos (TN): {tn:>6,}  — No prazo, previu no prazo ✅")
print(f"  Falsos Positivos (FP):      {fp:>6,}  — No prazo, previu atraso ⚠️")
print(f"  Falsos Negativos (FN):      {fn:>6,}  — Atrasou, previu no prazo ❌")
print(f"  Verdadeiros Positivos (TP): {tp:>6,}  — Atrasou, previu atraso ✅")

# %% [markdown]
# ---
# ## Seção 5 — Gráficos Comparativos

# %%
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# 5.1 — Gráfico de Threshold vs Métricas
fig_thresh = go.Figure()
fig_thresh.add_trace(go.Scatter(x=df_thresh['threshold'], y=df_thresh['precision'],
                                 mode='lines', name='Precision', line=dict(color='#EF4444', width=2)))
fig_thresh.add_trace(go.Scatter(x=df_thresh['threshold'], y=df_thresh['recall'],
                                 mode='lines', name='Recall', line=dict(color='#3B82F6', width=2)))
fig_thresh.add_trace(go.Scatter(x=df_thresh['threshold'], y=df_thresh['f1'],
                                 mode='lines', name='F1-Score', line=dict(color='#10B981', width=3)))
fig_thresh.add_vline(x=threshold_otimo, line_dash="dash", line_color="gold",
                      annotation_text=f"Ótimo: {threshold_otimo:.2f}")
fig_thresh.update_layout(
    title=f'Threshold Optimization — Ponto Ótimo em {threshold_otimo:.2f}',
    xaxis_title='Threshold', yaxis_title='Score',
    height=450, width=700
)
fig_thresh.write_html('resultado_threshold_optimization.html')
fig_thresh.show()

# %%
# 5.2 — Curva ROC do v2
fpr, tpr, _ = roc_curve(y_test, y_proba)
fig_roc = go.Figure()
fig_roc.add_trace(go.Scatter(x=fpr, y=tpr, mode='lines',
                              name=f'XGBoost v2 (AUC = {roc_auc_v2:.4f})',
                              line=dict(color='#2563EB', width=3)))
fig_roc.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines',
                              name='Aleatório (AUC = 0.50)',
                              line=dict(color='gray', dash='dash')))
fig_roc.update_layout(
    title=f'Curva ROC — XGBoost v2 (AUC = {roc_auc_v2:.4f})',
    xaxis_title='FPR', yaxis_title='TPR / Recall',
    height=500, width=600, legend=dict(x=0.55, y=0.1)
)
fig_roc.write_html('resultado_curva_roc.html')
fig_roc.show()

# %%
# 5.3 — Matriz de Confusão v2
labels = ['No Prazo (0)', 'Atrasou (1)']
fig_cm = go.Figure(data=go.Heatmap(
    z=cm_v2, x=labels, y=labels,
    text=[[f'TN\n{tn:,}', f'FP\n{fp:,}'], [f'FN\n{fn:,}', f'TP\n{tp:,}']],
    texttemplate='%{text}', textfont={'size': 18},
    colorscale='Blues', showscale=True
))
fig_cm.update_layout(
    title='Matriz de Confusão — XGBoost v2 (Tuned)',
    xaxis_title='Previsto', yaxis_title='Real', height=450, width=500
)
fig_cm.write_html('resultado_matriz_confusao.html')
fig_cm.show()

# %%
# 5.4 — Feature Importance v2
importances = best_model.feature_importances_
feat_imp = pd.DataFrame({'feature': FEATURES, 'importance': importances}).sort_values('importance', ascending=True)

fig_imp = px.bar(feat_imp, x='importance', y='feature', orientation='h',
                  title='Feature Importance — XGBoost v2 (Tuned)',
                  labels={'importance': 'Importância', 'feature': 'Feature'},
                  color='importance', color_continuous_scale='Viridis')
fig_imp.update_layout(height=400, width=600, yaxis={'categoryorder': 'total ascending'})
fig_imp.write_html('resultado_feature_importance.html')
fig_imp.show()

# %% [markdown]
# ---
# ## Seção 6 — Exportação do Modelo v2

# %%
import joblib

# Salvar modelo tuned
model_path = 'xgboost_atraso_v2.pkl'
joblib.dump(best_model, model_path)

# Salvar o threshold ótimo (o backend precisa disso!)
import json
config = {
    'model_file': 'xgboost_atraso_v2.pkl',
    'threshold': float(threshold_otimo),
    'features': FEATURES,
    'best_params': grid_search.best_params_,
    'metrics': {
        'roc_auc': float(roc_auc_v2),
        'recall': float(recall_v2),
        'precision': float(precision_v2),
        'f1_score': float(f1_v2)
    },
    'version': 'v2'
}
with open('model_config.json', 'w') as f:
    json.dump(config, f, indent=2, default=str)

# Features order
with open('features_order.txt', 'w') as f:
    for feat in FEATURES:
        f.write(feat + '\n')

import os
print("\n" + "=" * 60)
print("  EXPORTAÇÃO DO MODELO v2")
print("=" * 60)
print(f"  Modelo:    {model_path} ({os.path.getsize(model_path)/1024:.1f} KB)")
print(f"  Config:    model_config.json (contém threshold + params)")
print(f"  Features:  features_order.txt")

# %% [markdown]
# ---
# ## Seção 7 — Resumo Final Comparativo

# %%
print("\n" + "=" * 60)
print("  COMPARATIVO FINAL: v1 (BASELINE) vs v2 (TUNED)")
print("=" * 60)
print(f"""
  ┌──────────────────────────────────────────────────────────┐
  │  MÉTRICA          │    v1 (Baseline)  │   v2 (Tuned)     │
  ├──────────────────────────────────────────────────────────┤
  │  ROC-AUC          │      0.7527       │   {roc_auc_v2:.4f}         │
  │  Recall           │      0.6180       │   {recall_v2:.4f}         │
  │  Precision        │      0.1523       │   {precision_v2:.4f}         │
  │  F1-Score         │      0.2443       │   {f1_v2:.4f}         │
  │  Threshold        │      0.50         │   {threshold_otimo:.2f}           │
  │  Falsos Positivos │      5,000        │   {fp:,}           │
  └──────────────────────────────────────────────────────────┘
""")

melhoria_precision = ((precision_v2 - 0.1523) / 0.1523) * 100
print(f"  Melhoria na Precision: {melhoria_precision:+.1f}%")
print(f"  Redução de Falsos Positivos: {5000 - fp:,} alertas falsos a menos!")
print("\n" + "=" * 60)
