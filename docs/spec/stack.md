# Stack Tecnológica Oficial

> Versões mínimas recomendadas. Os requirements estão em `requirementsANALISE.txt` (raiz e `src/olist_mcp/`).

---

## Linguagem
- **Python 3.10+**

## Manipulação de Dados
- `pandas` ≥ 2.0.0 — DataFrames e operações tabulares
- `numpy` ≥ 1.24.0 — Operações numéricas e vetorizadas

## Machine Learning
- `catboost` ≥ 1.2.0 — **Algoritmo principal** de classificação binária (CatBoost V5, ROC-AUC 0.8454)
- `scikit-learn` ≥ 1.3.0 — train_test_split, métricas (ROC-AUC, F1, confusion_matrix), pipelines
- `imbalanced-learn` ≥ 0.11.0 — SMOTE para oversampling da classe minoritária
- `joblib` ≥ 1.3.0 — Serialização do modelo treinado (`.pkl`)

## Visualização
- `plotly` ≥ 5.18.0 (Python) + `plotly.js` (Frontend) — Gráficos interativos (barras, dispersão, mapas choropleth)
- `kaleido` ≥ 0.2.1 — Exportação de gráficos Plotly como imagens estáticas (PNG/SVG)
- `Pillow` ≥ 10.0.0 — Manipulação de imagens para visualizações

## MCP Server (Chatbot Integration)
- `fastmcp` ≥ 3.0.0 — Framework para Model Context Protocol (MCP) com transport stdio
- `pydantic` ≥ 2.5.0 — Validação de schemas para tools MCP
- `tabulate` ≥ 0.9.0 — Formatação de tabelas markdown (`pandas.to_markdown()`)
- `python-dateutil` ≥ 2.8.0 — Parsing de datas

## Aplicação Web
- **Frontend:** HTML5, CSS3, Vanilla JavaScript puro
- **Backend:** FastAPI ≥ 0.110.0, Uvicorn ≥ 0.27.0
- **Chatbot LLM:** OpenRouter API via `httpx` ≥ 0.27.0 (async streaming)
- **Protocolo:** SSE (Server-Sent Events) para streaming de respostas

## Ambiente de Desenvolvimento
- `jupyter` ≥ 1.0.0 — Notebooks para EDA e experimentação
- `python-dotenv` = 1.0.0 — Variáveis de ambiente (.env)

## Deploy
- **VPS** — Frontend HTML + Backend API (FastAPI + MCP) em servidor unificado

---

## Evolução da Stack

| Componente | Antes (v1–v4) | Atual (v5) |
|:--|:--|:--|
| Modelo ML | XGBoost | **CatBoost** (categóricas nativas) |
| MCP Framework | 60 tools manuais | **FastMCP** (22 tools refatorados) |
| Balanceamento | `scale_pos_weight` | **SMOTE** (imbalanced-learn) |
| Encoding categórico | LabelEncoder manual | **Nativo CatBoost** (ordered target encoding) |

---

## Bibliotecas que NÃO são utilizadas

| Biblioteca | Motivo da Exclusão |
|:--|:--|
| `xgboost` | Substituído pelo CatBoost V5 (melhor ROC-AUC, categóricas nativas) |
| `lifetimes` | CLV/BG-NBD fora do escopo |
| `causalml` | Uplift Modeling fora do escopo |
| `nltk` / `spacy` | NLP fora do escopo |
| `seaborn` | Padronizado no `plotly.js` para integração com Frontend |
