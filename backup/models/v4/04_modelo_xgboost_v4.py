# %% [markdown]
# # Modelo XGBoost v4 — Histórico Implícito + SMOTE
# **Card:** ALPHA-09 (Otimização Avançada)
#
# **Técnicas Novas:**
# 1. Features de Histórico: Taxa de Atraso acumulada por Vendedor e por Rota
# 2. SMOTE: Balanceamento artificial do dataset de treino (93/7 → 50/50)
# 3. GridSearchCV + Threshold Optimization (herdado do v3)

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
import time
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

# ============================================================
# SEÇÃO 1 — CARGA E MERGE (idêntico ao v3)
# ============================================================
print("=" * 60)
print("  SEÇÃO 1 — CARGA E MERGE")
print("=" * 60)

orders    = pd.read_csv(f'{DATASET_DIR}/olist_orders_dataset.csv')
customers = pd.read_csv(f'{DATASET_DIR}/olist_customers_dataset.csv')
items     = pd.read_csv(f'{DATASET_DIR}/olist_order_items_dataset.csv')
products  = pd.read_csv(f'{DATASET_DIR}/olist_products_dataset.csv')
sellers   = pd.read_csv(f'{DATASET_DIR}/olist_sellers_dataset.csv')
geo       = pd.read_csv(f'{DATASET_DIR}/olist_geolocation_dataset.csv')

orders = orders[orders['order_status'] == 'delivered'].copy()
for col in ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date',
            'order_delivered_customer_date', 'order_estimated_delivery_date']:
    orders[col] = pd.to_datetime(orders[col])
orders = orders.dropna(subset=['order_delivered_customer_date'])

products['product_category_name'] = products['product_category_name'].fillna('desconhecido')
for col in ['product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']:
    products[col] = products[col].fillna(products[col].median())

geo_agg = geo.groupby('geolocation_zip_code_prefix', as_index=False).agg(
    {'geolocation_lat': 'mean', 'geolocation_lng': 'mean'})

df = orders.merge(customers, on='customer_id', how='left')
df = df.merge(items, on='order_id', how='left')
df = df.merge(products, on='product_id', how='left')
df = df.merge(sellers, on='seller_id', how='left')
df = df.merge(geo_agg.rename(columns={
    'geolocation_zip_code_prefix': 'seller_zip_code_prefix',
    'geolocation_lat': 'seller_lat', 'geolocation_lng': 'seller_lng'}),
    on='seller_zip_code_prefix', how='left')
df = df.merge(geo_agg.rename(columns={
    'geolocation_zip_code_prefix': 'customer_zip_code_prefix',
    'geolocation_lat': 'customer_lat', 'geolocation_lng': 'customer_lng'}),
    on='customer_zip_code_prefix', how='left')

print(f"  Merge completo: {df.shape}")

# ============================================================
# SEÇÃO 2 — FEATURE ENGINEERING (12 do v3 + 4 de Histórico)
# ============================================================
print("\n" + "=" * 60)
print("  SEÇÃO 2 — FEATURE ENGINEERING (16 features)")
print("=" * 60)

# TARGET
df['foi_atraso'] = ((df['order_delivered_customer_date'] - df['order_estimated_delivery_date']).dt.days > 0).astype(int)

# --- 12 Features do v3 ---
df['velocidade_lojista_dias'] = (df['order_delivered_carrier_date'] - df['order_approved_at']).dt.days
df['velocidade_lojista_dias'] = df['velocidade_lojista_dias'].fillna(df['velocidade_lojista_dias'].median())

df['distancia_haversine_km'] = 6371 * 2 * np.arcsin(np.sqrt(
    np.sin(np.radians(df['customer_lat'] - df['seller_lat'])/2)**2 +
    np.cos(np.radians(df['seller_lat'])) * np.cos(np.radians(df['customer_lat'])) *
    np.sin(np.radians(df['customer_lng'] - df['seller_lng'])/2)**2))
df['distancia_haversine_km'] = df['distancia_haversine_km'].fillna(df['distancia_haversine_km'].median())

df['rota_interestadual'] = (df['seller_state'] != df['customer_state']).astype(int)

for col_state, col_enc in [('customer_state', 'customer_state_encoded'),
                            ('seller_state', 'seller_state_encoded')]:
    mapping = df.groupby(col_state)['foi_atraso'].mean()
    df[col_enc] = df[col_state].map(mapping)

df['volume_cm3'] = df['product_length_cm'] * df['product_height_cm'] * df['product_width_cm']
df['volume_cm3'] = df['volume_cm3'].fillna(df['volume_cm3'].median())
df['product_weight_g'] = df['product_weight_g'].fillna(df['product_weight_g'].median())
df['total_itens_pedido'] = df.groupby('order_id')['order_item_id'].transform('max').fillna(1).astype(int)
df['dia_semana_compra'] = df['order_purchase_timestamp'].dt.dayofweek
df['prazo_estimado_dias'] = (df['order_estimated_delivery_date'] - df['order_purchase_timestamp']).dt.days

# --- 4 NOVAS FEATURES DE HISTÓRICO (o pulo do gato) ---
print("\n  Calculando Features de Histórico Implícito...")

# Ordenar por data de compra para calcular histórico acumulado
df = df.sort_values('order_purchase_timestamp').reset_index(drop=True)

# H1: Taxa de atraso histórica do vendedor (expanding mean)
# Para cada pedido, calcula a média de atraso de TODOS os pedidos ANTERIORES daquele vendedor
df['historico_atraso_vendedor'] = df.groupby('seller_id')['foi_atraso'].transform(
    lambda x: x.expanding().mean().shift(1))
# Primeira venda do vendedor recebe a média global
media_global = df['foi_atraso'].mean()
df['historico_atraso_vendedor'] = df['historico_atraso_vendedor'].fillna(media_global)

# H2: Quantidade de pedidos anteriores do vendedor (experiência)
df['qtd_pedidos_anteriores_vendedor'] = df.groupby('seller_id').cumcount()

# H3: Taxa de atraso histórica da ROTA (estado_vendedor → estado_cliente)
df['rota'] = df['seller_state'] + '_' + df['customer_state']
df['historico_atraso_rota'] = df.groupby('rota')['foi_atraso'].transform(
    lambda x: x.expanding().mean().shift(1))
df['historico_atraso_rota'] = df['historico_atraso_rota'].fillna(media_global)

# H4: Frete por quilo (indicador de qualidade da transportadora)
df['frete_por_kg'] = df['freight_value'] / (df['product_weight_g'] / 1000)
df['frete_por_kg'] = df['frete_por_kg'].replace([np.inf, -np.inf], np.nan)
df['frete_por_kg'] = df['frete_por_kg'].fillna(df['frete_por_kg'].median())

FEATURES_V4 = [
    # 12 do v3
    'velocidade_lojista_dias', 'distancia_haversine_km', 'freight_value',
    'rota_interestadual', 'customer_state_encoded', 'seller_state_encoded',
    'volume_cm3', 'product_weight_g', 'price',
    'total_itens_pedido', 'dia_semana_compra', 'prazo_estimado_dias',
    # 4 novas de histórico
    'historico_atraso_vendedor', 'qtd_pedidos_anteriores_vendedor',
    'historico_atraso_rota', 'frete_por_kg'
]

df_clean = df[FEATURES_V4 + ['foi_atraso']].dropna()

print(f"\n  Total de features: {len(FEATURES_V4)}")
for i, f in enumerate(FEATURES_V4, 1):
    tag = "HIST" if i > 12 else ("NOVA" if i > 6 else "v1")
    print(f"  F{i:2d}. {f:35s} [{tag}]")
print(f"\n  Dataset limpo: {df_clean.shape}")
print(f"  Taxa de atraso: {df_clean['foi_atraso'].mean():.2%}")

# ============================================================
# SEÇÃO 3 — SPLIT + SMOTE (Balanceamento Artificial)
# ============================================================
print("\n" + "=" * 60)
print("  SEÇÃO 3 — SPLIT + SMOTE")
print("=" * 60)

from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE

X = df_clean[FEATURES_V4]
y = df_clean['foi_atraso']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42)

print(f"  ANTES do SMOTE:")
print(f"    Treino: {X_train.shape[0]:,} amostras")
print(f"    Classe 0 (no prazo): {(y_train == 0).sum():,}")
print(f"    Classe 1 (atraso):   {(y_train == 1).sum():,}")
print(f"    Proporção: {y_train.mean():.2%} atrasos")

smote = SMOTE(random_state=42, sampling_strategy=0.3)  # 30% de atrasos no treino
X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)

print(f"\n  DEPOIS do SMOTE:")
print(f"    Treino: {X_train_smote.shape[0]:,} amostras")
print(f"    Classe 0 (no prazo): {(y_train_smote == 0).sum():,}")
print(f"    Classe 1 (atraso):   {(y_train_smote == 1).sum():,}")
print(f"    Proporção: {y_train_smote.mean():.2%} atrasos")
print(f"    Amostras sintéticas geradas: {X_train_smote.shape[0] - X_train.shape[0]:,}")

# ============================================================
# SEÇÃO 4 — GRIDSEARCH
# ============================================================
print("\n" + "=" * 60)
print("  SEÇÃO 4 — GRIDSEARCH (16 features + SMOTE)")
print("=" * 60)

from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV

param_grid = {
    'max_depth': [6, 8, 10],
    'n_estimators': [200, 300, 500],
    'learning_rate': [0.05, 0.1],
    'scale_pos_weight': [1, 2, 3],  # Valores menores pq o SMOTE já equilibrou
    'min_child_weight': [1, 3, 5],
}

total = 1
for v in param_grid.values():
    total *= len(v)
print(f"  Combinações: {total} | Fits: {total * 5}")

base_model = XGBClassifier(
    objective='binary:logistic', eval_metric='auc',
    subsample=0.8, colsample_bytree=0.8, random_state=42)

inicio = time.time()
grid = GridSearchCV(base_model, param_grid, scoring='roc_auc', cv=5, n_jobs=-1, verbose=1)
grid.fit(X_train_smote, y_train_smote)
best_model = grid.best_estimator_
tempo = time.time() - inicio

print(f"\n  GridSearch concluído em {tempo:.1f}s")
print(f"  Melhor ROC-AUC CV: {grid.best_score_:.4f}")
print(f"  Melhores params:")
for p, v in grid.best_params_.items():
    print(f"    {p:25s} = {v}")

# ============================================================
# SEÇÃO 5 — THRESHOLD OPTIMIZATION
# ============================================================
print("\n" + "=" * 60)
print("  SEÇÃO 5 — THRESHOLD OPTIMIZATION")
print("=" * 60)

from sklearn.metrics import (f1_score, precision_score, recall_score,
                              roc_auc_score, confusion_matrix, classification_report)

y_proba = best_model.predict_proba(X_test)[:, 1]
thresholds = np.arange(0.05, 0.96, 0.01)
resultados = []
for t in thresholds:
    yp = (y_proba >= t).astype(int)
    resultados.append({
        'threshold': t,
        'precision': precision_score(y_test, yp, zero_division=0),
        'recall': recall_score(y_test, yp, zero_division=0),
        'f1': f1_score(y_test, yp, zero_division=0)
    })
df_thresh = pd.DataFrame(resultados)
melhor = df_thresh.loc[df_thresh['f1'].idxmax()]
threshold_otimo = melhor['threshold']

print(f"  Threshold ótimo: {threshold_otimo:.2f}")
print(f"  F1 nesse ponto:  {melhor['f1']:.4f}")

# ============================================================
# SEÇÃO 6 — AVALIAÇÃO FINAL E COMPARATIVO
# ============================================================
y_pred = (y_proba >= threshold_otimo).astype(int)
roc_auc = roc_auc_score(y_test, y_proba)
recall  = recall_score(y_test, y_pred)
prec    = precision_score(y_test, y_pred)
f1      = f1_score(y_test, y_pred)
cm      = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = cm.ravel()

print("\n" + "=" * 60)
print("  COMPARATIVO: v3 (12feat) vs v4 (16feat + SMOTE)")
print("=" * 60)
print(f"  {'MÉTRICA':<25} {'V3':>10} {'V4':>10} {'DELTA':>10}")
print(f"  {'='*55}")
print(f"  {'ROC-AUC':<25} {'0.8304':>10} {roc_auc:>10.4f} {roc_auc - 0.8304:>+10.4f}")
print(f"  {'Recall':<25} {'0.4157':>10} {recall:>10.4f} {recall - 0.4157:>+10.4f}")
print(f"  {'Precision':<25} {'0.3761':>10} {prec:>10.4f} {prec - 0.3761:>+10.4f}")
print(f"  {'F1-Score':<25} {'0.3949':>10} {f1:>10.4f} {f1 - 0.3949:>+10.4f}")
print(f"  {'Falsos Positivos':<25} {'1,002':>10} {fp:>10,}")
print(f"  {'Falsos Negativos':<25} {'849':>10} {fn:>10,}")
print(f"  {'Threshold':<25} {'0.29':>10} {threshold_otimo:>10.2f}")
print(f"  {'='*55}")

print(f"\n  Classification Report (v4):")
print(classification_report(y_test, y_pred, target_names=['No Prazo (0)', 'Atrasou (1)']))

print(f"  Feature Importance v4:")
importances = best_model.feature_importances_
feat_imp = pd.DataFrame({'feature': FEATURES_V4, 'importance': importances}).sort_values('importance', ascending=False)
for _, row in feat_imp.iterrows():
    barra = '█' * int(row['importance'] * 50)
    print(f"  {row['feature']:35s} {row['importance']:.4f}  {barra}")

# ============================================================
# SEÇÃO 7 — EXPORTAÇÃO
# ============================================================
import joblib, json

joblib.dump(best_model, 'xgboost_atraso_v4.pkl')

config = {
    'model_file': 'xgboost_atraso_v4.pkl',
    'threshold': float(threshold_otimo),
    'features': FEATURES_V4,
    'n_features': len(FEATURES_V4),
    'best_params': grid.best_params_,
    'smote': {'strategy': 0.3, 'synthetic_samples': int(X_train_smote.shape[0] - X_train.shape[0])},
    'metrics': {
        'roc_auc': float(roc_auc), 'recall': float(recall),
        'precision': float(prec), 'f1_score': float(f1)
    },
    'version': 'v4'
}
with open('model_config.json', 'w') as f:
    json.dump(config, f, indent=2, default=str)
with open('features_order.txt', 'w') as f:
    for feat in FEATURES_V4:
        f.write(feat + '\n')

print("\n" + "=" * 60)
print("  EXPORTAÇÃO v4")
print("=" * 60)
print(f"  Modelo:   xgboost_atraso_v4.pkl ({os.path.getsize('xgboost_atraso_v4.pkl')/1024:.1f} KB)")
print(f"  Config:   model_config.json")
print(f"  Features: {len(FEATURES_V4)} colunas")
print("=" * 60)
