# Especificação do Projeto — Olist Logistics Growth

> Este arquivo é a fonte de verdade para qualquer agente de IA ou desenvolvedor que trabalhar neste repositório.
> Se houver conflito entre este arquivo e qualquer outro, **este prevalece**.

---

## Escopo

Construir uma aplicação web unificada (Streamlit) que analise dados históricos de logística do e-commerce Olist e preveja, **em tempo real**, se um novo pedido tem risco de atrasar, permitindo ações preventivas de Growth e retenção.

## Prazo

**4 dias corridos** (Quinta a Domingo).

## Equipe (7 pessoas / 3 Esquadrões)

| Esquadrão | Membros | Responsabilidade |
|:--|:--|:--|
| **Alpha** (Insights & ML) | Mauricio, Henry, Lucas | EDA, Feature Engineering, treinamento do XGBoost |
| **Delta** (Painel Visual) | Pablo, Douglas | Streamlit App (3 abas), gráficos Plotly |
| **Omega** (Negócios) | Anderson, Gabriel | Narrativa de negócio, slides, apresentação |

## Entrega Final

Uma Aplicação Web Streamlit com **3 abas**:

1. **Painel Gerencial (O Passado):** Dashboard interativo com filtros por data, estado e categoria. Mapa de calor logístico do Brasil.
2. **Insights Valiosos (A Inteligência):** Key Results e descobertas de negócio em formato texto + gráficos de apoio.
3. **Motor de Predição (O Futuro):** Formulário "Simulador de Nova Venda" onde o usuário insere CEP, produto e categoria. O modelo de ML retorna a probabilidade de atraso e sugere ações preventivas.

## Deploy

- O deploy do Frontend HTML e da API Backend/MCP será realizado de forma integral via **VPS**.

---

## ⛔ O que NÃO será implementado neste projeto

Os itens abaixo **não fazem parte do escopo** e qualquer agente de IA deve **ignorá-los**:

- Análise RFM (Recência, Frequência, Valor Monetário)
- Previsão de Churn (inatividade >180 dias)
- Customer Lifetime Value (CLV / Gamma-Gamma / BG-NBD)
- NLP / Análise de Sentimento em Reviews
- Inferência Causal / Uplift Modeling
- Market Basket Analysis (Apriori / Cross-sell)
- Testes E2E com Playwright
- Mais de 3 abas no Dashboard
