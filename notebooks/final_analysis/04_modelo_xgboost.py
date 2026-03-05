# %% [markdown]
# # Modelo Preditivo XGBoost — Previsão de Atraso Logístico
# **Cards:** ALPHA-07 (Split Treino/Teste) + ALPHA-08 (Baseline XGBoost)
#
# **Branch:** `feat/alpha-07-08-baseline-xgboost`
#
# **Objetivo:** Treinar a primeira versão do classificador binário XGBoost
# para prever se um pedido vai atrasar (`foi_atraso = 1`) ou não (`= 0`).
#
# **Referência:** `spec/model_spec.md`

# %% [markdown]
# ---
# ## Seção 1 — Carga do Dataset de Treino
# O dataset `dataset_treino_v1.csv` foi preparado na fase de EDA
# e contém 6 features + 1 target, sem nulos, com encoding aplicado.

# %%
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Carregar dataset limpo
df = pd.read_csv('dataset_treino_v1.csv')

print("=" * 60)
print("  CARGA DO DATASET DE TREINO")
print("=" * 60)
print(f"  Shape: {df.shape}")
print(f"  Colunas: {list(df.columns)}")
print(f"\n  Primeiras 5 linhas:")
print(df.head())
print(f"\n  Estatísticas descritivas:")
print(df.describe().round(4))
print(f"\n  Nulos por coluna:")
print(df.isnull().sum())

# %% [markdown]
# ---
# ## Seção 2 — Split Treino/Teste (ALPHA-07)
# Dividir os dados em 80% treino e 20% teste com estratificação
# para manter a proporção de ~7% de atrasos em ambos os conjuntos.
#
# ### Por que estratificar?
# Como a classe `foi_atraso = 1` representa apenas ~6.6% dos dados,
# um split aleatório poderia colocar pouquíssimos atrasos no conjunto
# de teste, tornando a avaliação do modelo não-representativa.

# %%
from sklearn.model_selection import train_test_split

# Separar features (X) e target (y)
FEATURES = [col for col in df.columns if col != 'foi_atraso']
TARGET = 'foi_atraso'

X = df[FEATURES]
y = df[TARGET]

print("=" * 60)
print("  SPLIT TREINO/TESTE ESTRATIFICADO")
print("=" * 60)
print(f"  Features ({len(FEATURES)}): {FEATURES}")
print(f"  Target: {TARGET}")

# Split 80/20 estratificado
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

print(f"\n  Treino: {X_train.shape[0]:,} amostras ({X_train.shape[0]/len(df)*100:.1f}%)")
print(f"  Teste:  {X_test.shape[0]:,} amostras ({X_test.shape[0]/len(df)*100:.1f}%)")

# Validar proporção do target nos dois conjuntos
print(f"\n  Proporção de atrasos no TREINO: {y_train.mean():.4f} ({y_train.mean()*100:.2f}%)")
print(f"  Proporção de atrasos no TESTE:  {y_test.mean():.4f} ({y_test.mean()*100:.2f}%)")
print(f"  Proporção ORIGINAL:             {y.mean():.4f} ({y.mean()*100:.2f}%)")

# Validação automática
diff = abs(y_train.mean() - y_test.mean())
assert diff < 0.005, f"ERRO: proporções divergem em {diff:.4f}!"
print(f"\n  >>> Diferença entre treino/teste: {diff:.6f} — Validação OK! ✅")

# %% [markdown]
# ---
# ## Seção 3 — Treino do Modelo Baseline (ALPHA-08)
# Treinar o XGBoost com os hiperparâmetros definidos no `model_spec.md`.
#
# ### Parâmetros-chave:
# - `objective='binary:logistic'` → classificação binária
# - `scale_pos_weight=13.76` → compensa o desbalanceamento (93/7)
# - `eval_metric='auc'` → otimiza para ROC-AUC internamente
# - `max_depth=6` → profundidade máxima de cada árvore
# - `n_estimators=200` → número de árvores no ensemble
# - `learning_rate=0.1` → taxa de aprendizado
# - `random_state=42` → reprodutibilidade

# %%
from xgboost import XGBClassifier
import time

print("=" * 60)
print("  TREINAMENTO DO XGBOOST BASELINE")
print("=" * 60)

# Instanciar o modelo com os hiperparâmetros do model_spec.md
model = XGBClassifier(
    objective='binary:logistic',
    eval_metric='auc',
    scale_pos_weight=13.76,       # ratio: ~89941 / ~6535
    max_depth=6,
    learning_rate=0.1,
    n_estimators=200,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    use_label_encoder=False
)

print("  Hiperparâmetros configurados:")
print(f"    objective:         {model.objective}")
print(f"    scale_pos_weight:  {model.scale_pos_weight}")
print(f"    max_depth:         {model.max_depth}")
print(f"    learning_rate:     {model.learning_rate}")
print(f"    n_estimators:      {model.n_estimators}")
print(f"    subsample:         {model.subsample}")
print(f"    colsample_bytree:  {model.colsample_bytree}")

# Treinar
print(f"\n  Treinando com {X_train.shape[0]:,} amostras...")
inicio = time.time()

model.fit(X_train, y_train)

tempo = time.time() - inicio
print(f"  Treino concluído em {tempo:.2f} segundos! ✅")

# %% [markdown]
# ---
# ## Seção 4 — Avaliação do Modelo
# Gerar as métricas de performance no conjunto de TESTE (nunca visto pelo modelo).
#
# ### Métricas principais (conforme model_spec.md):
# | Métrica | Meta Mínima |
# |:--|:--|
# | ROC-AUC | ≥ 0.70 |
# | Recall | ≥ 0.60 |
# | F1-Score | ≥ 0.50 |

# %%
from sklearn.metrics import (
    classification_report, roc_auc_score, confusion_matrix,
    roc_curve, precision_recall_curve, f1_score, recall_score,
    precision_score, accuracy_score
)

# Predições
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]  # probabilidade da classe 1

print("=" * 60)
print("  AVALIAÇÃO DO MODELO — CONJUNTO DE TESTE")
print("=" * 60)

# Métricas principais
roc_auc = roc_auc_score(y_test, y_proba)
recall = recall_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n  {'='*40}")
print(f"  {'MÉTRICA':<25} {'VALOR':>8}  {'META':>8}  {'STATUS':>6}")
print(f"  {'='*40}")
print(f"  {'ROC-AUC':<25} {roc_auc:>8.4f}  {'≥ 0.70':>8}  {'✅' if roc_auc >= 0.70 else '❌':>6}")
print(f"  {'Recall':<25} {recall:>8.4f}  {'≥ 0.60':>8}  {'✅' if recall >= 0.60 else '❌':>6}")
print(f"  {'F1-Score':<25} {f1:>8.4f}  {'≥ 0.50':>8}  {'✅' if f1 >= 0.50 else '❌':>6}")
print(f"  {'Precision':<25} {precision:>8.4f}  {'—':>8}  {'ℹ️':>6}")
print(f"  {'Accuracy':<25} {accuracy:>8.4f}  {'—':>8}  {'ℹ️':>6}")
print(f"  {'='*40}")

# Classification Report completo
print(f"\n  Classification Report:")
print(classification_report(y_test, y_pred, target_names=['No Prazo (0)', 'Atrasou (1)']))

# %% [markdown]
# ---
# ## Seção 5 — Matriz de Confusão
# Visualizar quantos pedidos foram classificados corretamente
# e onde o modelo erra (falsos positivos e falsos negativos).

# %%
import plotly.graph_objects as go
import plotly.express as px

# Calcular matriz de confusão
cm = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = cm.ravel()

print("=" * 60)
print("  MATRIZ DE CONFUSÃO")
print("=" * 60)
print(f"  Verdadeiros Negativos (TN): {tn:,}  — No prazo, previu no prazo ✅")
print(f"  Falsos Positivos (FP):      {fp:,}  — No prazo, previu atraso ⚠️")
print(f"  Falsos Negativos (FN):      {fn:,}  — Atrasou, previu no prazo ❌")
print(f"  Verdadeiros Positivos (TP): {tp:,}  — Atrasou, previu atraso ✅")

# Gráfico da Matriz de Confusão
labels = ['No Prazo (0)', 'Atrasou (1)']
fig_cm = go.Figure(data=go.Heatmap(
    z=cm,
    x=labels,
    y=labels,
    text=[[f'TN\n{tn:,}', f'FP\n{fp:,}'],
          [f'FN\n{fn:,}', f'TP\n{tp:,}']],
    texttemplate='%{text}',
    textfont={'size': 18},
    colorscale='Blues',
    showscale=True
))
fig_cm.update_layout(
    title='Matriz de Confusão — XGBoost Baseline',
    xaxis_title='Previsto pelo Modelo',
    yaxis_title='Valor Real',
    height=450, width=500
)
fig_cm.write_html('../../models/v1/resultado_matriz_confusao.html')
fig_cm.show()

# %% [markdown]
# ---
# ## Seção 6 — Curva ROC
# A Curva ROC mostra a relação entre a Taxa de Verdadeiros Positivos (Recall)
# e a Taxa de Falsos Positivos para diferentes limiares de classificação.
# Quanto mais a curva se afasta da diagonal, melhor o modelo.

# %%
# Calcular curva ROC
fpr, tpr, thresholds = roc_curve(y_test, y_proba)

fig_roc = go.Figure()
fig_roc.add_trace(go.Scatter(
    x=fpr, y=tpr,
    mode='lines',
    name=f'XGBoost (AUC = {roc_auc:.4f})',
    line=dict(color='#2563EB', width=3)
))
fig_roc.add_trace(go.Scatter(
    x=[0, 1], y=[0, 1],
    mode='lines',
    name='Aleatório (AUC = 0.50)',
    line=dict(color='gray', dash='dash')
))
fig_roc.update_layout(
    title=f'Curva ROC — XGBoost Baseline (AUC = {roc_auc:.4f})',
    xaxis_title='Taxa de Falsos Positivos (FPR)',
    yaxis_title='Taxa de Verdadeiros Positivos (TPR / Recall)',
    height=500, width=600,
    legend=dict(x=0.55, y=0.1)
)
fig_roc.write_html('../../models/v1/resultado_curva_roc.html')
fig_roc.show()

print(f"\n  Curva ROC gerada. AUC = {roc_auc:.4f}")

# %% [markdown]
# ---
# ## Seção 7 — Feature Importance
# Quais features o XGBoost considerou mais importantes para decidir
# se um pedido vai atrasar ou não?

# %%
# Extrair importâncias
importances = model.feature_importances_
feat_imp = pd.DataFrame({
    'feature': FEATURES,
    'importance': importances
}).sort_values('importance', ascending=True)

print("=" * 60)
print("  FEATURE IMPORTANCE (XGBoost)")
print("=" * 60)
for _, row in feat_imp.iterrows():
    barra = '█' * int(row['importance'] * 50)
    print(f"  {row['feature']:30s} {row['importance']:.4f}  {barra}")

# Gráfico de Feature Importance
fig_imp = px.bar(
    feat_imp,
    x='importance',
    y='feature',
    orientation='h',
    title='Feature Importance — XGBoost Baseline',
    labels={'importance': 'Importância', 'feature': 'Feature'},
    color='importance',
    color_continuous_scale='Viridis'
)
fig_imp.update_layout(height=400, width=600, yaxis={'categoryorder': 'total ascending'})
fig_imp.write_html('../../models/v1/resultado_feature_importance.html')
fig_imp.show()

# %% [markdown]
# ---
# ## Seção 8 — Exportação do Modelo
# Salvar o modelo treinado como `.pkl` para uso futuro pelo
# Backend (FastAPI) e pelo Servidor MCP.

# %%
import joblib
import os

# Criar pasta models/v1 se não existir
os.makedirs('../../models/v1', exist_ok=True)

# Salvar modelo
model_path = '../../models/v1/xgboost_atraso_v1.pkl'
joblib.dump(model, model_path)

# Salvar lista de features na ordem exata (o backend precisa disso)
features_path = '../../models/v1/features_order.txt'
with open(features_path, 'w') as f:
    for feat in FEATURES:
        f.write(feat + '\n')

print("=" * 60)
print("  EXPORTAÇÃO DO MODELO")
print("=" * 60)
print(f"  Modelo salvo em: {model_path}")
print(f"  Features salvas em: {features_path}")
print(f"  Tamanho do .pkl: {os.path.getsize(model_path) / 1024:.1f} KB")

# %% [markdown]
# ---
# ## Seção 9 — Resumo Final e Veredito

# %%
print("\n" + "=" * 60)
print("  RESUMO FINAL — MODELO XGBOOST BASELINE")
print("=" * 60)
print(f"""
  Dataset:        {len(df):,} amostras | {len(FEATURES)} features
  Split:          80/20 estratificado (random_state=42)
  Algoritmo:      XGBClassifier (200 árvores, depth=6)

  ┌─────────────────────────────────────────────┐
  │  MÉTRICAS NO CONJUNTO DE TESTE              │
  ├─────────────────────────────────────────────┤
  │  ROC-AUC:   {roc_auc:.4f}  {'✅ APROVADO' if roc_auc >= 0.70 else '❌ ABAIXO DA META'}{'':>12}│
  │  Recall:    {recall:.4f}  {'✅ APROVADO' if recall >= 0.60 else '⚠️ AVALIAR'}{'':>12}│
  │  F1-Score:  {f1:.4f}  {'✅ APROVADO' if f1 >= 0.50 else '⚠️ AVALIAR'}{'':>12}│
  │  Precision: {precision:.4f}{'':>28}│
  │  Accuracy:  {accuracy:.4f}{'':>28}│
  └─────────────────────────────────────────────┘

  Modelo exportado: models/xgboost_atraso_v1.pkl

  Arquivos gerados:
    - resultado_matriz_confusao.html
    - resultado_curva_roc.html
    - resultado_feature_importance.html
""")

viavel = roc_auc >= 0.65
print(f"  VEREDITO: {'✅ MODELO VIÁVEL — Prosseguir para Tuning (ALPHA-09)' if viavel else '❌ MODELO INVIÁVEL — Revisar features ou trocar algoritmo'}")
print("=" * 60)
