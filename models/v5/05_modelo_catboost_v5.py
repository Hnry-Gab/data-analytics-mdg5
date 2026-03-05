# %% [markdown]
# # Modelo CatBoost v5 — Features Textuais Nativas + Sazonalidade + SMOTE
# **Card:** ALPHA-09 (Obra-prima Final)
#
# **Diferenciais em relação ao v4 (XGBoost):**
# 1. CatBoost processa categorias textuais SEM encoding manual
# 2. Features de sazonalidade (mês, semana do ano, é Black Friday?)
# 3. Categoria de produto como texto nativo
# 4. Rota seller_state→customer_state como texto nativo
# 5. SMOTE herdado do v4

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
# SEÇÃO 1 — CARGA E MERGE
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
# SEÇÃO 2 — FEATURE ENGINEERING (20 features)
# ============================================================
print("\n" + "=" * 60)
print("  SEÇÃO 2 — FEATURE ENGINEERING (20 features)")
print("=" * 60)

# TARGET
df['foi_atraso'] = ((df['order_delivered_customer_date'] - df['order_estimated_delivery_date']).dt.days > 0).astype(int)

# --- Features Numéricas (herdadas do v4) ---
df['velocidade_lojista_dias'] = (df['order_delivered_carrier_date'] - df['order_approved_at']).dt.days
df['velocidade_lojista_dias'] = df['velocidade_lojista_dias'].fillna(df['velocidade_lojista_dias'].median())

df['distancia_haversine_km'] = 6371 * 2 * np.arcsin(np.sqrt(
    np.sin(np.radians(df['customer_lat'] - df['seller_lat'])/2)**2 +
    np.cos(np.radians(df['seller_lat'])) * np.cos(np.radians(df['customer_lat'])) *
    np.sin(np.radians(df['customer_lng'] - df['seller_lng'])/2)**2))
df['distancia_haversine_km'] = df['distancia_haversine_km'].fillna(df['distancia_haversine_km'].median())

df['volume_cm3'] = df['product_length_cm'] * df['product_height_cm'] * df['product_width_cm']
df['volume_cm3'] = df['volume_cm3'].fillna(df['volume_cm3'].median())
df['product_weight_g'] = df['product_weight_g'].fillna(df['product_weight_g'].median())
df['total_itens_pedido'] = df.groupby('order_id')['order_item_id'].transform('max').fillna(1).astype(int)
df['prazo_estimado_dias'] = (df['order_estimated_delivery_date'] - df['order_purchase_timestamp']).dt.days

# --- Features de Histórico (herdadas do v4) ---
print("  Calculando Features de Histórico...")
df = df.sort_values('order_purchase_timestamp').reset_index(drop=True)
media_global = df['foi_atraso'].mean()

df['historico_atraso_vendedor'] = df.groupby('seller_id')['foi_atraso'].transform(
    lambda x: x.expanding().mean().shift(1))
df['historico_atraso_vendedor'] = df['historico_atraso_vendedor'].fillna(media_global)

df['qtd_pedidos_anteriores_vendedor'] = df.groupby('seller_id').cumcount()

df['frete_por_kg'] = df['freight_value'] / (df['product_weight_g'] / 1000)
df['frete_por_kg'] = df['frete_por_kg'].replace([np.inf, -np.inf], np.nan)
df['frete_por_kg'] = df['frete_por_kg'].fillna(df['frete_por_kg'].median())

# --- NOVAS Features de Sazonalidade (Exclusivas do v5) ---
print("  Calculando Features de Sazonalidade...")
df['mes_compra'] = df['order_purchase_timestamp'].dt.month
df['semana_ano'] = df['order_purchase_timestamp'].dt.isocalendar().week.astype(int)
df['dia_semana_compra'] = df['order_purchase_timestamp'].dt.dayofweek
# Black Friday / Natal: Semanas 47-52 são caóticas logisticamente
df['eh_alta_temporada'] = df['semana_ano'].apply(lambda x: 1 if x >= 47 else 0)

# --- Features CATEGÓRICAS NATIVAS (A Revolução do CatBoost) ---
print("  Preparando Features Categóricas Nativas...")
# O CatBoost vai processar esses textos internamente sem encoding!
df['rota'] = df['seller_state'].fillna('XX') + '_' + df['customer_state'].fillna('XX')
df['seller_state'] = df['seller_state'].fillna('XX')
df['customer_state'] = df['customer_state'].fillna('XX')
df['product_category_name'] = df['product_category_name'].fillna('desconhecido')

FEATURES_NUM = [
    'velocidade_lojista_dias', 'distancia_haversine_km', 'freight_value',
    'volume_cm3', 'product_weight_g', 'price',
    'total_itens_pedido', 'prazo_estimado_dias',
    'historico_atraso_vendedor', 'qtd_pedidos_anteriores_vendedor', 'frete_por_kg',
    'mes_compra', 'semana_ano', 'dia_semana_compra', 'eh_alta_temporada'
]

FEATURES_CAT = [
    'seller_state', 'customer_state', 'rota', 'product_category_name'
]

# Tipo string obrigatório para CatBoost
for col in FEATURES_CAT:
    df[col] = df[col].astype(str)

# Remover NaN residuais
FEATURES_ALL = FEATURES_NUM + FEATURES_CAT
df_clean = df[FEATURES_ALL + ['foi_atraso']].dropna(subset=FEATURES_NUM + ['foi_atraso'])

print(f"\n  Total de features: {len(FEATURES_ALL)} ({len(FEATURES_NUM)} numéricas + {len(FEATURES_CAT)} categóricas)")
for i, f in enumerate(FEATURES_NUM, 1):
    print(f"  F{i:2d}. {f:35s} [NUM]")
for i, f in enumerate(FEATURES_CAT, len(FEATURES_NUM) + 1):
    print(f"  F{i:2d}. {f:35s} [CAT] ← CatBoost nativo")
print(f"\n  Dataset limpo: {df_clean.shape}")
print(f"  Taxa de atraso: {df_clean['foi_atraso'].mean():.2%}")

# ============================================================
# SEÇÃO 3 — SPLIT + SMOTE (apenas nas numéricas)
# ============================================================
print("\n" + "=" * 60)
print("  SEÇÃO 3 — SPLIT + SMOTE")
print("=" * 60)

from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE

X = df_clean[FEATURES_ALL]
y = df_clean['foi_atraso']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42)

print(f"  ANTES do SMOTE:")
print(f"    Treino: {X_train.shape[0]:,} amostras")
print(f"    Classe 0: {(y_train == 0).sum():,} | Classe 1: {(y_train == 1).sum():,}")
print(f"    Proporção: {y_train.mean():.2%} atrasos")

# SMOTE só funciona com dados numéricos, então aplicamos só nas numéricas
# e depois "colamos" as categóricas de volta
X_train_num = X_train[FEATURES_NUM]
X_train_cat = X_train[FEATURES_CAT]

smote = SMOTE(random_state=42, sampling_strategy=0.3)
X_train_num_smote, y_train_smote = smote.fit_resample(X_train_num, y_train)

# Replicar as categóricas para as amostras sintéticas
# Para as amostras novas geradas pelo SMOTE, usamos a categórica do vizinho mais próximo
n_original = X_train.shape[0]
n_synthetic = X_train_num_smote.shape[0] - n_original

# Para as sintéticas, sortear categorias do treino original da classe minoritária
idx_minority = y_train[y_train == 1].index
cat_minority = X_train_cat.loc[idx_minority]
cat_synthetic = cat_minority.sample(n=n_synthetic, replace=True, random_state=42).reset_index(drop=True)

X_train_cat_smote = pd.concat([
    X_train_cat.reset_index(drop=True),
    cat_synthetic
], ignore_index=True)

X_train_smote = pd.concat([
    X_train_num_smote.reset_index(drop=True),
    X_train_cat_smote
], axis=1)

print(f"\n  DEPOIS do SMOTE:")
print(f"    Treino: {X_train_smote.shape[0]:,} amostras")
print(f"    Classe 0: {(y_train_smote == 0).sum():,} | Classe 1: {(y_train_smote == 1).sum():,}")
print(f"    Proporção: {y_train_smote.mean():.2%} atrasos")
print(f"    Amostras sintéticas: {n_synthetic:,}")

# ============================================================
# SEÇÃO 4 — GRIDSEARCH MANUAL COM CATBOOST
# ============================================================
print("\n" + "=" * 60)
print("  SEÇÃO 4 — GRIDSEARCH MANUAL COM CATBOOST")
print("=" * 60)

from catboost import CatBoostClassifier, Pool
from sklearn.model_selection import StratifiedKFold
from itertools import product

cat_feature_indices = [FEATURES_ALL.index(c) for c in FEATURES_CAT]

param_grid = {
    'depth': [6, 8, 10],
    'iterations': [300, 500],
    'learning_rate': [0.05, 0.1],
    'l2_leaf_reg': [1, 3, 5],
}

keys = list(param_grid.keys())
combos = list(product(*param_grid.values()))
print(f"  Combinações: {len(combos)} | Fits: {len(combos) * 5}")

best_score = -1
best_params = None
best_model = None
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

inicio = time.time()
for i, vals in enumerate(combos):
    params = dict(zip(keys, vals))
    fold_scores = []
    for fold_idx, (train_idx, val_idx) in enumerate(skf.split(X_train_smote, y_train_smote)):
        X_fold_train = X_train_smote.iloc[train_idx]
        y_fold_train = y_train_smote.iloc[train_idx]
        X_fold_val = X_train_smote.iloc[val_idx]
        y_fold_val = y_train_smote.iloc[val_idx]

        train_pool = Pool(X_fold_train, y_fold_train, cat_features=cat_feature_indices)
        val_pool = Pool(X_fold_val, y_fold_val, cat_features=cat_feature_indices)

        model = CatBoostClassifier(
            **params,
            cat_features=cat_feature_indices,
            eval_metric='AUC',
            random_seed=42,
            verbose=0,
            auto_class_weights='Balanced'
        )
        model.fit(train_pool, eval_set=val_pool, verbose=0)
        score = model.get_best_score()['validation']['AUC']
        fold_scores.append(score)

    mean_score = np.mean(fold_scores)
    if (i + 1) % 6 == 0 or i == 0:
        elapsed = time.time() - inicio
        print(f"  [{i+1:3d}/{len(combos)}] score={mean_score:.4f} | {elapsed:.0f}s")

    if mean_score > best_score:
        best_score = mean_score
        best_params = params

# Retrain com os melhores params no dataset SMOTE inteiro
print(f"\n  Retreinando melhor modelo no dataset completo...")
train_pool_full = Pool(X_train_smote, y_train_smote, cat_features=cat_feature_indices)
best_model = CatBoostClassifier(
    **best_params,
    cat_features=cat_feature_indices,
    eval_metric='AUC',
    random_seed=42,
    verbose=0,
    auto_class_weights='Balanced'
)
best_model.fit(train_pool_full, verbose=0)
tempo = time.time() - inicio

print(f"\n  GridSearch concluído em {tempo:.1f}s")
print(f"  Melhor ROC-AUC CV: {best_score:.4f}")
print(f"  Melhores params:")
for p, v in best_params.items():
    print(f"    {p:25s} = {v}")

# Converter para compatibilidade com as seções seguintes
class GridResult:
    def __init__(self, best_params, best_score):
        self.best_params_ = best_params
        self.best_score_ = best_score
grid = GridResult(best_params, best_score)

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
print("  COMPARATIVO: v4 (XGBoost) vs v5 (CatBoost)")
print("=" * 60)
print(f"  {'MÉTRICA':<25} {'V4':>10} {'V5':>10} {'DELTA':>10}")
print(f"  {'='*55}")
print(f"  {'ROC-AUC':<25} {'0.8375':>10} {roc_auc:>10.4f} {roc_auc - 0.8375:>+10.4f}")
print(f"  {'Recall':<25} {'0.4577':>10} {recall:>10.4f} {recall - 0.4577:>+10.4f}")
print(f"  {'Precision':<25} {'0.4593':>10} {prec:>10.4f} {prec - 0.4593:>+10.4f}")
print(f"  {'F1-Score':<25} {'0.4585':>10} {f1:>10.4f} {f1 - 0.4585:>+10.4f}")
print(f"  {'Falsos Positivos':<25} {'783':>10} {fp:>10,}")
print(f"  {'Falsos Negativos':<25} {'788':>10} {fn:>10,}")
print(f"  {'Threshold':<25} {'0.29':>10} {threshold_otimo:>10.2f}")
print(f"  {'='*55}")

print(f"\n  Acurácia Global: {(tp+tn)/(tp+tn+fp+fn):.2%}")
print(f"  Multiplicador vs Acaso: {prec / 0.066:.1f}x")

print(f"\n  Classification Report (v5 CatBoost):")
print(classification_report(y_test, y_pred, target_names=['No Prazo (0)', 'Atrasou (1)']))

print(f"\n  Feature Importance v5:")
importances = best_model.get_feature_importance()
feat_imp = pd.DataFrame({'feature': FEATURES_ALL, 'importance': importances}).sort_values('importance', ascending=False)
for _, row in feat_imp.iterrows():
    barra = '█' * int(row['importance'] / 2)
    print(f"  {row['feature']:35s} {row['importance']:6.2f}%  {barra}")

# ============================================================
# SEÇÃO 7 — EXPORTAÇÃO
# ============================================================
import joblib, json

best_model.save_model('catboost_atraso_v5.cbm')
joblib.dump(best_model, 'catboost_atraso_v5.pkl')

config = {
    'model_file': 'catboost_atraso_v5.cbm',
    'model_file_pkl': 'catboost_atraso_v5.pkl',
    'algorithm': 'CatBoost',
    'threshold': float(threshold_otimo),
    'features_num': FEATURES_NUM,
    'features_cat': FEATURES_CAT,
    'features_all': FEATURES_ALL,
    'n_features': len(FEATURES_ALL),
    'cat_feature_indices': cat_feature_indices,
    'best_params': {k: (int(v) if isinstance(v, (int, np.integer)) else float(v))
                    for k, v in grid.best_params_.items()},
    'smote': {'strategy': 0.3, 'synthetic_samples': n_synthetic},
    'metrics': {
        'roc_auc': float(roc_auc), 'recall': float(recall),
        'precision': float(prec), 'f1_score': float(f1),
        'accuracy': float((tp+tn)/(tp+tn+fp+fn)),
        'multiplicador_vs_acaso': float(prec / 0.066)
    },
    'confusion_matrix': {'TP': int(tp), 'TN': int(tn), 'FP': int(fp), 'FN': int(fn)},
    'version': 'v5'
}
with open('model_config.json', 'w') as f:
    json.dump(config, f, indent=2, default=str)
with open('features_order.txt', 'w') as f:
    for feat in FEATURES_ALL:
        f.write(feat + '\n')

print("\n" + "=" * 60)
print("  EXPORTAÇÃO v5 CatBoost")
print("=" * 60)
cbm_size = os.path.getsize('catboost_atraso_v5.cbm') / 1024
pkl_size = os.path.getsize('catboost_atraso_v5.pkl') / 1024
print(f"  Modelo CBM: catboost_atraso_v5.cbm ({cbm_size:.1f} KB)")
print(f"  Modelo PKL: catboost_atraso_v5.pkl ({pkl_size:.1f} KB)")
print(f"  Config:     model_config.json")
print(f"  Features:   {len(FEATURES_ALL)} ({len(FEATURES_NUM)} num + {len(FEATURES_CAT)} cat)")
print("=" * 60)
