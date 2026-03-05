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
- `plotly` — Gráficos interativos (barras, dispersão, mapas choropleth) compatíveis com Streamlit

## Aplicação Web
- `streamlit` — Interface web unificada (Dashboard + Insights + Simulador de Predição)

## Ambiente de Desenvolvimento
- `jupyter` — Notebooks para EDA e experimentação do modelo (Esquadrão Alpha)

## Deploy
- **Streamlit Community Cloud** (free tier)
- Vinculado diretamente ao repositório GitHub (deploy automático via push na main)

---

## Bibliotecas que NÃO serão utilizadas

| Biblioteca | Motivo da Exclusão |
|:--|:--|
| `lifetimes` | CLV/BG-NBD fora do escopo |
| `causalml` | Uplift Modeling fora do escopo |
| `nltk` / `spacy` | NLP fora do escopo |
| `pytest` / `playwright` | Testes automatizados fora do escopo de 4 dias |
| `seaborn` | Padronizamos no `plotly` para integração nativa com Streamlit |
