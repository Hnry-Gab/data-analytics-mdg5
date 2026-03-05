# Critérios de Sucesso e Plano de Contingência

Este documento define os critérios mínimos aceitáveis para considerar o projeto aprovado e as ações corretivas caso alguma frente não atinja a meta.

---

## Critérios de Sucesso do Modelo de ML

| Métrica | Meta Mínima | Justificativa |
|:--|:--|:--|
| **ROC-AUC** | ≥ 0.70 | Capacidade geral de separar pedidos atrasados dos pontuais |
| **Recall** | ≥ 0.60 | Percentual de atrasos reais que a IA consegue identificar |
| **F1-Score** | ≥ 0.50 | Equilíbrio entre Precisão e Recall |

> **Importante:** Não usar **Acurácia** como métrica principal. Como a base é desbalanceada (93% classe 0 / 7% classe 1), um modelo que chute "nunca atrasa" teria 93% de acurácia mas seria completamente inútil.

## Critérios de Sucesso do Dashboard

| Critério | Meta |
|:--|:--|
| Web App rodando sem erros | Obrigatório |
| 3 abas funcionais (Painel, Insights, Simulador) | Obrigatório |
| Gráficos interativos (ECharts/Chart.js) carregando | Obrigatório |
| Deploy no Render/Railway | Desejável |

## Critérios de Sucesso da Apresentação

| Critério | Meta |
|:--|:--|
| Slides com narrativa coerente de Growth | Obrigatório |
| Demonstração ao vivo do App | Desejável |
| Tempo de apresentação dentro do limite | Obrigatório |

---

## Plano de Contingência

| Cenário de Risco | Ação Corretiva |
|:--|:--|
| ROC-AUC do XGBoost < 0.65 | Trocar para Random Forest ou reduzir features |
| Modelo muito lento no Frontend/FastAPI | Reduzir `n_estimators` para 100 e usar `joblib` com compressão |
| Deploy no Render/Vercel falhar | Usar Render (free tier) como alternativa |
| Henry não conseguir finalizar a EDA no Dia 1 | Mauricio assume a EDA e o treino do modelo é adiado para Dia 2 à tarde |
| Bug crítico no Web App no Dia 4 | Priorizar as abas 1 e 3 (Painel e Simulador), sacrificar aba 2 (Insights) |
| Dados faltantes no merge das tabelas | Usar `fillna()` com medianas para features numéricas e "desconhecido" para categóricas |
