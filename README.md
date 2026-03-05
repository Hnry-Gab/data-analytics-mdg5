# Olist E-Commerce Growth Analytics

Plataforma de inteligência de cliente e analytics de crescimento para o dataset Olist Brazilian E-Commerce, habilitando decisões data-driven para retenção, otimização de CLV e crescimento de receita através de modelos de machine learning avançados e visualizações interativas.

---

## Dataset & Schema

**Fonte:** Olist Brazilian E-Commerce Public Dataset (Kaggle)  
**Período:** Setembro 2016 - Outubro 2018  
**Volume:** ~100k ordens, ~99k clientes, ~1M registros (8 tabelas CSV)

**Tabelas Principais:**
- `customers`: Identificação e geolocalização do cliente
- `orders`: Timestamps, status e métricas de entrega
- `order_items`: Produtos, preços e frete por ordem
- `payments`: Tipo de pagamento, parcelas e valor
- `reviews`: Avaliações e comentários (NLP)
- `products`: Categorias e características físicas
- `sellers`: Informações dos vendedores
- `category_translation`: Tradução de categorias PT→EN

**Schema DataFrame Master:**
```python
{
    'order_id', 'customer_unique_id', 'order_status',
    'order_purchase_timestamp', 'delivery_delay_days',
    'customer_state', 'customer_city',
    'product_category_name_english', 'price', 'freight_value',
    'total_order_value', 'payment_type', 'payment_installments',
    'review_score', 'review_comment_message'
}
```

---

## Stack Tecnológica

**Core:** Python 3.10+, pandas, numpy  
**Machine Learning:** scikit-learn, XGBoost/LightGBM, lifetimes  
**Causal Inference:** causalml (Uplift Modeling)  
**NLP:** nltk, spacy (processamento de texto em português)  
**Visualização:** plotly, seaborn, streamlit  
**Storage:** parquet (compressão snappy)  
**Testes:** pytest, playwright (E2E dashboard)  
**VCS:** Git (main=production, development=dev)

---

## Técnicas de Análise

**Descritiva:** RFM, Cohort Analysis, Geographic, Funnel  
**Preditiva:** Churn Prediction (>180 dias), CLV Prediction, Order Prediction  
**Causal:** Uplift Modeling (incentivos), Attribution Analysis (reviews, frete, pagamento)  
**NLP:** Sentiment Analysis, Topic Modeling, Text Preprocessing  
**Association Rules:** Cross-sell, Apriori Algorithm, Market Basket Analysis

---

## Modelos de Predição

**Churn Prediction:** XGBoost Classifier
- Features: Recência, Frequência, Monetary, avg_review_score, avg_delivery_delay, payment_type, product_category, customer_state
- Target: `churn_flag` (1 = inativo >180 dias)
- Output: `churn_probability` (0-1)

**CLV Prediction:** BG/NBD + Gamma-Gamma (Probabilístico)
- BG/NBD: Prediz transações futuras (frequency, recency, T)
- Gamma-Gamma: Estima valor monetário por transação
- Output: `expected_purchases`, `expected_clv` (90/180/365 dias)

**Review Sentiment:** NLP Pipeline
- Preprocessing: lowercase, stopwords PT, tokenization, stemming
- Features: TF-IDF vectors
- Model: Logistic Regression / Naive Bayes
- Output: `sentiment_score` (-1 a 1)

**Uplift Modeling:** Two-Model Approach / CausalML Meta-Learners
- Treatment: campanha/incentivo
- Control: sem intervenção
- Output: `uplift_score` (lift incremental)

---

## Estratégias de Clustering

**RFM Clustering (K-Means):**
- Features: Recency, Frequency, Monetary
- Preprocessing: log transform, StandardScaler, outlier handling
- n_clusters=5: Champions, Loyal Customers, Potential Loyalists, At Risk, Lost

**BG/NBD Segmentation (Probabilístico):**
- Valuable High-CLV (top 25%, baixo risco)
- Loyal Mid-CLV (meio 50%, baixo risco)
- Developing (CLV menor, engajamento moderado)
- At Risk (CLV moderado, alta prob. churn)
- Lost/Hibernating (CLV baixo, alta prob. churn)

**Geographic Clustering:** Estados por GMV, crescimento, atraso entrega, churn

**Category-Based Clustering:** Categorias por preço, volume, frete, review, cancelamento

---

## Estrutura do Projeto (7 Partes)

Cada parte possui complexidade e carga de trabalho balanceadas (densidade média):

**Part 1: Data Pipeline Foundation**
- Ingestão CSV, joins sequenciais, limpeza, cache parquet, configuração

**Part 2: Customer Analytics Core**
- RFM analysis, feature engineering, churn labels, cohort analysis

**Part 3: Segmentation Models**
- K-Means clustering, BG/NBD, segment labeling logic

**Part 4: Value Prediction**
- CLV calculation, Gamma-Gamma, probabilistic forecasting

**Part 5: Churn Prediction**
- XGBoost model, feature engineering, feature importance, SHAP

**Part 6: Advanced Analytics**
- NLP sentiment analysis, cross-sell Apriori, causal inference (uplift)

**Part 7: Dashboard & Testing**
- Streamlit multi-page app (5 páginas), E2E tests (Playwright), unit tests (pytest)

---

## Entregáveis

**Módulos Python (`src/`):**
```
config.py           # Constantes e paths
data_loader.py      # Ingestão CSV e master order join
data_cleaner.py     # Missing values, outliers, timestamps
feature_engineering.py  # RFM, CLV, churn labels, derived features
cache.py            # DataFrame parquet caching + decorators
models/rfm.py       # K-Means clustering
models/clv.py       # CLV calculation + BG/NBD
models/churn.py     # Churn prediction (XGBoost)
models/cross_sell.py # Market basket analysis
models/bgnd.py      # BG/NBD probabilistic modeling
models/sentiment.py # NLP sentiment analysis
attribution.py      # Geographic, payment, cohort
```

**Jupyter Notebook (`notebooks/`):**
- `olist_analysis.ipynb`: EDA completo, visualizações, todos os modelos, insights

**Streamlit Dashboard (`dashboard/`):**
```
app.py                    # Multi-page shell
pages/01_overview.py      # KPIs, time series, mapa geográfico
pages/02_rfm.py           # 3D scatter, segment summary
pages/03_clv.py           # CLV distribution, top customers
pages/04_churn.py         # Risk distribution, feature importance
pages/05_attribution.py   # Payment, cohort, cross-sell
```

**Testes (`tests/`):**
- Unit tests (todos os módulos)
- Data validation tests
- Model prediction tests
- E2E dashboard tests (Playwright)

**Documentação:**
- README.md
- spec/macro.md (planejamento macro)
- spec/plan/part_1.md ... part_7.md (planejamento micro)
- .streamlit/config.toml (configuração Streamlit)

---

## Setup & Execução

**Instalação:**
```bash
pip install -r requirements.txt
```

**Executar Dashboard:**
```bash
cd dashboard
streamlit run app.py
```

**Executar Testes:**
```bash
pytest tests/
```

**Estrutura de Branches:**
- `main` → PRODUCTION
- `development` → DEVELOPMENT
- `feat/feature`, `fix/fix`, `chore/doc`, `refactor/feature`
- Pull requests para code review

---

## Convenções de Git

**Branches:**
- `main`: produção estável
- `development`: desenvolvimento contínuo
- `feat/`: novas features
- `fix/`: correções de bugs
- `chore/`: documentação, refatoração

**Commits:**
- Mensagens descritivas e concisas
- Prefixos: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`

**Pull Requests:**
- Code review obrigatório
- Tests passando antes do merge
- Documentação atualizada

---

## Design System Dashboard

**Cores:**
- Primária: To Implement
- Background: To Implement
- Background Secundário: To Implement
- Texto: To Implement

**Tipografia:** To Implement
**Layout:** To Implement
**Caching:** @st.cache_data com ttl=3600 (1 hora)

**Visualizações:**
- plotly.express: gráficos interativos (scatter, line, bar, choropleth)
- plotly.graph_objects: customizações avançadas
- st.metric(): KPI cards com delta
- st.dataframe(): tabelas com ordenação
- px.scatter_3d(): visualização 3D RFM
- px.choropleth(): mapa geográfico

---

## Performance & Otimização

**Data Pipeline:**
- Parquet com compressão snappy (I/O otimizado)
- Joins sequenciais para evitar perda de dados
- @cache_dataframe decorator (save/load automático)

**Dashboard:**
- @st.cache_data para carregamento de dados
- Limitar tamanho de figuras plotly em datasets grandes

**Model Training:**
- Feature scaling obrigatório (StandardScaler/RobustScaler)
- Outlier handling (cap at 99th percentile)
- Cross-validation para validação de modelos

---

## Métricas de Avaliação

**Churn Model:** ROC-AUC, Precision, Recall, F1-Score  
**CLV Model:** Comparação Simple vs. BG/NBD (MAE, RMSE)  
**RFM Clustering:** Silhouette Score, Elbow Method  
**Sentiment Model:** Accuracy, Classification Report  
**Uplift Model:** AUUC (Area Under Uplift Curve)

---

## Riscos & Mitigação

**Data Leakage:** Limpar timestamps considerando "tempo de corte"  
**Custo de Memória:** Unir tabelas progressivamente, usar Parquet  
**Desbalanceamento de Classes:** SMOTE, scale_pos_weight (XGBoost)  
**Janela Estática:** Dataset limitado 2016-2018, churn >180 dias pode ser muito longo  
**Frequência:** 95% clientes compraram apenas 1 vez (F=1 enviesado)  
**Premissa Gamma-Gamma:** Validar independência entre valor monetário e frequência  
**K-Means Sensitivity:** Escalar dados antes do treino, outliers tratados

---

## Contato

Para questões sobre implementação, bugs ou melhorias, consulte:
- `spec/macro.md`: Planejamento completo do projeto
- `spec/plan/part_*.md`: Detalhes de cada fase de implementação
- Issues no GitHub para bugs e feature requests
