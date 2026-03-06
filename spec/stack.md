# Stack Tecnológica Oficial

> Versões mínimas recomendadas. O `requirements.txt` na raiz do projeto deve refletir este arquivo.

---

## Linguagem
- **Python 3.10+**

## Manipulação de Dados
- `pandas` — DataFrames e operações tabulares
- `numpy` — Operações numéricas e vetorizadas

## Machine Learning
- `scikit-learn` — train_test_split, métricas (ROC-AUC, F1, confusion_matrix), pipelines
- `xgboost` — Algoritmo principal de classificação binária (Atraso Sim/Não)
- `joblib` — Serialização do modelo treinado (exportar `.pkl`)

## Visualização
## Visualização
- `plotly` (Python) + `plotly.js` (Frontend) — Gráficos interativos (barras, dispersão, mapas choropleth) no backend e no browser

## Aplicação Web
- **Frontend:** HTML5, CSS3, Vanilla JavaScript puro
- **Backend:** FastAPI, Python, Servidor Web Uvicorn
- **Ferramentas LLM:** Protocolo MCP (Model Context Protocol)

## Ambiente de Desenvolvimento
- `jupyter` — Notebooks para EDA e experimentação do modelo (Esquadrão Alpha)

## Deploy
- **VPS** — Tanto o Frontend HTML quanto o Backend API (FastAPI + MCP) serão hospedados e geridos em um servidor VPS unificado.

---

## Bibliotecas que NÃO serão utilizadas

| Biblioteca | Motivo da Exclusão |
|:--|:--|
| `lifetimes` | CLV/BG-NBD fora do escopo |
| `causalml` | Uplift Modeling fora do escopo |
| `nltk` / `spacy` | NLP fora do escopo |
| `pytest` / `playwright` | Testes automatizados fora do escopo de 4 dias |
| `seaborn` | Padronizamos no `plotly.js` para integração nativa com o Frontend |
