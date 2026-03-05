# Olist Logistics Growth — Previsão de Atrasos 📦🚚

Aplicação de Machine Learning focada em **prever atrasos logísticos** no e-commerce da Olist, utilizando dados reais de ~100 mil pedidos para reduzir cancelamentos e maximizar a retenção de clientes (Growth).

---

## 🎯 Objetivo

Construir uma aplicação web (Streamlit) com 3 abas que permita:

1. **Painel Gerencial** — Dashboard interativo com métricas logísticas históricas, filtros por estado/data e mapa de calor do Brasil.
2. **Insights Valiosos** — Descobertas de negócio sobre os principais ofensores de atraso (rotas, vendedores, categorias).
3. **Motor de Predição** — Simulador onde o usuário insere dados de um novo pedido (CEP, produto, frete) e o modelo de ML retorna a probabilidade de atraso.

---

## 📊 Dataset

**Fonte:** [Olist Brazilian E-Commerce (Kaggle)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
**Período:** Set/2016 — Out/2018
**Volume:** ~100k pedidos | 9 tabelas CSV

| Tabela | Descrição |
|:--|:--|
| `olist_orders_dataset` | Base principal com datas de entrega (estimada vs real) |
| `olist_customers_dataset` | Estado e CEP do cliente |
| `olist_order_items_dataset` | Preço, frete e vendedor por item |
| `olist_products_dataset` | Peso, dimensões e categoria do produto |
| `olist_sellers_dataset` | Estado e CEP do vendedor |
| `olist_geolocation_dataset` | Latitude/Longitude por CEP |
| `olist_order_payments_dataset` | Tipo e valor do pagamento |
| `olist_order_reviews_dataset` | Avaliações dos clientes |
| `product_category_name_translation` | Tradução PT→EN das categorias |

---

## 🧠 Modelo de Machine Learning

| Aspecto | Detalhe |
|:--|:--|
| **Algoritmo** | XGBoost Classifier (Classificação Binária) |
| **Variável Alvo** | `foi_atraso` → 1 se entregou depois do prazo, 0 se no prazo |
| **Distribuição** | 93,22% no prazo / 6,77% atrasado (desbalanceado) |
| **Métrica Principal** | ROC-AUC ≥ 0.70 |
| **Balanceamento** | `scale_pos_weight` + Split Estratificado |

> Detalhes completos em [`spec/model_spec.md`](spec/model_spec.md)

---

## 🛠️ Stack Tecnológica

| Função | Biblioteca |
|:--|:--|
| Dados | `pandas`, `numpy` |
| Machine Learning | `scikit-learn`, `xgboost`, `joblib` |
| Visualização | `plotly` |
| Aplicação Web | `streamlit` |
| Deploy | Streamlit Community Cloud |

> Stack completa em [`spec/stack.md`](spec/stack.md)

---

## 📁 Estrutura do Repositório

```
olist-dataset/
├── dataset/              # CSVs originais (ignorados pelo Git)
├── docs/                 # Planejamento, cronograma, insights e dicionário de dados
│   ├── data/             # Dicionário de dados e guia de features
│   ├── insights/         # Hipóteses de negócio e análise de atraso
│   ├── algorithms/       # Material didático (Pearson, K-Means)
│   └── schedule/         # Cronograma de 4 dias e sprints diários
├── spec/                 # Especificação técnica para agentes de IA
│   ├── project_spec.md   # Escopo, restrições e regras do projeto
│   ├── stack.md          # Stack oficial
│   ├── data_schema.md    # Schema do DataFrame e features
│   └── model_spec.md     # Configuração do XGBoost
├── .gitignore
└── README.md
```

---

## 👥 Equipe

| Esquadrão | Membros | Foco |
|:--|:--|:--|
| 🐺 **Alpha** (Insights & ML) | Mauricio, Henry, Lucas | EDA, Feature Engineering, XGBoost |
| 🦅 **Delta** (Painel Visual) | Pablo, Douglas | App Streamlit, gráficos Plotly |
| 🦉 **Omega** (Negócios) | Anderson, Gabriel | Narrativa, slides, apresentação |

---

## 🚀 Setup & Execução

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar o Dashboard
streamlit run app.py
```

---

## 📝 Convenções de Git

| Prefixo | Uso |
|:--|:--|
| `feat/` | Novas funcionalidades |
| `fix/` | Correções de bugs |
| `docs/` | Documentação |
| `refactor/` | Refatoração de código |

**Commits:** Usar prefixos semânticos (`feat:`, `fix:`, `docs:`, `refactor:`).
**Pull Requests:** Revisão obrigatória antes do merge na `main`.
