# %% [markdown]
# # 📐 Normalização de Dados — Guia Didático Completo
#
# **Projeto:** Olist Logistics Growth — Previsão de Atrasos Logísticos
#
# **Objetivo deste notebook:**
# Entender o que é normalização de dados, por que ela existe, quais são
# as técnicas principais e, mais importante: **por que o nosso modelo
# XGBoost NÃO precisa dela** (mas outros modelos precisam).
#
# Este notebook usa os **dados reais do nosso projeto** para demonstrar
# cada conceito de forma visual e prática.
#
# ---

# %% [markdown]
# ## 1. O Problema: Features com Escalas Diferentes
#
# ### O que acontece quando as features têm escalas muito diferentes?
#
# Imagine que você quer comparar duas features do nosso dataset:
# - `distancia_haversine_km`: varia de **0 a 8.678 km**
# - `customer_state_encoded`: varia de **0.03 a 0.21**
#
# A distância tem números na casa dos **milhares**.
# O estado codificado tem números na casa dos **centésimos**.
#
# Para um ser humano, isso não é problema — sabemos que são unidades
# diferentes. Mas para **alguns algoritmos de Machine Learning**,
# essa diferença de escala cria um viés grave: o algoritmo "acha"
# que a distância é milhares de vezes mais importante que o estado,
# simplesmente porque os números são maiores.
#
# > ⚠️ **Isso NÃO é verdade para todos os modelos.** Vamos ver quais
# > sofrem e quais não sofrem com esse problema.

# %%
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Carregar a tabela de treino do projeto
df = pd.read_csv('dataset_treino_v1.csv')

print(f"Dataset carregado: {df.shape[0]:,} linhas x {df.shape[1]} colunas")
print(f"Colunas: {df.columns.tolist()}")

# %% [markdown]
# ### Visualizando o problema: Escalas Brutas
#
# O gráfico abaixo mostra a **escala real** de cada feature do nosso
# dataset de treino. Note como a `distancia_haversine_km` domina
# visualmente — isso é exatamente o que acontece dentro de alguns
# algoritmos quando os dados não são normalizados.

# %%
features = [c for c in df.columns if c != 'foi_atraso']

stats = pd.DataFrame({
    'Feature': features,
    'Min': [df[f].min() for f in features],
    'Max': [df[f].max() for f in features],
    'Media': [df[f].mean() for f in features],
    'Std': [df[f].std() for f in features]
})

fig_escala = px.bar(
    stats,
    x='Feature',
    y='Max',
    title='Escala Bruta: Valor Máximo de Cada Feature (SEM normalização)',
    color='Max',
    color_continuous_scale='Viridis',
    text=stats['Max'].apply(lambda x: f'{x:,.1f}')
)
fig_escala.update_traces(textposition='outside')
fig_escala.update_layout(font=dict(size=13), width=900, height=500)
fig_escala.show()

# %% [markdown]
# Perceba como a `distancia_haversine_km` (máx 8.678) engole todas
# as outras visualmente. Para um algoritmo como **KNN** ou **Regressão
# Logística**, isso significaria que a distância dominaria 100% das
# decisões, mesmo que `velocidade_lojista_dias` seja a feature
# mais correlacionada com atrasos.
#
# ---

# %% [markdown]
# ## 2. O que é Normalização?
#
# **Normalização** é o processo de transformar os valores das features
# para que todas fiquem na **mesma escala**, sem perder a informação
# relativa entre os dados.
#
# ### Analogia simples
# Imagine que você quer comparar a nota de um aluno em duas provas:
# - **Prova A:** nota máxima 10, o aluno tirou **8**
# - **Prova B:** nota máxima 1000, o aluno tirou **750**
#
# Sem normalizar, o "8" parece ridículo ao lado do "750".
# Mas se normalizarmos para a mesma escala (0 a 1):
# - Prova A: 8/10 = **0.80** (80%)
# - Prova B: 750/1000 = **0.75** (75%)
#
# Agora vemos que o aluno foi **melhor na Prova A!**
# A normalização revelou a verdade que os números brutos escondiam.
#
# ---

# %% [markdown]
# ## 3. Técnicas de Normalização
#
# Existem duas técnicas principais. Ambas transformam os dados
# para uma escala padronizada, mas de formas diferentes.
#
# ---

# %% [markdown]
# ### 3.1 Min-Max Scaling (Reescalonamento)
#
# **Fórmula:**
# ```
# X_normalizado = (X - X_min) / (X_max - X_min)
# ```
#
# **O que faz:** Comprime todos os valores para o intervalo **[0, 1]**.
# O menor valor vira 0, o maior vira 1, e todos os outros ficam
# proporcionalmente entre eles.
#
# **Quando usar:** Quando você sabe que os dados **não têm outliers
# extremos** e quer manter todos os valores em um range fixo.
#
# **Problema:** Se houver um outlier (ex: uma distância de 8.678 km
# quando a média é 596 km), ele "puxa" toda a escala, comprimindo
# 99% dos dados perto do zero.

# %%
from sklearn.preprocessing import MinMaxScaler

# Aplicar Min-Max Scaling
scaler_mm = MinMaxScaler()
df_minmax = pd.DataFrame(
    scaler_mm.fit_transform(df[features]),
    columns=features
)

print("="*60)
print("MIN-MAX SCALING (0 a 1)")
print("="*60)
for feat in features:
    print(f"  {feat:35s} | Min: {df_minmax[feat].min():.4f} | Max: {df_minmax[feat].max():.4f} | Media: {df_minmax[feat].mean():.4f}")

# %%
fig_mm = px.box(
    df_minmax.melt(var_name='Feature', value_name='Valor'),
    x='Feature',
    y='Valor',
    title='Distribuição Após Min-Max Scaling (0 a 1)',
    color='Feature'
)
fig_mm.update_layout(font=dict(size=12), width=900, height=500, showlegend=False)
fig_mm.show()

# %% [markdown]
# ### Observação do Min-Max no nosso dataset
#
# Note como as features com outliers (distância, frete, velocidade do
# lojista) ficaram com a **maioria dos dados concentrada perto do zero**
# e poucos pontos esticados até o 1. Isso acontece porque um único
# valor extremo (ex: 8.678 km) "achata" todos os outros.
#
# ---

# %% [markdown]
# ### 3.2 Standard Scaling (Z-Score / Padronização)
#
# **Fórmula:**
# ```
# X_padronizado = (X - media) / desvio_padrao
# ```
#
# **O que faz:** Transforma os dados para que tenham **média = 0** e
# **desvio padrão = 1**. Os valores ficam distribuídos ao redor do zero,
# onde valores negativos estão "abaixo da média" e positivos "acima da média".
#
# **Quando usar:** Quando os dados podem ter outliers e você quer que
# eles não dominem a escala. É a técnica mais usada na prática.
#
# **Vantagem sobre Min-Max:** Outliers não "achatam" os dados porque
# a transformação é baseada na média e no desvio, não no min/max.

# %%
from sklearn.preprocessing import StandardScaler

scaler_ss = StandardScaler()
df_standard = pd.DataFrame(
    scaler_ss.fit_transform(df[features]),
    columns=features
)

print("="*60)
print("STANDARD SCALING (Z-Score: media=0, std=1)")
print("="*60)
for feat in features:
    print(f"  {feat:35s} | Media: {df_standard[feat].mean():.4f} | Std: {df_standard[feat].std():.4f}")

# %%
fig_ss = px.box(
    df_standard.melt(var_name='Feature', value_name='Valor'),
    x='Feature',
    y='Valor',
    title='Distribuição Após Standard Scaling (Z-Score)',
    color='Feature'
)
fig_ss.update_layout(font=dict(size=12), width=900, height=500, showlegend=False)
fig_ss.show()

# %% [markdown]
# ### Comparação Visual: Antes vs Min-Max vs Z-Score

# %%
# Comparar as 3 versoes para uma feature especifica
feat_demo = 'distancia_haversine_km'
amostra = 5000  # pegar amostra para nao travar o grafico

fig_comp = make_subplots(rows=1, cols=3,
    subplot_titles=['Dados Brutos (Original)', 'Min-Max (0 a 1)', 'Z-Score (media=0)'])

fig_comp.add_trace(
    go.Histogram(x=df[feat_demo].sample(amostra), name='Original',
                 marker_color='#3498db', nbinsx=50),
    row=1, col=1
)
fig_comp.add_trace(
    go.Histogram(x=df_minmax[feat_demo].sample(amostra), name='Min-Max',
                 marker_color='#2ecc71', nbinsx=50),
    row=1, col=2
)
fig_comp.add_trace(
    go.Histogram(x=df_standard[feat_demo].sample(amostra), name='Z-Score',
                 marker_color='#e74c3c', nbinsx=50),
    row=1, col=3
)

fig_comp.update_layout(
    title_text=f'Comparação: {feat_demo} — Original vs Min-Max vs Z-Score',
    font=dict(size=12), width=1100, height=400,
    showlegend=False
)
fig_comp.show()

# %% [markdown]
# **Observe:** A **forma** da distribuição é idêntica nas três versões!
# A normalização **NÃO muda o formato dos dados**, apenas reposiciona
# e reescala os números. A informação relativa entre os pontos é preservada.
#
# ---

# %% [markdown]
# ## 4. Quais Modelos PRECISAM de Normalização?
#
# ### Modelos que PRECISAM (baseados em distância ou gradiente):
#
# | Modelo | Por que precisa? |
# |:--|:--|
# | **KNN** (K-Nearest Neighbors) | Calcula a "distância" entre pontos. Se distância vai de 0 a 8.678 e frete vai de 0 a 410, a distância domina o cálculo |
# | **Regressão Logística** | Os coeficientes são influenciados pela escala. Features maiores parecem mais importantes |
# | **SVM** (Support Vector Machine) | Mesma razão do KNN — trabalha com distâncias no espaço |
# | **Redes Neurais** (Deep Learning) | Os pesos são atualizados por gradiente. Escalas muito diferentes fazem o treino oscilar e não convergir |
# | **PCA** (Redução de Dimensionalidade) | Calcula variância. Features com números maiores dominam as componentes principais |
#
# ### Modelos que NÃO PRECISAM (baseados em árvores de decisão):
#
# | Modelo | Por que NÃO precisa? |
# |:--|:--|
# | **XGBoost** ⬅️ (nosso modelo) | Faz perguntas do tipo "frete > 30?". Se o frete for 30 ou 0.003 (normalizado), a pergunta muda mas o resultado é o mesmo |
# | **Random Forest** | Mesmo princípio — árvores de decisão |
# | **LightGBM** | Mesmo princípio — árvores de decisão |
# | **CatBoost** | Mesmo princípio — árvores de decisão |
# | **Decision Tree** | O modelo mais básico de árvore — também imune a escala |
#
# ---

# %% [markdown]
# ## 5. Demonstração Prática: Por que Árvores Não Ligam para Escala
#
# Vamos provar visualmente que o XGBoost toma a **mesma decisão**
# independentemente de os dados estarem normalizados ou não.
#
# ### Como uma árvore de decisão funciona?
# Ela faz perguntas binárias (sim/não) sobre os dados:
# ```
# "velocidade_lojista_dias > 3.5?"
#     → SIM: risco alto de atraso
#     → NÃO: "frete > 25?"
#         → SIM: risco médio
#         → NÃO: risco baixo
# ```
#
# O ponto de corte (3.5, 25, etc.) se ajusta automaticamente à
# escala dos dados. Se normalizarmos, a árvore simplesmente
# mudaria a pergunta para:
# ```
# "velocidade_lojista_dias > 0.0046?" (que é o 3.5 normalizado)
# ```
#
# O resultado final é **idêntico**.

# %%
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import xgboost as xgb

X = df[features]
y = df['foi_atraso']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# --- Treinar com dados BRUTOS (sem normalizar) ---
model_bruto = xgb.XGBClassifier(
    n_estimators=100, max_depth=4,
    scale_pos_weight=14, random_state=42,
    eval_metric='logloss', verbosity=0
)
model_bruto.fit(X_train, y_train)
auc_bruto = roc_auc_score(y_test, model_bruto.predict_proba(X_test)[:, 1])

# --- Treinar com dados NORMALIZADOS (Z-Score) ---
scaler = StandardScaler()
X_train_norm = pd.DataFrame(scaler.fit_transform(X_train), columns=features)
X_test_norm = pd.DataFrame(scaler.transform(X_test), columns=features)

model_normalizado = xgb.XGBClassifier(
    n_estimators=100, max_depth=4,
    scale_pos_weight=14, random_state=42,
    eval_metric='logloss', verbosity=0
)
model_normalizado.fit(X_train_norm, y_train)
auc_normalizado = roc_auc_score(y_test, model_normalizado.predict_proba(X_test_norm)[:, 1])

print("="*60)
print("PROVA: XGBoost COM vs SEM Normalizacao")
print("="*60)
print(f"  ROC-AUC SEM normalizar:  {auc_bruto:.6f}")
print(f"  ROC-AUC COM normalizar:  {auc_normalizado:.6f}")
print(f"  Diferenca:               {abs(auc_bruto - auc_normalizado):.6f}")
print(f"\n  Conclusao: A diferenca e {abs(auc_bruto - auc_normalizado):.6f},")
print(f"  ou seja, PRATICAMENTE ZERO. Normalizar nao mudou nada.")

# %% [markdown]
# ### Resultado Esperado
#
# Os dois ROC-AUC devem ser **praticamente idênticos** (diferença na
# 4ª-6ª casa decimal, causada apenas por arredondamentos internos).
#
# Isso **prova empiricamente** que, para o XGBoost, normalizar é um
# passo desnecessário que apenas adiciona complexidade ao pipeline
# sem nenhum ganho de performance.
#
# ---

# %% [markdown]
# ## 6. Quando Normalizar no Nosso Projeto?
#
# ### Resposta: NUNCA (para o modelo XGBoost)
#
# O nosso modelo de previsão de atrasos é um **XGBoost**, que é baseado
# em árvores de decisão. Como demonstrado acima, árvores são **imunes
# à escala** das features.
#
# ### Quando USARÍAMOS normalização?
#
# Se, no futuro, alguém quiser:
# 1. **Comparar features visualmente** em gráficos (ex: radar chart) → Usar Min-Max
# 2. **Treinar uma Rede Neural** com esses dados → Usar Z-Score (Standard Scaler)
# 3. **Usar KNN** para encontrar pedidos similares → Usar Z-Score
# 4. **Fazer PCA** para redução de dimensionalidade → Usar Z-Score
#
# Para o **escopo atual do projeto (XGBoost)**, a normalização é
# **desnecessária e não será aplicada**.
#
# ---

# %% [markdown]
# ## 7. Resumo Visual
#
# | Conceito | O que é | Quando usar |
# |:--|:--|:--|
# | **Min-Max** | Comprime para [0,1] | Dados sem outliers + modelos de distância |
# | **Z-Score** | Centraliza em média=0, std=1 | Dados com outliers + redes neurais |
# | **Sem normalizar** | Dados brutos | Modelos de árvore (XGBoost, Random Forest) |
#
# ---
# *Notebook gerado pelo Esquadrão Alpha — Olist Logistics Growth*
