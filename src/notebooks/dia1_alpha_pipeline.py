# %% [markdown]
# # Alpha Squad — Dia 1: Pipeline Completo
# **Cards:** ALPHA-01 (Merge) + ALPHA-02 (Target) + Feature Engineering
#
# **Branch:** `feat/merge-tabelas`
#
# **Objetivo:** Construir o DataFrame Master unificado com todas as features
# prontas para o treinamento do XGBoost.

# %% [markdown]
# ---
# ## Seção 1 — Carga dos Dados
# Carregar as 6 tabelas relevantes para o modelo de previsão de atraso.

# %%
import pandas as pd
import numpy as np
import os
from math import radians, cos, sin, asin, sqrt

# Caminhos absolutos baseados na localizacao do script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATASET_DIR = os.path.join(PROJECT_DIR, 'dataset')
NOTEBOOKS_DIR = SCRIPT_DIR
MODELS_DIR = os.path.join(PROJECT_DIR, 'models')

def banner(secao, titulo):
    """Imprime um separador visual claro entre etapas do pipeline."""
    print(f"\n{'='*70}")
    print(f"  SECAO {secao} -- {titulo}")
    print(f"{'='*70}\n")

# Carregar as 6 tabelas que entram no merge
orders    = pd.read_csv(f'{DATASET_DIR}/olist_orders_dataset.csv')
customers = pd.read_csv(f'{DATASET_DIR}/olist_customers_dataset.csv')
items     = pd.read_csv(f'{DATASET_DIR}/olist_order_items_dataset.csv')
products  = pd.read_csv(f'{DATASET_DIR}/olist_products_dataset.csv')
sellers   = pd.read_csv(f'{DATASET_DIR}/olist_sellers_dataset.csv')
geo       = pd.read_csv(f'{DATASET_DIR}/olist_geolocation_dataset.csv')

banner(1, "CARGA DOS DADOS")
print("=== Tabelas Carregadas ===")
for nome, df in [('orders', orders), ('customers', customers), ('items', items),
                 ('products', products), ('sellers', sellers), ('geo', geo)]:
    print(f"  {nome:12s} -> {df.shape[0]:>10,} linhas x {df.shape[1]} colunas")

# %%
# Verificar tipos de cada tabela
print("\n=== ORDERS - dtypes ===")
print(orders.dtypes)
print(f"\norder_status unicos: {orders['order_status'].unique()}")

# %% [markdown]
# ---
# ## Seção 2 — Limpeza e Tratamento
# Filtrar, remover nulos, converter tipos e tratar valores faltantes.

# %%
banner(2, "LIMPEZA E TRATAMENTO")
# 2.1 — Filtrar apenas pedidos ENTREGUES
print(f"Antes do filtro: {len(orders):,} pedidos")
print(f"Distribuicao de status:\n{orders['order_status'].value_counts()}\n")

orders = orders[orders['order_status'] == 'delivered'].copy()
print(f"Apos filtro (delivered): {len(orders):,} pedidos")

# %%
# 2.2 — Remover pedidos sem data de entrega real (nunca chegaram)
nulos_entrega = orders['order_delivered_customer_date'].isna().sum()
print(f"Nulos em order_delivered_customer_date: {nulos_entrega} ({nulos_entrega/len(orders)*100:.2f}%)")

orders = orders.dropna(subset=['order_delivered_customer_date'])
print(f"Apos remover nulos: {len(orders):,} pedidos")

# %%
# 2.3 — Converter TODAS as colunas de data de string para datetime
date_cols_orders = [
    'order_purchase_timestamp',
    'order_approved_at',
    'order_delivered_carrier_date',
    'order_delivered_customer_date',
    'order_estimated_delivery_date'
]

for col in date_cols_orders:
    orders[col] = pd.to_datetime(orders[col])

print("Tipos apos conversao:")
print(orders[date_cols_orders].dtypes)

# %%
# 2.4 — Tratar nulos em products (1.5% sem categoria e dimensoes)
print(f"\nNulos em products ANTES do tratamento:")
print(products.isnull().sum()[products.isnull().sum() > 0])

# Preencher categoria faltante
products['product_category_name'] = products['product_category_name'].fillna('desconhecido')

# Preencher dimensoes/peso com a mediana (mais robusto que media para outliers)
cols_numericas_products = ['product_weight_g', 'product_length_cm',
                           'product_height_cm', 'product_width_cm',
                           'product_name_lenght', 'product_description_lenght',
                           'product_photos_qty']

for col in cols_numericas_products:
    if products[col].isna().sum() > 0:
        mediana = products[col].median()
        products[col] = products[col].fillna(mediana)
        print(f"  {col}: preenchido com mediana = {mediana}")

print(f"\nNulos em products APOS tratamento:")
print(products.isnull().sum().sum(), "-> zero nulos!")

# %%
# 2.5 — Preparar geolocalização: deduplicar por CEP (media de lat/lng)
print(f"\nGeolocation antes: {len(geo):,} linhas")
print(f"  CEPs unicos: {geo['geolocation_zip_code_prefix'].nunique():,}")
print(f"  Linhas duplicadas: {geo.duplicated().sum():,}")

geo_agg = (
    geo
    .groupby('geolocation_zip_code_prefix', as_index=False)
    .agg({'geolocation_lat': 'mean', 'geolocation_lng': 'mean'})
)

print(f"Geolocation apos agregacao: {len(geo_agg):,} linhas (1 por CEP)")

# %% [markdown]
# ---
# ## Seção 3 — Merge (JOIN) das Tabelas
# Unificar tudo num DataFrame Master seguindo o schema:
# ```
# orders (base)
#   ├── customers  (via customer_id)
#   ├── items      (via order_id)
#   │     ├── products (via product_id)
#   │     └── sellers  (via seller_id)
#   └── geolocation (via zip_code_prefix — seller e customer)
# ```

# %%
banner(3, "MERGE (JOIN) DAS TABELAS")
# 3.1 — orders + customers
df = orders.merge(customers, on='customer_id', how='left')
print(f"orders + customers: {len(df):,} linhas")

# 3.2 — + items (pode gerar mais linhas: pedidos com multiplos itens)
linhas_antes = len(df)
df = df.merge(items, on='order_id', how='left')
print(f"+ items: {len(df):,} linhas (delta: +{len(df) - linhas_antes:,} por pedidos multi-item)")

# 3.3 — + products
df = df.merge(products, on='product_id', how='left')
print(f"+ products: {len(df):,} linhas")

# 3.4 — + sellers
df = df.merge(sellers, on='seller_id', how='left')
print(f"+ sellers: {len(df):,} linhas")

# %%
# 3.5 — + geolocation (seller e customer)

# Geolocalizacao do VENDEDOR
df = df.merge(
    geo_agg.rename(columns={
        'geolocation_zip_code_prefix': 'seller_zip_code_prefix',
        'geolocation_lat': 'seller_lat',
        'geolocation_lng': 'seller_lng'
    }),
    on='seller_zip_code_prefix',
    how='left'
)

# Geolocalizacao do CLIENTE
df = df.merge(
    geo_agg.rename(columns={
        'geolocation_zip_code_prefix': 'customer_zip_code_prefix',
        'geolocation_lat': 'customer_lat',
        'geolocation_lng': 'customer_lng'
    }),
    on='customer_zip_code_prefix',
    how='left'
)

print(f"+ geolocation (seller + customer): {len(df):,} linhas")

# %%
# 3.6 — Validacao pos-merge
print("\n=== VALIDACAO POS-MERGE ===")
print(f"Shape final: {df.shape}")
print(f"Colunas: {list(df.columns)}")
print(f"\nNulos por coluna:")
nulos = df.isnull().sum()
print(nulos[nulos > 0])
print(f"\nTotal de order_ids unicos: {df['order_id'].nunique():,}")
print(f"Total de linhas: {len(df):,}")

# %% [markdown]
# ---
# ## Seção 4 — Variável Alvo: `foi_atraso`
# Criar a coluna target que o XGBoost vai aprender a prever.
# - **1** = entregou DEPOIS do prazo (atrasou)
# - **0** = entregou NO PRAZO ou antes

# %%
banner(4, "VARIAVEL ALVO: foi_atraso")
# 4.1 — Calcular diferenca em dias
df['dias_diferenca'] = (
    df['order_delivered_customer_date'] - df['order_estimated_delivery_date']
).dt.days

# 4.2 — Criar variavel binaria
df['foi_atraso'] = (df['dias_diferenca'] > 0).astype(int)

# 4.3 — Validar distribuicao
print("=== DISTRIBUICAO DA VARIAVEL ALVO ===")
dist = df['foi_atraso'].value_counts(normalize=True)
print(f"  No prazo (0): {dist[0]*100:.2f}%")
print(f"  Atrasou  (1): {dist[1]*100:.2f}%")
print(f"\n  Total: {len(df):,} linhas")
print(f"  Nulos em foi_atraso: {df['foi_atraso'].isna().sum()}")

# Validacao automatica
assert df['foi_atraso'].isna().sum() == 0, "ERRO: ha NaN no target!"
assert 0.03 < df['foi_atraso'].mean() < 0.15, f"ALERTA: distribuicao inesperada ({df['foi_atraso'].mean():.2%})"
print("\n  >>> Validacao OK!")

# %% [markdown]
# ---
# ## Seção 5 — Feature Engineering
# Criar as 6 novas features definidas em `docs/data/atributos_modelo.md`.

# %%
banner(5, "FEATURE ENGINEERING")
# 5.1 — Volume cubico (cm3)
# Hipotese: pacotes maiores = mais dificuldade logistica = mais atraso
df['volume_cm3'] = (
    df['product_length_cm'] * df['product_height_cm'] * df['product_width_cm']
)
print(f"volume_cm3   -> min={df['volume_cm3'].min():.0f}, max={df['volume_cm3'].max():.0f}, media={df['volume_cm3'].mean():.0f}")

# %%
# 5.2 — Ratio frete/preco
# Hipotese: frete desproporcional ao preco indica rotas caras/remotas
df['frete_ratio'] = df['freight_value'] / df['price']
# Tratar divisao por zero (preco = 0, se existir)
df['frete_ratio'] = df['frete_ratio'].replace([np.inf, -np.inf], np.nan).fillna(0)
print(f"frete_ratio  -> min={df['frete_ratio'].min():.3f}, max={df['frete_ratio'].max():.3f}, media={df['frete_ratio'].mean():.3f}")

# %%
# 5.3 — Velocidade do lojista (dias para despachar)
# Hipotese: lojistas lentos = atraso na cadeia inteira
df['velocidade_lojista_dias'] = (
    df['order_delivered_carrier_date'] - df['order_approved_at']
).dt.days

# Preencher NaN (pedidos sem data de aprovacao ou despacho)
df['velocidade_lojista_dias'] = df['velocidade_lojista_dias'].fillna(
    df['velocidade_lojista_dias'].median()
)
print(f"velocidade_lojista_dias -> min={df['velocidade_lojista_dias'].min():.0f}, max={df['velocidade_lojista_dias'].max():.0f}, media={df['velocidade_lojista_dias'].mean():.1f}")

# %%
# 5.4 — Dia da semana da compra (0=Segunda, 6=Domingo)
# Hipotese: compras na sexta/sabado podem encalhar no fim de semana
df['dia_semana_compra'] = df['order_purchase_timestamp'].dt.dayofweek
print(f"dia_semana_compra -> distribuicao:")
print(df['dia_semana_compra'].value_counts().sort_index())

# %%
# 5.5 — Rota interestadual (booleana)
# Hipotese: pedidos cruzando fronteiras estaduais tem mais chance de atraso
df['rota_interestadual'] = (df['seller_state'] != df['customer_state']).astype(int)
print(f"\nrota_interestadual -> distribuicao:")
print(df['rota_interestadual'].value_counts(normalize=True).apply(lambda x: f"{x:.1%}"))

# %%
# 5.6 — Distancia Haversine (km) entre vendedor e cliente
# Hipotese: quanto maior a distancia, maior o risco de atraso

def haversine(lat1, lng1, lat2, lng2):
    """Calcula a distancia em km entre dois pontos usando a formula de Haversine."""
    # Converter para radianos
    lat1, lng1, lat2, lng2 = map(np.radians, [lat1, lng1, lat2, lng2])
    
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlng/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    
    # Raio da Terra em km
    r = 6371
    return c * r

df['distancia_haversine_km'] = haversine(
    df['seller_lat'], df['seller_lng'],
    df['customer_lat'], df['customer_lng']
)

# %%
# 5.7 — Carrinho Cheio (total_itens_pedido)
# Hipotese: Mais itens na mesma compra = logistica mais dificil (tempo de separacao maior)
df['total_itens_pedido'] = df.groupby('order_id')['order_item_id'].transform('max')
# Tratar possiveis linhas onde a contagem ficou nula
df['total_itens_pedido'] = df['total_itens_pedido'].fillna(1).astype(int)
print(f"\ntotal_itens_pedido -> min={df['total_itens_pedido'].min()}, max={df['total_itens_pedido'].max()}, media={df['total_itens_pedido'].mean():.1f}")

# %%
# 5.8 — Risco Financeiro / Item Premium (ticket_medio_alto)
# Hipotese: Produtos mais caros recebem prioridade logistica e transportadoras mais rapidas
# Flag 1 se o produto custar mais de R$ 500, CC 0
df['ticket_medio_alto'] = (df['price'] >= 500.0).astype(int)
print(f"\nticket_medio_alto (> R$ 500) -> {df['ticket_medio_alto'].sum():,} pedidos ({df['ticket_medio_alto'].mean():.1%})")

# %%
# 5.9 — Macro-Regioes do Brasil
# Hipotese: Atrasos sao maiores enviando do Sudeste pro Norte do que Sul pro Sudeste
regioes_map = {
    'AM': 'Norte', 'RR': 'Norte', 'AP': 'Norte', 'PA': 'Norte', 'TO': 'Norte', 'RO': 'Norte', 'AC': 'Norte',
    'MA': 'Nordeste', 'PI': 'Nordeste', 'CE': 'Nordeste', 'RN': 'Nordeste', 'PE': 'Nordeste', 'PB': 'Nordeste', 'SE': 'Nordeste', 'AL': 'Nordeste', 'BA': 'Nordeste',
    'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'DF': 'Centro-Oeste',
    'SP': 'Sudeste', 'RJ': 'Sudeste', 'ES': 'Sudeste', 'MG': 'Sudeste',
    'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul'
}

df['seller_regiao'] = df['seller_state'].map(regioes_map)
df['customer_regiao'] = df['customer_state'].map(regioes_map)
print(f"\nRegioes mapeadas com sucesso. Clientes no Nordeste: {(df['customer_regiao'] == 'Nordeste').sum():,} pedidos")

# Preencher NaN (CEPs sem geolocalizacao) com a mediana
nulos_dist = df['distancia_haversine_km'].isna().sum()
print(f"distancia_haversine_km -> {nulos_dist} nulos ({nulos_dist/len(df)*100:.1f}%)")
df['distancia_haversine_km'] = df['distancia_haversine_km'].fillna(
    df['distancia_haversine_km'].median()
)
print(f"  min={df['distancia_haversine_km'].min():.0f} km, max={df['distancia_haversine_km'].max():.0f} km, media={df['distancia_haversine_km'].mean():.0f} km")

# %% [markdown]
# ---
# ## Seção 6 — EDA: Correlações de Pearson
# Analisar quais variáveis numéricas correlacionam com `foi_atraso`.

# %%
import plotly.express as px
import plotly.graph_objects as go
import time
import os

banner(6, "EDA: CORRELACOES DE PEARSON")
# 6.1 — Correlacao de Pearson com a variavel alvo
colunas_numericas = df.select_dtypes(include='number').columns.tolist()

# Remover IDs e colunas que nao devem ser analisadas
excluir_corr = ['order_item_id', 'customer_zip_code_prefix', 'seller_zip_code_prefix',
                'dias_diferenca']  # dias_diferenca e' derivada do target
colunas_analise = [c for c in colunas_numericas if c not in excluir_corr]

corr_target = df[colunas_analise].corr()['foi_atraso'].drop('foi_atraso').sort_values()

print("=== CORRELACAO DE PEARSON COM foi_atraso ===")
for feat, val in corr_target.items():
    sinal = "+" if val > 0 else ""
    print(f"  {feat:35s} {sinal}{val:.4f}")

# %%
# 6.2 — Grafico de barras das correlacoes
fig_corr = px.bar(
    x=corr_target.values,
    y=corr_target.index,
    orientation='h',
    title='Correlacao de Pearson com foi_atraso',
    labels={'x': 'Correlacao', 'y': 'Feature'},
    color=corr_target.values,
    color_continuous_scale='RdBu_r'
)
fig_corr.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
fig_corr.write_html(os.path.join(NOTEBOOKS_DIR, 'eda_1_correlacoes.html'))
time.sleep(1.5)
fig_corr.show()

# %%
# 6.3 — Heatmap completo de correlacoes entre features
corr_matrix = df[colunas_analise].corr()

fig_heat = px.imshow(
    corr_matrix,
    text_auto='.2f',
    title='Matriz de Correlacao — Features Numericas',
    color_continuous_scale='RdBu_r',
    zmin=-1, zmax=1,
    aspect='auto'
)
fig_heat.update_layout(height=700, width=800)
fig_heat.write_html(os.path.join(NOTEBOOKS_DIR, 'eda_2_heatmap_features.html'))
time.sleep(1.5)
fig_heat.show()

# %%
# 6.4 — Investigar multicolinearidade
print("\n=== MULTICOLINEARIDADE (correlacoes > 0.7 entre features) ===")
for i, col1 in enumerate(colunas_analise):
    for col2 in colunas_analise[i+1:]:
        if col1 == 'foi_atraso' or col2 == 'foi_atraso':
            continue
        c = abs(corr_matrix.loc[col1, col2])
        if c > 0.7:
            print(f"  {col1} x {col2} = {c:.3f} <- ALTA CORRELACAO")

# %%
# 6.5 — Distribuicao do target por features categoricas
print("\n=== TAXA DE ATRASO POR ROTA ===")
print(df.groupby('rota_interestadual')['foi_atraso'].mean().apply(lambda x: f"{x:.2%}"))

print("\n=== TAXA DE ATRASO POR DIA DA SEMANA ===")
print(df.groupby('dia_semana_compra')['foi_atraso'].mean().apply(lambda x: f"{x:.2%}"))

# %%
# 6.6 — Piores Vendedores (seller_id)
# Filtrar vendedores com mais de 30 pedidos fechados para ter validade estatistica
vendedores = df.groupby('seller_id').agg(
    total_pedidos=('order_id', 'count'),
    taxa_atraso=('foi_atraso', 'mean')
).reset_index()
piores_vendedores = vendedores[vendedores['total_pedidos'] >= 30].sort_values('taxa_atraso', ascending=False)

print("\n=== TOP 10 PIORES VENDEDORES (Minimo 30 pedidos) ===")
print(piores_vendedores.head(10).apply(
    lambda r: f"Seller: {r['seller_id']} | Pedidos: {r['total_pedidos']:4.0f} | Atraso: {r['taxa_atraso']:.2%}", axis=1
).to_string(index=False))

# Acao de negocio: O time Omega poderia pausar temporariamente as lojas desses sellers.

# %%
# 6.7 — Piores Categorias de Produto
categorias = df.groupby('product_category_name').agg(
    total_pedidos=('order_id', 'count'),
    taxa_atraso=('foi_atraso', 'mean')
).reset_index()
piores_categorias = categorias[categorias['total_pedidos'] >= 100].sort_values('taxa_atraso', ascending=False)

print("\n=== TOP 10 PIORES CATEGORIAS (Minimo 100 pedidos) ===")
print(piores_categorias.head(10).apply(
    lambda r: f"{r['product_category_name'][:30]:<30} | Pedidos: {r['total_pedidos']:5.0f} | Atraso: {r['taxa_atraso']:.2%}", axis=1
).to_string(index=False))

# Plotar as piores categorias
fig_cat = px.bar(
    piores_categorias.head(15), 
    x='taxa_atraso', 
    y='product_category_name', 
    orientation='h',
    title='Top 15 Categorias com Maior Risco de Atraso (>100 Pedidos)',
    text_auto='.1%',
    labels={'product_category_name': 'Categoria do Produto', 'taxa_atraso': 'Taxa de Atraso'},
    color='taxa_atraso',
    color_continuous_scale='Reds'
)
fig_cat.update_layout(yaxis={'categoryorder':'total ascending'})
fig_cat.write_html(os.path.join(NOTEBOOKS_DIR, 'eda_3_piores_categorias.html'))
time.sleep(1.5)
fig_cat.show()

# %%
# 6.8 — Mapa de Calor por Rotas Geograficas (Estado Origem -> Estado Destino)
rotas = df.groupby(['seller_state', 'customer_state']).agg(
    total_pedidos=('order_id', 'count'),
    taxa_atraso=('foi_atraso', 'mean')
).reset_index()

# Filtrar rotas com volume minimo (ex: >= 50 pedidos) para remover ruidos estatisticos
rotas_freq = rotas[rotas['total_pedidos'] >= 50]
matriz_rotas = rotas_freq.pivot(index='seller_state', columns='customer_state', values='taxa_atraso')

fig_rotas = px.imshow(
    matriz_rotas,
    text_auto='.1%',
    title='Heatmap: Taxa de Atraso por Rota (Origem -> Destino) [Min. 50 Pedidos]',
    labels=dict(x="Estado Cliente (Destino)", y="Estado Vendedor (Origem)", color="Taxa Atraso"),
    color_continuous_scale='Reds'
)
fig_rotas.update_layout(height=800, width=1000)
fig_rotas.write_html(os.path.join(NOTEBOOKS_DIR, 'eda_4_heatmap_rotas.html'))
time.sleep(1.5)
fig_rotas.show()

# %%
# 6.9 — Mapa de Calor por MACRO-REGIOES Geograficas (Vendedor Origem -> Cliente Destino)
rotas_regiao = df.groupby(['seller_regiao', 'customer_regiao']).agg(
    total_pedidos=('order_id', 'count'),
    taxa_atraso=('foi_atraso', 'mean')
).reset_index()

# Filtrar rotas com volume minimo (ex: >= 50 pedidos)
rotas_regiao_freq = rotas_regiao[rotas_regiao['total_pedidos'] >= 50]
matriz_regioes = rotas_regiao_freq.pivot(index='seller_regiao', columns='customer_regiao', values='taxa_atraso')

fig_regioes = px.imshow(
    matriz_regioes,
    text_auto='.1%',
    title='Heatmap: Taxa de Atraso por MACRO-REGIAO (Origem -> Destino)',
    labels=dict(x="Regiao Cliente (Destino)", y="Regiao Vendedor (Origem)", color="Taxa Atraso"),
    color_continuous_scale='Reds'
)
fig_regioes.update_layout(height=600, width=800)
fig_regioes.write_html(os.path.join(NOTEBOOKS_DIR, 'eda_5_heatmap_regioes.html'))
time.sleep(1.5)
fig_regioes.show()

# %% [markdown]
# ---
# ## Resumo Final

# %%
banner(7, "RESUMO FINAL E EXPORTACAO")

# Resumo das features engenhadas
print("=== FEATURES ENGENHADAS ===")
features_novas = ['volume_cm3', 'frete_ratio', 'velocidade_lojista_dias',
                  'dia_semana_compra', 'rota_interestadual', 'distancia_haversine_km',
                  'total_itens_pedido', 'ticket_medio_alto', 'seller_regiao', 'customer_regiao']

for feat in features_novas:
    nulos = df[feat].isna().sum()
    print(f"  {feat:30s} dtype={str(df[feat].dtype):8s} nulos={nulos}")

print(f"\n=== DATAFRAME FINAL ===")
print(f"  Shape: {df.shape}")
print(f"  Pedidos unicos: {df['order_id'].nunique():,}")
print(f"  Taxa de atraso (Total): {df['foi_atraso'].mean():.2%}")

# %%
# Exportar CSV unificado
output_path = os.path.join(NOTEBOOKS_DIR, 'dataset_unificado_v1.csv')
df.to_csv(output_path, index=False)
print(f"\nDataset salvo em: {output_path}")
print(f"Tamanho: {len(df):,} linhas x {len(df.columns)} colunas")

print("\n" + "=" * 60)
print("   PIPELINE DATA PREP & EDA COMPLETO!")
print("=" * 60)
print(f"  Dataset gerado: {output_path}")
print(f"  Graficos salvos em: {NOTEBOOKS_DIR}/eda_*.html")
print("=" * 60)

