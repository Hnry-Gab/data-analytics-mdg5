# %% [markdown]
# # 📊 EDA Nichado — Correlação de Atributos com `foi_atraso`
#
# **Projeto:** Olist Logistics Growth — Previsão de Atrasos Logísticos
#
# **Objetivo deste notebook:**
# Descobrir quais atributos (variáveis) do dataset Olist possuem **relação estatística**
# com a ocorrência de atrasos na entrega. O resultado final é uma **tabela-resumo rankeada**
# que servirá de base para a seleção de features do modelo XGBoost.
#
# **O que NÃO faremos aqui:**
# - Treinar modelos (isso é tarefa do ALPHA-07/08/09)
# - Filtrar features finais (será feito no treino, limitando a ~6 melhores)
# - Tratar outliers ou fazer encoding (será feito no notebook de Feature Engineering)
#
# **Cards do Linear cobertos:** ALPHA-01, ALPHA-02, ALPHA-03
#
# ---

# %% [markdown]
# ## 1. Importação de Bibliotecas
#
# Usamos apenas as bibliotecas definidas na stack oficial do projeto (`spec/stack.md`).

# %%
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import pointbiserialr, chi2_contingency
import warnings
warnings.filterwarnings('ignore')

# Configuração visual
pd.set_option('display.max_columns', 50)
pd.set_option('display.float_format', '{:.4f}'.format)

print("✅ Bibliotecas importadas com sucesso")

# %% [markdown]
# ## 2. Carregamento das Tabelas CSV
#
# O dataset da Olist é composto por múltiplas tabelas relacionais.
# Para nossa análise de atrasos logísticos, precisamos de **6 tabelas** que, quando
# unidas (merge/JOIN), formam um DataFrame completo com informações de:
# - **Pedido** (datas, status)
# - **Cliente** (estado, CEP)
# - **Produto** (peso, dimensões, categoria)
# - **Vendedor** (estado, CEP)
# - **Item do Pedido** (preço, frete)
#
# > 📁 Todos os CSVs estão no diretório `dataset/`

# %%
DATA_DIR = '../dataset'

# Tabelas principais
df_orders    = pd.read_csv(f'{DATA_DIR}/olist_orders_dataset.csv')
df_items     = pd.read_csv(f'{DATA_DIR}/olist_order_items_dataset.csv')
df_products  = pd.read_csv(f'{DATA_DIR}/olist_products_dataset.csv')
df_customers = pd.read_csv(f'{DATA_DIR}/olist_customers_dataset.csv')
df_sellers   = pd.read_csv(f'{DATA_DIR}/olist_sellers_dataset.csv')
df_geo       = pd.read_csv(f'{DATA_DIR}/olist_geolocation_dataset.csv')

print(f"📦 orders:    {df_orders.shape[0]:,} linhas x {df_orders.shape[1]} colunas")
print(f"📦 items:     {df_items.shape[0]:,} linhas x {df_items.shape[1]} colunas")
print(f"📦 products:  {df_products.shape[0]:,} linhas x {df_products.shape[1]} colunas")
print(f"📦 customers: {df_customers.shape[0]:,} linhas x {df_customers.shape[1]} colunas")
print(f"📦 sellers:   {df_sellers.shape[0]:,} linhas x {df_sellers.shape[1]} colunas")
print(f"📦 geoloc:    {df_geo.shape[0]:,} linhas x {df_geo.shape[1]} colunas")

# %% [markdown]
# ## 3. Filtro de Segurança e Merge das Tabelas
#
# ### Por que filtramos?
# Só nos interessam pedidos que **realmente chegaram ao destino** (`delivered`),
# porque precisamos comparar a data real de entrega com a data estimada.
# Pedidos cancelados, em trânsito ou extraviados não servem para calcular atraso.
#
# ### Sequência dos JOINs
# ```
# orders (base)
#   → customers  (via customer_id)
#   → items      (via order_id)
#     → products  (via product_id)
#     → sellers   (via seller_id)
# ```

# %%
# --- FILTRO DE SEGURANÇA ---
# Manter apenas pedidos entregues e com data de entrega real preenchida
df_orders = df_orders[df_orders['order_status'] == 'delivered'].copy()
df_orders = df_orders.dropna(subset=['order_delivered_customer_date'])

print(f"✅ Pedidos após filtro (delivered + data preenchida): {len(df_orders):,}")

# --- CONVERSÃO DE DATAS ---
# Convertemos todas as colunas de data para o tipo datetime do pandas,
# permitindo cálculos como diferença de dias e extração do dia da semana.
date_cols = [
    'order_purchase_timestamp',
    'order_approved_at',
    'order_delivered_carrier_date',
    'order_delivered_customer_date',
    'order_estimated_delivery_date'
]
for col in date_cols:
    df_orders[col] = pd.to_datetime(df_orders[col])

# --- MERGE SEQUENCIAL ---
# 1. Orders + Customers (traz estado e CEP do cliente)
df = df_orders.merge(df_customers, on='customer_id', how='left')

# 2. + Items (traz preço, frete, product_id, seller_id)
df = df.merge(df_items, on='order_id', how='left')

# 3. + Products (traz peso, dimensões, categoria do produto)
df = df.merge(df_products, on='product_id', how='left')

# 4. + Sellers (traz estado e CEP do vendedor)
df = df.merge(df_sellers, on='seller_id', how='left')

print(f"✅ DataFrame unificado: {df.shape[0]:,} linhas x {df.shape[1]} colunas")
print(f"\n📋 Colunas disponíveis:\n{list(df.columns)}")

# %% [markdown]
# ## 4. Criação da Variável Alvo (`foi_atraso`)
#
# ### O que é a variável alvo?
# É a coluna que o modelo de Machine Learning vai **aprender a prever**.
# No nosso caso, queremos prever se um pedido vai atrasar ou não.
#
# ### Como calculamos?
# Comparamos duas datas:
# - `order_delivered_customer_date`: quando o pacote **realmente** chegou
# - `order_estimated_delivery_date`: quando a Olist **prometeu** que chegaria
#
# Se a entrega real foi **depois** da prometida → **Atrasou** (1)
# Se a entrega real foi **antes ou no dia** → **No prazo** (0)
#
# > ⚠️ **ALERTA DE DATA LEAKAGE:** A coluna `order_delivered_customer_date` é usada
# > APENAS para criar o target. Ela **NUNCA** será feature do modelo, pois é uma
# > informação do futuro (você só sabe quando o pacote chegou DEPOIS que ele chegou).

# %%
# Cálculo da diferença em dias (auxiliar para análise, NÃO será feature)
df['dias_diferenca'] = (
    df['order_delivered_customer_date'] - df['order_estimated_delivery_date']
).dt.days

# Variável alvo binária
df['foi_atraso'] = (df['dias_diferenca'] > 0).astype(int)

# --- Validação da distribuição ---
dist = df['foi_atraso'].value_counts(normalize=True)
total = df['foi_atraso'].value_counts()

print("=" * 50)
print("📊 DISTRIBUIÇÃO DA VARIÁVEL ALVO")
print("=" * 50)
print(f"  No prazo (0): {total[0]:,} pedidos ({dist[0]:.2%})")
print(f"  Atrasou  (1): {total[1]:,} pedidos ({dist[1]:.2%})")
print("=" * 50)
print(f"\n⚠️ Dataset DESBALANCEADO: a classe minoritária (atraso)")
print(f"   representa apenas {dist[1]:.2%} dos dados.")
print(f"   Isso significa que a ACURÁCIA não serve como métrica")
print(f"   de avaliação (um modelo 'burro' teria {dist[0]:.0%} de acurácia")
print(f"   chutando sempre 'no prazo').")

# %% [markdown]
# ### Visualização: Proporção de Atrasos
#
# Este gráfico é importante para a apresentação final porque mostra
# ao público o **tamanho do problema** que estamos resolvendo.

# %%
fig_target = px.pie(
    names=['No prazo', 'Atrasou'],
    values=[total[0], total[1]],
    color_discrete_sequence=['#2ecc71', '#e74c3c'],
    title='Distribuição da Variável Alvo: foi_atraso',
    hole=0.4
)
fig_target.update_traces(textinfo='label+percent+value', textfont_size=14)
fig_target.update_layout(font=dict(size=14), width=600, height=400)
fig_target.show()

# %% [markdown]
# ## 5. Criação de Features Derivadas (Feature Engineering)
#
# As tabelas originais da Olist fornecem dados brutos. Mas o XGBoost
# aprende melhor quando criamos **variáveis derivadas** que capturam
# relações mais complexas. Abaixo criamos cada uma com sua justificativa.
#
# > 📖 Referência completa: `docs/data/atributos_modelo.md`

# %%
# --- 5.1 Volume Cúbico (cm³) ---
# Hipótese: Pacotes maiores são mais difíceis de alocar nos caminhões,
# gerando gargalos logísticos e potenciais atrasos.
df['volume_cm3'] = (
    df['product_length_cm'] *
    df['product_height_cm'] *
    df['product_width_cm']
)

# --- 5.2 Frete/Preço Ratio ---
# Hipótese: Quando o frete é proporcionalmente muito alto em relação
# ao preço do produto, pode indicar rotas difíceis ou produtos pesados.
# Ex: caneta de R$2 com frete de R$40 = ratio 20x (rota crítica).
df['frete_ratio'] = df['freight_value'] / df['price'].replace(0, np.nan)

# --- 5.3 Velocidade do Lojista (Lead Time Interno) ---
# Hipótese: Quanto mais tempo o vendedor demora para despachar o pacote
# (da aprovação do pedido até entregar à transportadora), maior a chance
# de estourar o prazo final.
df['velocidade_lojista_dias'] = (
    df['order_delivered_carrier_date'] - df['order_approved_at']
).dt.total_seconds() / 86400  # converter para dias (com decimais)

# --- 5.4 Dia da Semana da Compra ---
# Hipótese: Pedidos feitos na sexta-feira à noite ou no sábado podem
# ficar parados nos pátios durante o fim de semana, acumulando atraso.
df['dia_semana_compra'] = df['order_purchase_timestamp'].dt.dayofweek
# 0=Segunda, 1=Terça, ..., 4=Sexta, 5=Sábado, 6=Domingo

# --- 5.5 Rota Interestadual ---
# Hipótese: Pacotes que cruzam fronteiras estaduais enfrentam blitz
# fiscais, trocas de transportadora e distâncias maiores.
df['rota_interestadual'] = (
    df['seller_state'] != df['customer_state']
).astype(int)

# --- 5.6 Distância Haversine (km) ---
# Hipótese: Quanto maior a distância em linha reta entre vendedor e
# cliente, maior a chance de atraso (mais pontos de falha na rota).
# Para isso, precisamos das coordenadas de geolocalização.

# Preparar geolocation: pegar a mediana de lat/lng por CEP (a tabela
# tem múltiplas coordenadas por CEP, usamos a mediana para estabilidade)
geo_median = df_geo.groupby('geolocation_zip_code_prefix').agg(
    lat=('geolocation_lat', 'median'),
    lng=('geolocation_lng', 'median')
).reset_index()

# Merge das coordenadas do CLIENTE (pelo CEP do cliente)
df = df.merge(
    geo_median.rename(columns={
        'geolocation_zip_code_prefix': 'customer_zip_code_prefix',
        'lat': 'customer_lat',
        'lng': 'customer_lng'
    }),
    on='customer_zip_code_prefix',
    how='left'
)

# Merge das coordenadas do VENDEDOR (pelo CEP do vendedor)
df = df.merge(
    geo_median.rename(columns={
        'geolocation_zip_code_prefix': 'seller_zip_code_prefix',
        'lat': 'seller_lat',
        'lng': 'seller_lng'
    }),
    on='seller_zip_code_prefix',
    how='left'
)

# Cálculo da distância Haversine
def haversine_km(lat1, lon1, lat2, lon2):
    """
    Calcula a distância em km entre dois pontos geográficos usando
    a fórmula de Haversine (distância em linha reta sobre a esfera terrestre).
    """
    R = 6371  # Raio da Terra em km
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

df['distancia_haversine_km'] = haversine_km(
    df['seller_lat'], df['seller_lng'],
    df['customer_lat'], df['customer_lng']
)

print("✅ Features derivadas criadas com sucesso:")
print(f"   • volume_cm3:             {df['volume_cm3'].notna().sum():,} valores válidos")
print(f"   • frete_ratio:            {df['frete_ratio'].notna().sum():,} valores válidos")
print(f"   • velocidade_lojista_dias:{df['velocidade_lojista_dias'].notna().sum():,} valores válidos")
print(f"   • dia_semana_compra:      {df['dia_semana_compra'].notna().sum():,} valores válidos")
print(f"   • rota_interestadual:     {df['rota_interestadual'].notna().sum():,} valores válidos")
print(f"   • distancia_haversine_km: {df['distancia_haversine_km'].notna().sum():,} valores válidos")

# %% [markdown]
# ## 6. Correlação de Pearson — Features Numéricas vs `foi_atraso`
#
# ### O que é correlação de Pearson?
# É uma medida estatística que varia de **-1 a +1** e indica a **força
# e direção** de uma relação linear entre duas variáveis numéricas:
#
# | Valor | Interpretação |
# |:--|:--|
# | +1.0 | Correlação positiva perfeita (uma sobe, a outra sobe junto) |
# | +0.3 a +0.7 | Correlação positiva moderada |
# | +0.1 a +0.3 | Correlação positiva fraca |
# | 0.0 | Nenhuma correlação linear |
# | -0.1 a -0.3 | Correlação negativa fraca |
# | -0.3 a -0.7 | Correlação negativa moderada |
# | -1.0 | Correlação negativa perfeita (uma sobe, a outra desce) |
#
# ### Limitação importante
# Pearson mede apenas relações **lineares**. Se uma variável tem uma relação
# curva (ex: "U invertido") com o atraso, Pearson pode dar ~0 mesmo havendo
# relação forte. Por isso, combinaremos Pearson com **feeling técnico**.
#
# ### Por que funciona com `foi_atraso` (0/1)?
# Quando a variável alvo é binária (0 ou 1), a correlação de Pearson é
# matematicamente equivalente ao **Point-Biserial**, que é a versão
# específica para correlação entre uma contínua e uma binária.

# %%
# Lista de features numéricas candidatas
features_numericas = [
    'price',
    'freight_value',
    'product_weight_g',
    'volume_cm3',
    'frete_ratio',
    'velocidade_lojista_dias',
    'dia_semana_compra',
    'distancia_haversine_km'
]

# Calcular correlação de Pearson + p-valor (Point-Biserial)
resultados_pearson = []
for feat in features_numericas:
    serie = df[[feat, 'foi_atraso']].dropna()
    if len(serie) > 100:
        corr, pvalue = pointbiserialr(serie['foi_atraso'], serie[feat])
        resultados_pearson.append({
            'Feature': feat,
            'Correlação (Pearson)': round(corr, 4),
            'p-valor': f'{pvalue:.2e}',
            'Significativo?': '✅ Sim' if pvalue < 0.05 else '❌ Não',
            'N válido': len(serie)
        })

df_pearson = pd.DataFrame(resultados_pearson)
df_pearson = df_pearson.sort_values('Correlação (Pearson)', key=abs, ascending=False)
df_pearson = df_pearson.reset_index(drop=True)

print("=" * 80)
print("📊 CORRELAÇÃO DE PEARSON (POINT-BISERIAL) vs foi_atraso")
print("=" * 80)
print(df_pearson.to_string(index=False))

# %% [markdown]
# ### Visualização: Ranking de Correlações
#
# O gráfico abaixo mostra, de forma visual, quais features têm a correlação
# mais forte (positiva ou negativa) com atrasos. Barras para a **direita**
# indicam que valores maiores daquela feature estão **associados a mais
# atrasos**. Barras para a **esquerda** indicam o oposto.

# %%
fig_pearson = px.bar(
    df_pearson.sort_values('Correlação (Pearson)'),
    x='Correlação (Pearson)',
    y='Feature',
    orientation='h',
    title='Ranking: Correlação de Pearson vs foi_atraso',
    color='Correlação (Pearson)',
    color_continuous_scale='RdYlGn_r',
    text='Correlação (Pearson)'
)
fig_pearson.update_traces(textposition='outside', texttemplate='%{text:.4f}')
fig_pearson.update_layout(
    font=dict(size=13),
    width=900, height=500,
    yaxis=dict(autorange='reversed')
)
fig_pearson.show()

# %% [markdown]
# ## 7. Análise de Features Categóricas vs `foi_atraso`
#
# Features categóricas (texto/categorias) não podem ser medidas com Pearson.
# Usamos duas técnicas complementares:
#
# 1. **Taxa de atraso por categoria**: Simples e intuitiva. Calculamos a % de
#    atrasos dentro de cada grupo (ex: "moveis_decoracao" tem 15% de atraso vs
#    média de 7%).
#
# 2. **Cramér's V**: Medida estatística que vai de 0 a 1 e indica a **força
#    da associação** entre duas variáveis categóricas. Quanto mais próximo de 1,
#    maior a relação.
#
# > **Nota para apresentação:** Cramér's V não indica direção (positiva/negativa),
# > apenas a força da associação.

# %%
features_categoricas = ['customer_state', 'seller_state', 'product_category_name']

# --- Cramér's V ---
def cramers_v(x, y):
    """
    Calcula o coeficiente V de Cramér entre duas variáveis categóricas.
    Retorna um valor entre 0 (nenhuma associação) e 1 (associação perfeita).
    """
    confusion_matrix = pd.crosstab(x, y)
    chi2 = chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    phi2 = chi2 / n
    r, k = confusion_matrix.shape
    phi2corr = max(0, phi2 - ((k-1)*(r-1))/(n-1))
    rcorr = r - ((r-1)**2)/(n-1)
    kcorr = k - ((k-1)**2)/(n-1)
    return np.sqrt(phi2corr / min((kcorr-1), (rcorr-1))) if min(kcorr, rcorr) > 1 else 0

resultados_categoricas = []
for feat in features_categoricas:
    serie = df[[feat, 'foi_atraso']].dropna()
    cv = cramers_v(serie[feat], serie['foi_atraso'])
    n_categorias = serie[feat].nunique()
    resultados_categoricas.append({
        'Feature': feat,
        "Cramér's V": round(cv, 4),
        'Nº Categorias': n_categorias,
        'N válido': len(serie)
    })

df_cramer = pd.DataFrame(resultados_categoricas)
df_cramer = df_cramer.sort_values("Cramér's V", ascending=False).reset_index(drop=True)

print("=" * 70)
print("📊 CRAMÉR'S V — ASSOCIAÇÃO DAS CATEGÓRICAS vs foi_atraso")
print("=" * 70)
print(df_cramer.to_string(index=False))

# %% [markdown]
# ### Taxa de Atraso por Estado do Vendedor
#
# Este gráfico revela **de onde saem os pacotes que mais atrasam**.
# É um insight direto para o time de Supply Chain da Olist.

# %%
# Taxa de atraso por seller_state
taxa_seller = df.groupby('seller_state')['foi_atraso'].agg(['mean', 'count']).reset_index()
taxa_seller.columns = ['Estado Vendedor', 'Taxa Atraso', 'Total Pedidos']
taxa_seller = taxa_seller[taxa_seller['Total Pedidos'] >= 50]  # filtrar estados com poucos dados
taxa_seller = taxa_seller.sort_values('Taxa Atraso', ascending=False)

fig_seller = px.bar(
    taxa_seller,
    x='Estado Vendedor',
    y='Taxa Atraso',
    title='Taxa de Atraso por Estado do Vendedor (mínimo 50 pedidos)',
    color='Taxa Atraso',
    color_continuous_scale='YlOrRd',
    text=taxa_seller['Taxa Atraso'].apply(lambda x: f'{x:.1%}')
)
fig_seller.update_traces(textposition='outside')
fig_seller.update_layout(
    font=dict(size=13), width=900, height=500,
    yaxis_tickformat='.0%',
    xaxis=dict(categoryorder='total descending')
)
fig_seller.show()

# %% [markdown]
# ### Taxa de Atraso por Estado do Cliente
#
# Este gráfico mostra **para onde vão os pacotes que mais atrasam**.
# Combinado com o gráfico anterior, revela as **rotas mais problemáticas**.

# %%
taxa_customer = df.groupby('customer_state')['foi_atraso'].agg(['mean', 'count']).reset_index()
taxa_customer.columns = ['Estado Cliente', 'Taxa Atraso', 'Total Pedidos']
taxa_customer = taxa_customer[taxa_customer['Total Pedidos'] >= 50]
taxa_customer = taxa_customer.sort_values('Taxa Atraso', ascending=False)

fig_customer = px.bar(
    taxa_customer,
    x='Estado Cliente',
    y='Taxa Atraso',
    title='Taxa de Atraso por Estado do Cliente (mínimo 50 pedidos)',
    color='Taxa Atraso',
    color_continuous_scale='YlOrRd',
    text=taxa_customer['Taxa Atraso'].apply(lambda x: f'{x:.1%}')
)
fig_customer.update_traces(textposition='outside')
fig_customer.update_layout(
    font=dict(size=13), width=900, height=500,
    yaxis_tickformat='.0%',
    xaxis=dict(categoryorder='total descending')
)
fig_customer.show()

# %% [markdown]
# ### Taxa de Atraso por Rota (Intraestadual vs Interestadual)
#
# Uma das hipóteses mais fortes do projeto: pedidos que **cruzam
# fronteiras estaduais** enfrentam mais gargalos (blitz fiscal,
# troca de transportadora, distância).

# %%
taxa_rota = df.groupby('rota_interestadual')['foi_atraso'].agg(['mean', 'count']).reset_index()
taxa_rota.columns = ['Tipo Rota', 'Taxa Atraso', 'Total']
taxa_rota['Tipo Rota'] = taxa_rota['Tipo Rota'].map({0: 'Intraestadual', 1: 'Interestadual'})

fig_rota = px.bar(
    taxa_rota,
    x='Tipo Rota',
    y='Taxa Atraso',
    title='Taxa de Atraso: Rota Intraestadual vs Interestadual',
    color='Tipo Rota',
    color_discrete_sequence=['#2ecc71', '#e74c3c'],
    text=taxa_rota['Taxa Atraso'].apply(lambda x: f'{x:.2%}')
)
fig_rota.update_traces(textposition='outside', textfont_size=16)
fig_rota.update_layout(
    font=dict(size=14), width=600, height=400,
    yaxis_tickformat='.0%', showlegend=False
)
fig_rota.show()

# %% [markdown]
# ### Top 10 Categorias de Produto com Mais Atrasos
#
# Identificar quais categorias de produto são mais vulneráveis
# a atrasos pode guiar decisões de priorização logística.

# %%
taxa_cat = df.groupby('product_category_name')['foi_atraso'].agg(['mean', 'count']).reset_index()
taxa_cat.columns = ['Categoria', 'Taxa Atraso', 'Total Pedidos']
taxa_cat = taxa_cat[taxa_cat['Total Pedidos'] >= 100]  # filtrar categorias com poucos dados
top10_cat = taxa_cat.sort_values('Taxa Atraso', ascending=False).head(10)

fig_cat = px.bar(
    top10_cat,
    x='Taxa Atraso',
    y='Categoria',
    orientation='h',
    title='Top 10 Categorias com Maior Taxa de Atraso (mín. 100 pedidos)',
    color='Taxa Atraso',
    color_continuous_scale='YlOrRd',
    text=top10_cat['Taxa Atraso'].apply(lambda x: f'{x:.1%}')
)
fig_cat.update_traces(textposition='outside')
fig_cat.update_layout(
    font=dict(size=13), width=900, height=500,
    yaxis=dict(autorange='reversed')
)
fig_cat.show()

# %% [markdown]
# ## 8. Análise de Multicolinearidade
#
# ### O que é multicolinearidade?
# Ocorre quando duas features são **altamente correlacionadas entre si**
# (não com o target, mas uma com a outra). Isso é problemático porque:
# - O modelo pode "contar duas vezes" a mesma informação.
# - Os coeficientes de importância ficam instáveis.
#
# **Regra prática:** Se duas features têm correlação > 0.7 entre si,
# considerar manter apenas a mais forte contra `foi_atraso`.

# %%
features_multicol = [
    'price', 'freight_value', 'product_weight_g', 'volume_cm3',
    'frete_ratio', 'velocidade_lojista_dias', 'distancia_haversine_km',
    'rota_interestadual'
]

corr_matrix = df[features_multicol].corr()

fig_multi = px.imshow(
    corr_matrix,
    text_auto='.2f',
    title='Matriz de Multicolinearidade entre Features Candidatas',
    color_continuous_scale='RdBu_r',
    zmin=-1, zmax=1,
    aspect='auto'
)
fig_multi.update_layout(font=dict(size=12), width=800, height=700)
fig_multi.show()

# %% [markdown]
# ### Pares com Alta Multicolinearidade (> 0.7)

# %%
# Identificar pares com correlação > 0.7
pares_altos = []
for i in range(len(features_multicol)):
    for j in range(i+1, len(features_multicol)):
        corr_val = corr_matrix.iloc[i, j]
        if abs(corr_val) > 0.7:
            pares_altos.append({
                'Feature A': features_multicol[i],
                'Feature B': features_multicol[j],
                'Correlação': round(corr_val, 4),
                'Ação Sugerida': 'Avaliar remoção de uma delas'
            })

if pares_altos:
    df_multicol = pd.DataFrame(pares_altos)
    print("⚠️ PARES COM ALTA MULTICOLINEARIDADE (|r| > 0.7):")
    print(df_multicol.to_string(index=False))
else:
    print("✅ Nenhum par de features com multicolinearidade > 0.7")

# %% [markdown]
# ## 9. Tabela-Resumo Final — Ranking Geral de Atributos
#
# Esta é a **entrega principal** deste notebook. A tabela consolida:
# - Todas as features analisadas (diretas + criadas)
# - A métrica de correlação/associação com `foi_atraso`
# - A hipótese de negócio por trás de cada variável
# - Um **veredito** baseado nos dados e no feeling técnico
#
# > 💡 Esta tabela será a referência para o Esquadrão Alpha selecionar
# > as ~6 melhores features na fase de treino do modelo.

# %%
# Montar tabela-resumo consolidada
resumo = []

# Features numéricas (Pearson)
hipoteses = {
    'price': 'Produtos caros recebem prioridade logística?',
    'freight_value': 'Frete alto indica rotas difíceis?',
    'product_weight_g': 'Pacotes pesados geram gargalos logísticos?',
    'volume_cm3': 'Pacotes volumosos complicam a alocação em caminhões?',
    'frete_ratio': 'Frete desproporcional ao preço indica rota crítica?',
    'velocidade_lojista_dias': 'Lojista lento ao despachar causa cascata de atraso?',
    'dia_semana_compra': 'Compras no fim de semana acumulam nos pátios?',
    'distancia_haversine_km': 'Distância geográfica é o fator dominante de atraso?'
}

for _, row in df_pearson.iterrows():
    feat = row['Feature']
    corr_val = row['Correlação (Pearson)']
    abs_corr = abs(corr_val)

    if abs_corr >= 0.10:
        veredito = '✅ Forte candidata'
    elif abs_corr >= 0.05:
        veredito = '⚠️ Avaliar no treino'
    else:
        veredito = '❌ Fraca (mas testar)'

    resumo.append({
        'Feature': feat,
        'Tipo': 'Numérica',
        'Métrica': 'Pearson',
        'Valor': corr_val,
        '|Valor|': abs_corr,
        'Hipótese de Negócio': hipoteses.get(feat, '—'),
        'Veredito': veredito
    })

# Features categóricas (Cramér's V)
hipoteses_cat = {
    'customer_state': 'Destinos remotos (Norte/Nordeste) sofrem mais atrasos?',
    'seller_state': 'Concentração de vendedores em SP afeta rotas longas?',
    'product_category_name': 'Categorias volumosas (móveis) atrasam mais?'
}

for _, row in df_cramer.iterrows():
    feat = row['Feature']
    cv = row["Cramér's V"]

    if cv >= 0.10:
        veredito = '✅ Forte candidata'
    elif cv >= 0.05:
        veredito = '⚠️ Avaliar no treino'
    else:
        veredito = '❌ Fraca (mas testar)'

    resumo.append({
        'Feature': feat,
        'Tipo': 'Categórica',
        'Métrica': "Cramér's V",
        'Valor': cv,
        '|Valor|': cv,
        'Hipótese de Negócio': hipoteses_cat.get(feat, '—'),
        'Veredito': veredito
    })

# Feature binária (rota_interestadual já está em Pearson, mas reforçamos)
df_resumo = pd.DataFrame(resumo)
df_resumo = df_resumo.sort_values('|Valor|', ascending=False).reset_index(drop=True)

print("=" * 100)
print("🏆 TABELA-RESUMO FINAL — RANKING DE ATRIBUTOS vs foi_atraso")
print("=" * 100)
print(df_resumo[['Feature', 'Tipo', 'Métrica', 'Valor', 'Veredito', 'Hipótese de Negócio']].to_string(index=False))

# %% [markdown]
# ### Visualização: Radar de Features
#
# Gráfico para a apresentação final mostrando a "força" relativa
# de cada feature candidata.

# %%
fig_resumo = px.bar(
    df_resumo.sort_values('|Valor|'),
    x='|Valor|',
    y='Feature',
    orientation='h',
    color='Veredito',
    color_discrete_map={
        '✅ Forte candidata': '#2ecc71',
        '⚠️ Avaliar no treino': '#f39c12',
        '❌ Fraca (mas testar)': '#e74c3c'
    },
    title='Ranking Final: Força de cada Feature candidata vs foi_atraso',
    text=df_resumo.sort_values('|Valor|')['|Valor|'].apply(lambda x: f'{x:.4f}')
)
fig_resumo.update_traces(textposition='outside')
fig_resumo.update_layout(
    font=dict(size=13), width=900, height=600,
    yaxis=dict(autorange='reversed'),
    legend_title='Veredito'
)
fig_resumo.show()

# %% [markdown]
# ## 10. Exportação dos Resultados
#
# Salvamos a tabela-resumo como CSV para referência dos outros esquadrões
# e para documentação do projeto.

# %%
# Exportar tabela-resumo
output_path = 'tabela_resumo_correlacoes.csv'
df_resumo.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"✅ Tabela-resumo exportada para: notebooks/{output_path}")

# Exportar DataFrame unificado para uso nos próximos notebooks
df.to_csv('dataset_unificado_v1.csv', index=False)
print(f"✅ DataFrame unificado exportado para: notebooks/dataset_unificado_v1.csv")
print(f"   Shape: {df.shape[0]:,} linhas x {df.shape[1]} colunas")

# %% [markdown]
# ## 11. Conclusões e Próximos Passos
#
# ### O que aprendemos neste notebook:
# 1. O dataset é **desbalanceado** (~93% no prazo / ~7% atraso), o que
#    invalida a acurácia como métrica e exige `scale_pos_weight` no XGBoost.
#
# 2. As features com **maior sinal** de correlação com atrasos serão
#    reveladas na tabela-resumo acima após a execução.
#
# 3. A **multicolinearidade** entre features foi mapeada para evitar
#    redundância no modelo.
#
# ### Próximos passos:
# - **ALPHA-04:** Revisão anti data-leakage sobre este notebook
# - **ALPHA-05:** Aprofundar Feature Engineering com tratamento de NaNs/outliers
# - **ALPHA-06:** Selecionar as ~6 features finais para o treino
# - **ALPHA-07/08:** Split treino/teste e treino do baseline XGBoost
#
# ---
# *Notebook gerado pelo Esquadrão Alpha — Olist Logistics Growth*
