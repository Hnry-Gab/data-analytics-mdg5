# %% [markdown]
# # Modelo XGBoost v3 — Features Expandidas + Tuning
# **Card:** ALPHA-09 (Otimização via Feature Expansion)
#
# **Objetivo:** Reconstruir o dataset com 12 features a partir das tabelas
# brutas e re-treinar o XGBoost buscando maximizar a Precision/F1-Score.

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
import time
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
DATASET_DIR = os.path.join(REPO_ROOT, 'dataset')

print("=" * 60)
print("  SEÇÃO 1 — RECONSTRUÇÃO DO DATASET EXPANDIDO")
print("=" * 60)

orders    = pd.read_csv(f'{DATASET_DIR}/olist_orders_dataset.csv')
customers = pd.read_csv(f'{DATASET_DIR}/olist_customers_dataset.csv')
items     = pd.read_csv(f'{DATASET_DIR}/olist_order_items_dataset.csv')
products  = pd.read_csv(f'{DATASET_DIR}/olist_products_dataset.csv')
sellers   = pd.read_csv(f'{DATASET_DIR}/olist_sellers_dataset.csv')
geo       = pd.read_csv(f'{DATASET_DIR}/olist_geolocation_dataset.csv')

# Filtrar entregues e datas
orders = orders[orders['order_status'] == 'delivered'].copy()
for col in ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date']:
    orders[col] = pd.to_datetime(orders[col])
orders = orders.dropna(subset=['order_delivered_customer_date'])

# Products fillna
products['product_category_name'] = products['product_category_name'].fillna('desconhecido')
for col in ['product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']:
    products[col] = products[col].fillna(products[col].median())

# Geolocation
geo_agg = geo.groupby('geolocation_zip_code_prefix', as_index=False).agg({'geolocation_lat': 'mean', 'geolocation_lng': 'mean'})

# Merge
df = orders.merge(customers, on='customer_id', how='left')
df = df.merge(items, on='order_id', how='left')
df = df.merge(products, on='product_id', how='left')
df = df.merge(sellers, on='seller_id', how='left')
df = df.merge(geo_agg.rename(columns={'geolocation_zip_code_prefix': 'seller_zip_code_prefix', 'geolocation_lat': 'seller_lat', 'geolocation_lng': 'seller_lng'}), on='seller_zip_code_prefix', how='left')
df = df.merge(geo_agg.rename(columns={'geolocation_zip_code_prefix': 'customer_zip_code_prefix', 'geolocation_lat': 'customer_lat', 'geolocation_lng': 'customer_lng'}), on='customer_zip_code_prefix', how='left')


print("\n" + "=" * 60)
print("  SEÇÃO 2 — FEATURE ENGINEERING EXPANDIDA (12 features)")
print("=" * 60)

df['foi_atraso'] = ((df['order_delivered_customer_date'] - df['order_estimated_delivery_date']).dt.days > 0).astype(int)

# --- 6 Originais ---
df['velocidade_lojista_dias'] = (df['order_delivered_carrier_date'] - df['order_approved_at']).dt.days
df['velocidade_lojista_dias'] = df['velocidade_lojista_dias'].fillna(df['velocidade_lojista_dias'].median())

df['distancia_haversine_km'] = 6371 * 2 * np.arcsin(np.sqrt(np.sin(np.radians(df['customer_lat'] - df['seller_lat'])/2)**2 + np.cos(np.radians(df['seller_lat'])) * np.cos(np.radians(df['customer_lat'])) * np.sin(np.radians(df['customer_lng'] - df['seller_lng'])/2)**2))
df['distancia_haversine_km'] = df['distancia_haversine_km'].fillna(df['distancia_haversine_km'].median())

df['rota_interestadual'] = (df['seller_state'] != df['customer_state']).astype(int)

for col_state, col_enc in [('customer_state', 'customer_state_encoded'), ('seller_state', 'seller_state_encoded')]:
    mapping = df.groupby(col_state)['foi_atraso'].mean()
    df[col_enc] = df[col_state].map(mapping)

# --- 6 Novas ---
df['volume_cm3'] = df['product_length_cm'] * df['product_height_cm'] * df['product_width_cm']
df['volume_cm3'] = df['volume_cm3'].fillna(df['volume_cm3'].median())

df['product_weight_g'] = df['product_weight_g'].fillna(df['product_weight_g'].median())

df['total_itens_pedido'] = df.groupby('order_id')['order_item_id'].transform('max')
df['total_itens_pedido'] = df['total_itens_pedido'].fillna(1).astype(int)

df['dia_semana_compra'] = df['order_purchase_timestamp'].dt.dayofweek
df['prazo_estimado_dias'] = (df['order_estimated_delivery_date'] - df['order_purchase_timestamp']).dt.days

FEATURES_V3 = [
    'velocidade_lojista_dias', 'distancia_haversine_km', 'freight_value', 'rota_interestadual', 'customer_state_encoded', 'seller_state_encoded',
    'volume_cm3', 'product_weight_g', 'price', 'total_itens_pedido', 'dia_semana_compra', 'prazo_estimado_dias'
]
df_clean = df[FEATURES_V3 + ['foi_atraso']].dropna()
df_clean.to_csv('dataset_treino_v3.csv', index=False)


print("\n" + "=" * 60)
print("  SEÇÃO 3 — GRIDSEARCH COM FEATURES EXPANDIDAS")
print("=" * 60)

from sklearn.model_selection import train_test_split, GridSearchCV
from xgboost import XGBClassifier

X = df_clean[FEATURES_V3]
y = df_clean['foi_atraso']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

param_grid = {
    'max_depth': [6, 8, 10], 'n_estimators': [200, 300, 500], 'learning_rate': [0.05, 0.1],
    'scale_pos_weight': [3, 5, 7], 'min_child_weight': [1, 3, 5],
}
base_model = XGBClassifier(objective='binary:logistic', eval_metric='auc', subsample=0.8, colsample_bytree=0.8, random_state=42)

inicio = time.time()
grid = GridSearchCV(base_model, param_grid, scoring='roc_auc', cv=5, n_jobs=-1, verbose=1)
grid.fit(X_train, y_train)
best_model = grid.best_estimator_

print(f"\nGridSearch concluído em {time.time() - inicio:.1f}s")
print(f"Melhor ROC-AUC CV: {grid.best_score_:.4f}")

# Threshold Optimization
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score, confusion_matrix

y_proba = best_model.predict_proba(X_test)[:, 1]
thresholds = np.arange(0.05, 0.96, 0.01)
resultados = [{'threshold': t, 'precision': precision_score(y_test, (y_proba >= t).astype(int), zero_division=0), 'recall': recall_score(y_test, (y_proba >= t).astype(int), zero_division=0), 'f1': f1_score(y_test, (y_proba >= t).astype(int), zero_division=0)} for t in thresholds]
df_thresh = pd.DataFrame(resultados)
threshold_otimo = df_thresh.loc[df_thresh['f1'].idxmax()]['threshold']

y_pred_v3 = (y_proba >= threshold_otimo).astype(int)
roc_auc_v3, recall_v3, precision_v3, f1_v3 = roc_auc_score(y_test, y_proba), recall_score(y_test, y_pred_v3), precision_score(y_test, y_pred_v3), f1_score(y_test, y_pred_v3)
cm_v3 = confusion_matrix(y_test, y_pred_v3)
tn, fp, fn, tp = cm_v3.ravel()

print("\n" + "=" * 60)
print("  COMPARATIVO FINAL: v2 (6feat) vs v3 (12feat)")
print("=" * 60)
print(f"ROC-AUC:   0.7591 -> {roc_auc_v3:.4f}")
print(f"Recall:    0.4081 -> {recall_v3:.4f}")
print(f"Precision: 0.2224 -> {precision_v3:.4f}")
print(f"F1-Score:  0.2879 -> {f1_v3:.4f}")
print(f"Falsos Positivos: 2073 -> {fp}")

import joblib, json
joblib.dump(best_model, 'xgboost_atraso_v3.pkl')
config = {
    'model_file': 'xgboost_atraso_v3.pkl', 'threshold': float(threshold_otimo), 'features': FEATURES_V3,
    'n_features': len(FEATURES_V3), 'best_params': grid.best_params_,
    'metrics': {'roc_auc': float(roc_auc_v3), 'recall': float(recall_v3), 'precision': float(precision_v3), 'f1_score': float(f1_v3)},
    'version': 'v3'
}
with open('model_config.json', 'w') as f: json.dump(config, f, indent=2, default=str)
with open('features_order.txt', 'w') as f:
    for feat in FEATURES_V3: f.write(feat + '\n')
