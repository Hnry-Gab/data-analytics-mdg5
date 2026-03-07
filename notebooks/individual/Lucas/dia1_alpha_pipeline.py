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
import webbrowser
from math import radians, cos, sin, asin, sqrt

# Caminhos absolutos (compativeis com Script e Notebook)
try:
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    CURRENT_DIR = os.getcwd()

PROJECT_DIR = CURRENT_DIR
while not os.path.exists(os.path.join(PROJECT_DIR, 'dataset')) and PROJECT_DIR != os.path.dirname(PROJECT_DIR):
    PROJECT_DIR = os.path.dirname(PROJECT_DIR)

DATASET_DIR = os.path.join(PROJECT_DIR, 'dataset')
NOTEBOOKS_DIR = CURRENT_DIR
MODELS_DIR = os.path.join(PROJECT_DIR, 'models')

def banner(secao, titulo):
    """Imprime um separador visual claro entre etapas do pipeline."""
    print(f"\n{'='*70}")
    print(f"  SECAO {secao} -- {titulo}")
    print(f"{'='*70}\n")

# Carregar as 7 tabelas relevantes
orders    = pd.read_csv(f'{DATASET_DIR}/olist_orders_dataset.csv')
customers = pd.read_csv(f'{DATASET_DIR}/olist_customers_dataset.csv')
items     = pd.read_csv(f'{DATASET_DIR}/olist_order_items_dataset.csv')
products  = pd.read_csv(f'{DATASET_DIR}/olist_products_dataset.csv')
sellers   = pd.read_csv(f'{DATASET_DIR}/olist_sellers_dataset.csv')
geo       = pd.read_csv(f'{DATASET_DIR}/olist_geolocation_dataset.csv')
payments  = pd.read_csv(f'{DATASET_DIR}/olist_order_payments_dataset.csv')

banner(1, "CARGA DOS DADOS")
print("=== Tabelas Carregadas ===")
for nome, df_ in [('orders', orders), ('customers', customers), ('items', items),
                  ('products', products), ('sellers', sellers), ('geo', geo), ('payments', payments)]:
    print(f"  {nome:12s} -> {df_.shape[0]:>10,} linhas x {df_.shape[1]} colunas")

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

# %%
# 2.6 — Preparar pagamentos: extrair o metodo de pagamento principal (maior valor)
# Alguns pedidos sao pagos parte cartao, parte voucher. Vamos pegar o de maior peso.
payments_sorted = payments.sort_values(by=['order_id', 'payment_value'], ascending=[True, False])
# Drop duplicates mantendo o primeiro (que e o de maior valor por causa do sort desc)
payments_agg = payments_sorted.drop_duplicates(subset=['order_id'], keep='first')[['order_id', 'payment_type']]
print(f"Pagamentos apos achar principal: {len(payments_agg):,} linhas unicas")

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

# 3.6 — + pagamentos (tipo principal)
df = df.merge(payments_agg.rename(columns={'payment_type': 'tipo_pagamento_principal'}), on='order_id', how='left')
df['tipo_pagamento_principal'] = df['tipo_pagamento_principal'].fillna('desconhecido')
print(f"+ payments (tipo_pagamento_principal): {len(df):,} linhas")

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

# %%
# 5.10 — Historico de Atraso do Vendedor (ANTI-LEAKAGE: usa expanding window)
# Hipotese: vendedores reincidentes tem taxa de atraso futura alta
# CUIDADO: calculamos a media CUMULATIVA ate ANTES da data do pedido atual
df = df.sort_values('order_purchase_timestamp').reset_index(drop=True)

# Para cada vendedor, calcular a taxa de atraso acumulada historica
df['historico_atraso_seller'] = (
    df.groupby('seller_id')['foi_atraso']
    .transform(lambda x: x.expanding().mean().shift(1))
)
# Primeiro pedido de cada seller nao tem historico -> preencher com a media global
media_global_atraso = df['foi_atraso'].mean()
df['historico_atraso_seller'] = df['historico_atraso_seller'].fillna(media_global_atraso)
print(f"\nhistorico_atraso_seller -> min={df['historico_atraso_seller'].min():.3f}, max={df['historico_atraso_seller'].max():.3f}, media={df['historico_atraso_seller'].mean():.3f}")

# %%
# 5.11 — Velocidade da Transportadora (dias de transito)
# Hipotese: transportadora lenta = atraso independente do lojista
df['velocidade_transportadora_dias'] = (
    df['order_delivered_customer_date'] - df['order_delivered_carrier_date']
).dt.days
df['velocidade_transportadora_dias'] = df['velocidade_transportadora_dias'].fillna(
    df['velocidade_transportadora_dias'].median()
)
print(f"velocidade_transportadora_dias -> min={df['velocidade_transportadora_dias'].min():.0f}, max={df['velocidade_transportadora_dias'].max():.0f}, media={df['velocidade_transportadora_dias'].mean():.1f}")

# %%
# 5.12 — Compra no Fim de Semana (flag)
# Hipotese: pedidos feitos sexta-domingo demoram mais por causa do gap do fim de semana
df['compra_fds'] = (df['dia_semana_compra'] >= 5).astype(int)
print(f"compra_fds -> {df['compra_fds'].sum():,} pedidos no FDS ({df['compra_fds'].mean():.1%})")

# %%
# 5.13 — Mes da Compra (sazonalidade)
# Hipotese: meses de pico (novembro=Black Friday, dezembro=Natal) overload logistico
df['mes_compra'] = df['order_purchase_timestamp'].dt.month
print(f"mes_compra -> distribuicao:")
print(df['mes_compra'].value_counts().sort_index())

# %%
# 5.14 — Valor Total do Pedido (price + freight)
# Hipotese: pedidos de alto valor podem ter logistica diferenciada
df['valor_total_pedido'] = df['price'] + df['freight_value']
print(f"\nvalor_total_pedido -> min={df['valor_total_pedido'].min():.2f}, max={df['valor_total_pedido'].max():.2f}, media={df['valor_total_pedido'].mean():.2f}")

# %%
# 5.15 — Capital vs Interior
capitais = [
    'rio branco', 'maceio', 'macapa', 'manaus', 'salvador', 'fortaleza', 'brasilia', 'vitoria',
    'goiania', 'sao luis', 'cuiaba', 'campo grande', 'belo horizonte', 'belem', 'joao pessoa',
    'curitiba', 'recife', 'teresina', 'rio de janeiro', 'natal', 'porto alegre', 'porto velho',
    'boa vista', 'florianopolis', 'sao paulo', 'aracaju', 'palmas'
]

df['destino_tipo'] = np.where(df['customer_city'].str.lower().isin(capitais), 'Capital', 'Interior')
print(f"\ndestino_tipo -> Capital: {(df['destino_tipo'] == 'Capital').sum():,}, Interior: {(df['destino_tipo'] == 'Interior').sum():,}")

# Preencher NaN (CEPs sem geolocalizacao) com a mediana das distancias antes de dropar nulos absolutos
nulos_dist = df['distancia_haversine_km'].isna().sum()
print(f"\ndistancia_haversine_km -> {nulos_dist} nulos ({nulos_dist/len(df)*100:.1f}%)")
df['distancia_haversine_km'] = df['distancia_haversine_km'].fillna(
    df['distancia_haversine_km'].median()
)

# Limpeza Final (Dropna agressivo)
print(f"\n=== DROPNA FINAL ===")
linhas_antes_dropna = len(df)
df = df.dropna()
linhas_dropadas = linhas_antes_dropna - len(df)
print(f"Limpeza de Nulos: {linhas_dropadas:,} linhas removidas.")
print(f"Dataset final garantido sem NaNs: {len(df):,} linhas restantes.")
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
df_pearson_plot = pd.DataFrame({'Feature': corr_target.index, 'Pearson': corr_target.values})
df_pearson_plot['Sinal'] = np.where(df_pearson_plot['Pearson'] > 0, 'Positiva (Atrasa mais)', 'Negativa (Atrasa menos)')

fig_corr = px.bar(
    df_pearson_plot,
    x='Pearson',
    y='Feature',
    orientation='h',
    title='Correlacao de Pearson com foi_atraso',
    color='Sinal',
    color_discrete_map={'Positiva (Atrasa mais)': '#e74c3c', 'Negativa (Atrasa menos)': '#3498db'}
)
fig_corr.update_layout(
    height=600, 
    yaxis={'categoryorder': 'total ascending'},
    margin=dict(l=200, r=20, t=50, b=50)
)
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
# Aumento do minimo para 300 para filtrar ruidos estatísticos e limpar o gráfico
piores_categorias = categorias[categorias['total_pedidos'] >= 300].sort_values('taxa_atraso', ascending=False)

print("\n=== TOP 10 PIORES CATEGORIAS (Minimo 300 pedidos) ===")
print(piores_categorias.head(10).apply(
    lambda r: f"{r['product_category_name'][:30]:<30} | Pedidos: {r['total_pedidos']:5.0f} | Atraso: {r['taxa_atraso']:.2%}", axis=1
).to_string(index=False))

# Plotar as piores categorias
fig_cat = px.bar(
    piores_categorias.head(15), 
    x='taxa_atraso', 
    y='product_category_name', 
    orientation='h',
    title='Top 15 Categorias com Maior Risco de Atraso (>300 Pedidos)',
    text_auto='.1%',
    labels={'product_category_name': 'Categoria do Produto', 'taxa_atraso': 'Taxa de Atraso'},
    color='taxa_atraso',
    color_continuous_scale='Reds'
)
fig_cat.update_traces(textposition='outside')
fig_cat.update_layout(
    yaxis={'categoryorder':'total ascending'},
    margin=dict(l=200, r=40, t=50, b=20),
    height=600
)
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
    title='Heatmap: Taxa de Atraso por Rota Geográfica (Origem -> Destino) [Min. 50 Pedidos]',
    labels=dict(x="Estado Cliente (Destino)", y="Estado Vendedor (Origem)", color="Taxa Atraso"),
    color_continuous_scale='Reds'
)
# Reduzir fonte e arrumar proporcoes para o Heatmap nao sobrepor textos
fig_rotas.update_traces(textfont_size=9)
fig_rotas.update_layout(
    height=800, 
    width=1000,
    xaxis_tickangle=-45
)
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
fig_regioes.update_traces(textfont_size=11)
fig_regioes.update_layout(
    height=600, 
    width=800,
    xaxis_tickangle=-45
)
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
                  'total_itens_pedido', 'ticket_medio_alto', 'seller_regiao', 'customer_regiao',
                  'historico_atraso_seller', 'velocidade_transportadora_dias',
                  'compra_fds', 'mes_compra', 'valor_total_pedido']

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

# %% [markdown]
# ---
# ## Seção 8 — Correlações Avançadas (Spearman + Point-Biserial + Cramér's V)
# O professor pediu múltiplos métodos de correlação. Pearson mede relações LINEARES,
# mas nem toda relação é linear. Abaixo usamos 4 métodos complementares.

# %%
banner(8, "CORRELACOES AVANCADAS E MUTUAL INFORMATION")
from scipy.stats import spearmanr, pointbiserialr, chi2_contingency
from sklearn.feature_selection import mutual_info_classif

# 8.1 — Definir features numericas para analise (excluir IDs, target, etc.)
features_num_eda = [
    'price', 'freight_value', 'product_weight_g', 'volume_cm3',
    'frete_ratio', 'velocidade_lojista_dias', 'dia_semana_compra',
    'rota_interestadual', 'distancia_haversine_km', 'total_itens_pedido',
    'ticket_medio_alto', 'historico_atraso_seller', 'velocidade_transportadora_dias',
    'compra_fds', 'mes_compra', 'valor_total_pedido'
]

features_cat_eda = ['customer_state', 'seller_state', 'product_category_name',
                    'seller_regiao', 'customer_regiao', 'destino_tipo', 'tipo_pagamento_principal']

# %%
# 8.1.5 — MUTUAL INFORMATION (A métrica Suprema para Relações Não-Lineares)
# Mutual Information mede a redução da incerteza sobre o Alvo dado o conhecimento das Features.
# É excelente porque pega TODO tipo de relação estatística (linear e não-linear, categóricas ordinais, etc).
print("=== MUTUAL INFORMATION SCORE (Importância Pura) ===")

# Separar X e y sem nulos para o cálculo de MI
df_mi = df[features_num_eda + ['foi_atraso']].dropna()
X_mi = df_mi[features_num_eda]
y_mi = df_mi['foi_atraso']

# Calcular MI (usamos classif pois o alvo é discreto 0/1)
mi_scores = mutual_info_classif(X_mi, y_mi, random_state=42)

df_mi_res = pd.DataFrame({'Feature': features_num_eda, 'MI_Score': mi_scores})
df_mi_res = df_mi_res.sort_values('MI_Score', ascending=False)

print(f"{'Feature':40s} {'MI Score (Bits)':>15s}")
print("-" * 56)
for _, row in df_mi_res.iterrows():
    print(f"  {row['Feature']:38s} {row['MI_Score']:>15.4f}")

fig_mi = px.bar(
    df_mi_res.sort_values('MI_Score'),
    x='MI_Score', y='Feature', orientation='h',
    title='Mutual Information Score (Linear + Não-Linear)',
    text=df_mi_res.sort_values('MI_Score')['MI_Score'].apply(lambda x: f'{x:.4f}'),
    color='MI_Score', color_continuous_scale='Teal'
)
fig_mi.update_traces(textposition='outside')
fig_mi.update_layout(height=600, yaxis={'categoryorder': 'total ascending'}, margin=dict(l=250, r=40, t=50, b=20))
fig_mi.show()

# %%
# 8.2 — Correlação de SPEARMAN (captura relações NÃO-lineares e monotônicas)
# Diferença: Pearson mede relação LINEAR. Spearman mede relação MONOTÔNICA
# (se uma sobe, a outra sobe, mas não necessariamente em linha reta).
# É também mais robusta contra outliers.

print("=== CORRELACAO DE SPEARMAN COM foi_atraso ===")
print(f"{'Feature':40s} {'Spearman':>10s} {'p-valor':>12s} {'Signif?':>8s}")
print("-" * 72)

resultados_spearman = []
for feat in features_num_eda:
    serie = df[[feat, 'foi_atraso']].dropna()
    if len(serie) > 100:
        corr_sp, pval_sp = spearmanr(serie[feat], serie['foi_atraso'])
        sig = "Sim" if pval_sp < 0.05 else "Nao"
        print(f"  {feat:38s} {corr_sp:>+10.4f} {pval_sp:>12.2e} {sig:>8s}")
        resultados_spearman.append({
            'Feature': feat, 'Spearman': round(corr_sp, 4),
            'p_valor_sp': pval_sp, 'Significativo': sig
        })

df_spearman = pd.DataFrame(resultados_spearman).sort_values('Spearman', key=abs, ascending=False)
df_spearman['Sinal'] = np.where(df_spearman['Spearman'] > 0, 'Positiva (Atrasa mais)', 'Negativa (Atrasa menos)')

fig_spearman = px.bar(
    df_spearman.sort_values('Spearman'),
    x='Spearman', y='Feature', orientation='h',
    title='Correlação de Spearman vs foi_atraso (captura relações não-lineares)',
    color='Sinal',
    color_discrete_map={'Positiva (Atrasa mais)': '#e74c3c', 'Negativa (Atrasa menos)': '#3498db'},
    text=df_spearman.sort_values('Spearman')['Spearman'].apply(lambda x: f'{x:+.4f}')
)
fig_spearman.update_traces(textposition='outside')
fig_spearman.update_layout(
    height=600, 
    yaxis={'categoryorder': 'total ascending'},
    margin=dict(l=250, r=40, t=50, b=20)
)
fig_spearman.show()

# %%
# 8.3 — Correlação POINT-BISERIAL com p-valor
# É a versão correta de Pearson quando o target é BINÁRIO (0/1).
# Matematicamente equivalente, mas nos dá o p-valor de significância.

print("\n=== CORRELACAO POINT-BISERIAL COM foi_atraso ===")
print(f"{'Feature':40s} {'PtBiserial':>12s} {'p-valor':>12s} {'Signif?':>8s}")
print("-" * 74)

resultados_pb = []
for feat in features_num_eda:
    serie = df[[feat, 'foi_atraso']].dropna()
    if len(serie) > 100:
        corr_pb, pval_pb = pointbiserialr(serie['foi_atraso'], serie[feat])
        sig = "Sim" if pval_pb < 0.05 else "Nao"
        print(f"  {feat:38s} {corr_pb:>+12.4f} {pval_pb:>12.2e} {sig:>8s}")
        resultados_pb.append({
            'Feature': feat, 'PointBiserial': round(corr_pb, 4),
            'p_valor_pb': pval_pb, 'Significativo': sig
        })

df_pb = pd.DataFrame(resultados_pb).sort_values('PointBiserial', key=abs, ascending=False)

# %%
# 8.4 — CRAMÉR'S V + QUI-QUADRADO para features CATEGÓRICAS
# Pearson/Spearman não funcionam com texto (ex: "SP", "RJ").
# Cramér's V mede FORÇA da associação (0 a 1).
# Qui-Quadrado dá o p-valor (se a associação é estatisticamente significativa).

def cramers_v(x, y):
    """Calcula Cramér's V entre duas variáveis categóricas."""
    tabela = pd.crosstab(x, y)
    chi2 = chi2_contingency(tabela)[0]
    n = tabela.sum().sum()
    phi2 = chi2 / n
    r, k = tabela.shape
    phi2corr = max(0, phi2 - ((k-1)*(r-1))/(n-1))
    rcorr = r - ((r-1)**2)/(n-1)
    kcorr = k - ((k-1)**2)/(n-1)
    return np.sqrt(phi2corr / min((kcorr-1), (rcorr-1))) if min(kcorr, rcorr) > 1 else 0

print("\n=== CRAMÉR'S V + QUI-QUADRADO (CATEGORICAS vs foi_atraso) ===")
print(f"{'Feature':35s} {'Cramér V':>10s} {'Chi2':>12s} {'p-valor':>12s} {'N categ.':>10s}")
print("-" * 82)

resultados_cramer = []
for feat in features_cat_eda:
    serie = df[[feat, 'foi_atraso']].dropna()
    cv = cramers_v(serie[feat], serie['foi_atraso'])
    tabela = pd.crosstab(serie[feat], serie['foi_atraso'])
    chi2_val, p_val, dof, expected = chi2_contingency(tabela)
    n_cat = serie[feat].nunique()
    sig = "Sim" if p_val < 0.05 else "Nao"
    print(f"  {feat:33s} {cv:>10.4f} {chi2_val:>12.1f} {p_val:>12.2e} {n_cat:>10d}")
    resultados_cramer.append({
        'Feature': feat, 'CramersV': round(cv, 4),
        'Chi2': round(chi2_val, 1), 'p_valor_chi2': p_val,
        'N_categorias': n_cat, 'Significativo': sig
    })

df_cramer = pd.DataFrame(resultados_cramer).sort_values('CramersV', ascending=False)

# Grafico Cramer
fig_cramer = px.bar(
    df_cramer.sort_values('CramersV'),
    x='CramersV', y='Feature', orientation='h',
    title="Cramér's V — Força de Associação das Categóricas vs foi_atraso",
    color='CramersV', color_continuous_scale='Oranges',
    text=df_cramer.sort_values('CramersV')['CramersV'].apply(lambda x: f'{x:.4f}')
)
fig_cramer.update_traces(textposition='outside')
fig_cramer.update_layout(
    height=400, 
    yaxis={'categoryorder': 'total ascending'},
    margin=dict(l=150, r=40, t=50, b=20)
)
fig_cramer.show()

# %% [markdown]
# ---
# ## Seção 9 — Forest Plot (Comparação Visual de Todos os Métodos)
# O Forest Plot mostra o coeficiente de correlação de cada variável com
# seu intervalo de confiança. É o gráfico clássico de estatística para
# comparar múltiplas variáveis de uma só vez.

# %%
banner(9, "FOREST PLOT — COMPARACAO VISUAL")

# Montar DataFrame consolidado com Pearson + Spearman + Point-Biserial
df_consolidado = df_pb[['Feature', 'PointBiserial']].merge(
    df_spearman[['Feature', 'Spearman']], on='Feature', how='left'
)

# Calcular intervalo de confiança aproximado (IC 95% ~ ± 1.96/sqrt(n))
n_obs = len(df)
ic_95 = 1.96 / np.sqrt(n_obs)

df_consolidado['IC_lower_PB'] = df_consolidado['PointBiserial'] - ic_95
df_consolidado['IC_upper_PB'] = df_consolidado['PointBiserial'] + ic_95
df_consolidado = df_consolidado.sort_values('PointBiserial', key=abs, ascending=True)

# Forest Plot com go.Scatter (pontos + linhas de erro)
fig_forest = go.Figure()

# Ponto central (Point-Biserial)
fig_forest.add_trace(go.Scatter(
    x=df_consolidado['PointBiserial'],
    y=df_consolidado['Feature'],
    mode='markers',
    marker=dict(size=10, color='#2c3e50', symbol='diamond'),
    name='Point-Biserial',
    error_x=dict(
        type='data',
        symmetric=False,
        array=(df_consolidado['IC_upper_PB'] - df_consolidado['PointBiserial']).tolist(),
        arrayminus=(df_consolidado['PointBiserial'] - df_consolidado['IC_lower_PB']).tolist(),
        color='#2c3e50', thickness=1.5
    )
))

# Spearman (pontos secundarios)
fig_forest.add_trace(go.Scatter(
    x=df_consolidado['Spearman'],
    y=df_consolidado['Feature'],
    mode='markers',
    marker=dict(size=8, color='#e74c3c', symbol='circle'),
    name='Spearman'
))

# Linha de referencia no zero
fig_forest.add_vline(x=0, line_dash="dash", line_color="gray", line_width=1)

fig_forest.update_layout(
    title='Forest Plot — Correlações com foi_atraso (IC 95%)',
    xaxis_title='Coeficiente de Correlação',
    yaxis_title='Feature',
    height=600, width=900,
    font=dict(size=12),
    legend=dict(x=0.75, y=0.05),
    margin=dict(l=220, r=40, t=50, b=50)
)
fig_forest.show()

# %% [markdown]
# ---
# ## Seção 10 — Tabela-Resumo — Todas as Correlações Consolidadas
# Consolida Pearson, Spearman, Point-Biserial e Cramér's V numa só tabela.

# %%
banner(10, "TABELA-RESUMO DE CORRELACOES")

# Pearson ja calculado na Secao 6
df_pearson_resumo = corr_target.reset_index()
df_pearson_resumo.columns = ['Feature', 'Pearson']

# Juntar tudo
df_resumo = df_pearson_resumo.merge(
    df_spearman[['Feature', 'Spearman']], on='Feature', how='left'
).merge(
    df_pb[['Feature', 'PointBiserial', 'p_valor_pb']], on='Feature', how='left'
).merge(
    df_mi_res[['Feature', 'MI_Score']], on='Feature', how='left'
)

# Adicionar categoricas (Cramer)
for _, row in df_cramer.iterrows():
    nova_linha = pd.DataFrame([{
        'Feature': row['Feature'],
        'Pearson': np.nan,
        'Spearman': np.nan,
        'PointBiserial': np.nan,
        'MI_Score': np.nan,
        'p_valor_pb': row['p_valor_chi2'],
        'CramersV': row['CramersV']
    }])
    df_resumo = pd.concat([df_resumo, nova_linha], ignore_index=True)

if 'CramersV' not in df_resumo.columns:
    df_resumo['CramersV'] = np.nan

# Preencher NaN de Cramer para numericas
df_resumo['CramersV'] = df_resumo['CramersV'].fillna(0)

# Coluna de "Força Maxima" (pegar o maior valor absoluto entre os metodos lineares + Cramer)
df_resumo['Forca_Max'] = df_resumo[['Pearson', 'Spearman', 'PointBiserial', 'CramersV']].abs().max(axis=1)
df_resumo = df_resumo.sort_values(['Forca_Max', 'MI_Score'], ascending=[False, False]).reset_index(drop=True)

# Veredito
def veredito(forca):
    if forca >= 0.10:
        return 'FORTE'
    elif forca >= 0.05:
        return 'MODERADA'
    else:
        return 'FRACA'

df_resumo['Veredito'] = df_resumo['Forca_Max'].apply(veredito)

print("=" * 125)
print(f"{'#':3s} {'Feature':35s} {'Pearson':>8s} {'Spearman':>9s} {'PtBiser':>8s} {'CramerV':>8s} {'MI_Score':>8s} {'Forca':>7s} {'Veredito':>10s}")
print("=" * 125)
for i, row in df_resumo.iterrows():
    pearson_str = f"{row['Pearson']:+.4f}" if pd.notna(row['Pearson']) else "   —"
    spearman_str = f"{row['Spearman']:+.4f}" if pd.notna(row['Spearman']) else "   —"
    pb_str = f"{row['PointBiserial']:+.4f}" if pd.notna(row['PointBiserial']) else "   —"
    cv_str = f"{row['CramersV']:.4f}" if row['CramersV'] > 0 else "   —"
    mi_str = f"{row['MI_Score']:.4f}" if pd.notna(row['MI_Score']) else "   —"
    print(f"  {i+1:2d} {row['Feature']:35s} {pearson_str:>8s} {spearman_str:>9s} {pb_str:>8s} {cv_str:>8s} {mi_str:>8s} {row['Forca_Max']:>7.4f} {row['Veredito']:>10s}")
print("=" * 125)

# Exportar tabela
df_resumo.to_csv(os.path.join(NOTEBOOKS_DIR, 'tabela_resumo_correlacoes.csv'), index=False, encoding='utf-8-sig')
print(f"\nTabela exportada para: tabela_resumo_correlacoes.csv")

# %% [markdown]
# ---
# ## Seção 11 — Análise Temporal — Quando os Atrasos Acontecem?
# O professor pediu para correlacionar com DATAS e PERÍODOS.
# Vamos analisar: meses, trimestres, séries temporais e períodos críticos.

# %%
banner(11, "ANALISE TEMPORAL — PERIODOS DE ATRASO")

# 11.1 — Criar variáveis temporais auxiliares
df['ano_mes'] = df['order_purchase_timestamp'].dt.to_period('M').astype(str)
df['trimestre'] = df['order_purchase_timestamp'].dt.quarter
df['ano'] = df['order_purchase_timestamp'].dt.year
df['ano_trimestre'] = df['ano'].astype(str) + '-Q' + df['trimestre'].astype(str)

# Criar dias_atraso contínuo (para análise descritiva mais rica)
df['dias_atraso'] = df['dias_diferenca'].clip(lower=0)

print("=== VARIAVEIS TEMPORAIS CRIADAS ===")
print(f"  Periodo do dataset: {df['order_purchase_timestamp'].min().strftime('%Y-%m-%d')} a {df['order_purchase_timestamp'].max().strftime('%Y-%m-%d')}")
print(f"  Meses unicos: {df['ano_mes'].nunique()}")
print(f"  Trimestres unicos: {df['ano_trimestre'].nunique()}")

# %%
# 11.2 — Taxa de Atraso por MÊS DO ANO (sazonalidade)
meses_nomes = {1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun',
               7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'}

atraso_mes = df.groupby('mes_compra').agg(
    total_pedidos=('order_id', 'count'),
    taxa_atraso=('foi_atraso', 'mean'),
    media_dias_atraso=('dias_atraso', 'mean')
).reset_index()
atraso_mes['mes_nome'] = atraso_mes['mes_compra'].map(meses_nomes)

print("\n=== TAXA DE ATRASO POR MES DO ANO ===")
print(f"{'Mes':>6s} {'Pedidos':>10s} {'Taxa Atraso':>12s} {'Media Dias':>12s}")
print("-" * 42)
for _, r in atraso_mes.iterrows():
    print(f"  {r['mes_nome']:>4s} {r['total_pedidos']:>10,} {r['taxa_atraso']:>12.2%} {r['media_dias_atraso']:>12.1f}")

fig_mes = px.bar(
    atraso_mes, x='mes_nome', y='taxa_atraso',
    title='Taxa de Atraso por Mês do Ano (Sazonalidade)',
    text=atraso_mes['taxa_atraso'].apply(lambda x: f'{x:.1%}'),
    labels={'mes_nome': 'Mês', 'taxa_atraso': 'Taxa de Atraso'},
    color='taxa_atraso', color_continuous_scale='YlOrRd'
)
fig_mes.update_traces(textposition='outside')
fig_mes.update_layout(
    height=450, 
    xaxis={'categoryorder': 'array', 'categoryarray': list(meses_nomes.values())},
    margin=dict(t=50, b=50, l=50, r=20)
)
fig_mes.show()

# %%
# 11.3 — Taxa de Atraso por TRIMESTRE (visão macro)
atraso_tri = df.groupby('trimestre').agg(
    total_pedidos=('order_id', 'count'),
    taxa_atraso=('foi_atraso', 'mean'),
    media_dias_atraso=('dias_atraso', 'mean')
).reset_index()
atraso_tri['trimestre_nome'] = atraso_tri['trimestre'].apply(lambda x: f'Q{x}')

print("\n=== TAXA DE ATRASO POR TRIMESTRE ===")
for _, r in atraso_tri.iterrows():
    print(f"  Q{int(r['trimestre'])}: {r['taxa_atraso']:.2%} ({r['total_pedidos']:,} pedidos) | Media: {r['media_dias_atraso']:.1f} dias de atraso")

fig_tri = px.bar(
    atraso_tri, x='trimestre_nome', y='taxa_atraso',
    title='Taxa de Atraso por Trimestre',
    text=atraso_tri['taxa_atraso'].apply(lambda x: f'{x:.1%}'),
    labels={'trimestre_nome': 'Trimestre', 'taxa_atraso': 'Taxa de Atraso'},
    color='taxa_atraso', color_continuous_scale='YlOrRd'
)
fig_tri.update_traces(textposition='outside')
fig_tri.update_layout(
    height=450,
    margin=dict(t=50, b=50, l=50, r=20)
)
fig_tri.show()

# %%
# 11.4 — SÉRIE TEMPORAL: evolução mês-a-mês ao longo do dataset (2016–2018)
serie_mensal = df.groupby('ano_mes').agg(
    total_pedidos=('order_id', 'count'),
    taxa_atraso=('foi_atraso', 'mean'),
    media_dias_atraso=('dias_atraso', 'mean')
).reset_index().sort_values('ano_mes')

# Filtrar meses com poucos pedidos (início e fim do dataset)
serie_mensal = serie_mensal[serie_mensal['total_pedidos'] >= 100]

print("\n=== SERIE TEMPORAL MENSAL (taxa de atraso) ===")
for _, r in serie_mensal.iterrows():
    barra = "█" * int(r['taxa_atraso'] * 100)
    print(f"  {r['ano_mes']}  {r['taxa_atraso']:.1%} {barra}  ({r['total_pedidos']:,} ped.)")

fig_serie = go.Figure()
fig_serie.add_trace(go.Scatter(
    x=serie_mensal['ano_mes'], y=serie_mensal['taxa_atraso'],
    mode='lines+markers', name='Taxa de Atraso',
    line=dict(color='#e74c3c', width=2.5),
    marker=dict(size=7)
))
fig_serie.add_trace(go.Bar(
    x=serie_mensal['ano_mes'], y=serie_mensal['total_pedidos'],
    name='Volume de Pedidos', yaxis='y2',
    marker=dict(color='#3498db', opacity=0.3)
))
fig_serie.update_layout(
    title='Série Temporal: Taxa de Atraso + Volume de Pedidos (mês a mês)',
    xaxis_title='Mês',
    yaxis=dict(title='Taxa de Atraso', tickformat='.0%', side='left'),
    yaxis2=dict(title='Volume de Pedidos', overlaying='y', side='right'),
    height=550, width=1000,
    legend=dict(
        x=0.01, y=0.99,
        bgcolor='rgba(255,255,255,0.8)'
    ),
    xaxis=dict(tickangle=-45),
    margin=dict(t=50, b=80, l=50, r=50)
)
fig_serie.show()

# %%
# 11.5 — Períodos CRÍTICOS: Black Friday, Natal, Carnaval
print("\n=== PERIODOS CRITICOS (PICOS DE ATRASO) ===")

periodos = {
    'Black Friday 2017 (Nov 24)':   ('2017-11-20', '2017-11-30'),
    'Natal 2017 (Dez)':             ('2017-12-01', '2017-12-31'),
    'Pre-Carnaval 2018 (Fev)':      ('2018-02-01', '2018-02-28'),
    'Black Friday 2018 (Nov 23)':   ('2018-11-19', '2018-11-30'),
    'Media Geral':                  (None, None),
}

print(f"{'Periodo':35s} {'Pedidos':>10s} {'Taxa Atraso':>12s} {'Media Dias':>12s}")
print("-" * 72)
for nome, (inicio, fim) in periodos.items():
    if inicio is None:
        subset = df
    else:
        mask = (df['order_purchase_timestamp'] >= inicio) & (df['order_purchase_timestamp'] <= fim)
        subset = df[mask]
    
    if len(subset) > 0:
        taxa = subset['foi_atraso'].mean()
        dias_m = subset['dias_atraso'].mean()
        print(f"  {nome:33s} {len(subset):>10,} {taxa:>12.2%} {dias_m:>12.1f}")

# %%
# 11.6 — Dia da Semana + Hora da Compra
df['hora_compra'] = df['order_purchase_timestamp'].dt.hour

atraso_hora = df.groupby('hora_compra').agg(
    total=('order_id', 'count'),
    taxa_atraso=('foi_atraso', 'mean')
).reset_index()

fig_hora = px.bar(
    atraso_hora, x='hora_compra', y='taxa_atraso',
    title='Taxa de Atraso por Hora do Dia da Compra',
    text=atraso_hora['taxa_atraso'].apply(lambda x: f'{x:.1%}'),
    labels={'hora_compra': 'Hora do Dia (0-23h)', 'taxa_atraso': 'Taxa de Atraso'},
    color='taxa_atraso', color_continuous_scale='YlOrRd'
)
fig_hora.update_traces(textposition='outside', textfont_size=9)
fig_hora.update_layout(height=400)
fig_hora.show()

dias_nome = {0:'Seg', 1:'Ter', 2:'Qua', 3:'Qui', 4:'Sex', 5:'Sab', 6:'Dom'}
atraso_dia = df.groupby('dia_semana_compra').agg(
    total=('order_id', 'count'),
    taxa_atraso=('foi_atraso', 'mean'),
    media_dias=('dias_atraso', 'mean')
).reset_index()
atraso_dia['dia_nome'] = atraso_dia['dia_semana_compra'].map(dias_nome)

print("\n=== TAXA DE ATRASO POR DIA DA SEMANA ===")
for _, r in atraso_dia.iterrows():
    print(f"  {r['dia_nome']}: {r['taxa_atraso']:.2%} ({r['total']:,} pedidos)")

fig_dia = px.bar(
    atraso_dia, x='dia_nome', y='taxa_atraso',
    title='Taxa de Atraso por Dia da Semana',
    text=atraso_dia['taxa_atraso'].apply(lambda x: f'{x:.1%}'),
    labels={'dia_nome': 'Dia da Semana', 'taxa_atraso': 'Taxa de Atraso'},
    color='taxa_atraso', color_continuous_scale='YlOrRd'
)
fig_dia.update_traces(textposition='outside')
fig_dia.update_layout(
    height=450, 
    xaxis={'categoryorder': 'array', 'categoryarray': list(dias_nome.values())},
    margin=dict(t=50, b=50, l=50, r=20)
)
fig_dia.show()

# %% [markdown]
# ---
# ## Seção 12 — Distribuição de Dias de Atraso (Gravidade)
# Quantos dias de atraso os pedidos costumam ter? Filtrando os pedidos
# que *chegaram no prazo* e removendo outliers severos (ex: > 95º percentil).

# %%
banner(12, "DISTRIBUICAO DE DIAS DE ATRASO (GRAVIDADE)")

# Filtrar apenas quem atrasou (> 0 dias)
df_atrasados = df[df['dias_diferenca'] > 0].copy()

# Remover outliers extremos (acima do percentil 95%) para visualizacao limpa
limite_95 = df_atrasados['dias_diferenca'].quantile(0.95)
df_atrasados_clean = df_atrasados[df_atrasados['dias_diferenca'] <= limite_95]

print("=== GRAVIDADE DOS ATRASOS ===")
print(f"Total de pedidos atrasados: {len(df_atrasados):,}")
print(f"Atraso medio real (apenas atrasados): {df_atrasados['dias_diferenca'].mean():.1f} dias")
print(f"Limpando o grafico no P95 (<= {limite_95:.0f} dias) para remover outliers.")

# Agrupar por quantidade exata de dias
dist_dias = df_atrasados_clean.groupby('dias_diferenca').size().reset_index(name='qtd_pedidos')

fig_dist = px.bar(
    dist_dias, x='dias_diferenca', y='qtd_pedidos',
    title=f'Histograma: Quantos dias os pedidos costumam atrasar? (Truncado em {limite_95:.0f} dias)',
    labels={'dias_diferenca': 'Dias Atrasados', 'qtd_pedidos': 'Volume de Pedidos'},
    text='qtd_pedidos',
    color='qtd_pedidos', color_continuous_scale='Reds'
)
fig_dist.update_traces(textposition='outside')
fig_dist.update_layout(
    height=500, width=900,
    xaxis=dict(tickmode='linear', dtick=1),
    margin=dict(t=50, b=50, l=50, r=20)
)
fig_dist.show()

# %% [markdown]
# ---
# ## Seção 13 — Capital vs Interior & Tipo de Pagamento
# Explorando os atrasos com base na localidade específica do cliente e meio de pagamento.

# %%
banner(13, "CAPITAL VS INTERIOR & TIPO DE PAGAMENTO")

# 13.1 — Capital vs Interior
atraso_destino = df.groupby('destino_tipo').agg(
    total=('order_id', 'count'),
    taxa_atraso=('foi_atraso', 'mean')
).reset_index()

print("=== TAXA DE ATRASO: CAPITAL VS INTERIOR ===")
for _, r in atraso_destino.iterrows():
    print(f"  {r['destino_tipo']:10s}: {r['taxa_atraso']:.2%} ({r['total']:,} pedidos)")

fig_dest = px.bar(
    atraso_destino, x='destino_tipo', y='taxa_atraso',
    title='Taxa de Atraso: Capital vs Interior',
    text=atraso_destino['taxa_atraso'].apply(lambda x: f'{x:.1%}'),
    labels={'destino_tipo': 'Localização da Entrega', 'taxa_atraso': 'Taxa de Atraso'},
    color='destino_tipo', color_discrete_map={'Capital': '#2ecc71', 'Interior': '#f1c40f'}
)
fig_dest.update_traces(textposition='outside')
fig_dest.update_layout(height=400, margin=dict(t=50, b=50, l=50, r=20))
fig_dest.show()

# 13.2 — Tipo de Pagamento Principal (Agrupado)
# Desconsiderando pagamentos "not_defined" e "desconhecido" (ruído estatístico)
df_pag = df[~df['tipo_pagamento_principal'].isin(['not_defined', 'desconhecido'])].copy()

# Agrupar as categorias para facilitar a análise de negócios
mapa_pagamentos = {
    'credit_card': 'Cartão',
    'debit_card': 'Cartão',
    'boleto': 'Boleto',
    'voucher': 'Outros'
}
df_pag['categoria_pagamento'] = df_pag['tipo_pagamento_principal'].map(mapa_pagamentos)

atraso_pagamento = df_pag.groupby('categoria_pagamento').agg(
    total=('order_id', 'count'),
    taxa_atraso=('foi_atraso', 'mean')
).reset_index().sort_values('taxa_atraso', ascending=False)

print("\n=== TAXA DE ATRASO: TIPO DE PAGAMENTO (AGRUPADO) ===")
for _, r in atraso_pagamento.iterrows():
    print(f"  {r['categoria_pagamento']:15s}: {r['taxa_atraso']:.2%} ({r['total']:,} pedidos)")

fig_pag = px.bar(
    atraso_pagamento, x='categoria_pagamento', y='taxa_atraso',
    title='Taxa de Atraso: Cartão vs Boleto vs Outros',
    text=atraso_pagamento['taxa_atraso'].apply(lambda x: f'{x:.1%}'),
    labels={'categoria_pagamento': 'Método de Pagamento (Agrupado)', 'taxa_atraso': 'Taxa de Atraso'},
    color='categoria_pagamento', color_discrete_map={'Cartão': '#3498db', 'Boleto': '#e67e22', 'Outros': '#9b59b6'}
)
fig_pag.update_traces(textposition='outside')
fig_pag.update_layout(height=450, margin=dict(t=50, b=50, l=50, r=20))
fig_pag.show()

# %% [markdown]
# ---
# ## Seção 14 — Resumo Final e Exportação

# %%
banner(14, "RESUMO FINAL E EXPORTACAO")

# Exportar CSV unificado (atualizado com as novas colunas temporais e de pgto)
output_path = os.path.join(NOTEBOOKS_DIR, 'dataset_unificado_v1.csv')
df.to_csv(output_path, index=False)
print(f"Dataset salvo em: {output_path}")
print(f"Tamanho: {len(df):,} linhas x {len(df.columns)} colunas")

print("\n" + "=" * 60)
print("   PIPELINE EDA COMPLETO!")
print("=" * 60)
print(f"  Dataset: {output_path}")
print(f"  Graficos Gerados Localmente: Pearson, Heatmaps, Piores Categories, Rotas, Spearman, Mutual Info, Cramer, Forest Plot, Temporal.")
print(f"  Tabela CSV: tabela_resumo_correlacoes.csv")
print("=" * 60)

