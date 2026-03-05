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
- `ECharts/Chart.js` — Gráficos interativos (barras, dispersão, mapas choropleth) compatíveis com chamadas assíncronas no JS

## Aplicação Web (Frontend)
- **HTML5 / CSS3 Vanilla** — Sem frameworks pesados (Tailwind só se necessário), foco em Web Design moderno (Glassmorphism, Dark mode).
- **Vanilla JavaScript** — Lógica de interface, Fetch API para conectar com o backend.

## Backend (API Olist)
- `fastapi` — Criação da API REST assíncrona super-rápida.
- `uvicorn` — Servidor ASGI para rodar o FastAPI.
- `pydantic` — Validação estrita de dados de entrada do frontend.

## Integração Inteligente (IA)
- **MCP Server (Model Context Protocol)** — Servidor Python para conectar a inteligência do motor de previsão a agentes LLM externos.

## Deploy
- **Backend/API:** Render ou Railway (suporte nativo a containers FastAPI/Python).
- **Frontend:** Vercel ou GitHub Pages (hospedagem de estáticos HTML/JS).

---

## Bibliotecas que NÃO serão utilizadas

| Biblioteca | Motivo da Exclusão |
|:--|:--|
| `lifetimes` | CLV/BG-NBD fora do escopo |
| `causalml` | Uplift Modeling fora do escopo |
| `nltk` / `spacy` | NLP fora do escopo |
| `pytest` / `playwright` | Testes automatizados fora do escopo de 4 dias |
| `streamlit` | Trocado por HTML/JS + FastAPI para maior escalabilidade gráfica e de API |
