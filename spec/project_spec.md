# Especificação do Projeto — Olist Logistics Growth

> Este arquivo é a fonte de verdade para qualquer agente de IA ou desenvolvedor que trabalhar neste repositório.
> Se houver conflito entre este arquivo e qualquer outro, **este prevalece**.

---

## Escopo

Construir uma aplicação web Full-Stack (Frontend Javascript + Backend Python FastAPI) que analise dados históricos de logística do e-commerce Olist e preveja, **em tempo real**, se um novo pedido tem risco de atrasar, permitindo ações preventivas de Growth e retenção. Também deve expor um servidor MCP para integração com Agentes IA externos.

## Prazo

**4 dias corridos** (Quinta a Domingo).

## Equipe (7 pessoas / 3 Esquadrões)

| Esquadrão | Membros | Responsabilidade |
|:--|:--|:--|
| **Alpha** (Insights & ML) | Mauricio, Henry, Lucas | EDA, Feature Engineering, treinamento do XGBoost |
| **Delta** (Painel Visual) | Pablo, Douglas | UI em HTML/CSS/JS, API FastAPI, Servidor MCP |
| **Omega** (Negócios) | Anderson, Gabriel | Narrativa de negócio, slides, apresentação |

## Entrega Final

Uma Aplicação Web Full-Stack dividida em:

**Frontend (Client-Side):**
1. **Página Gerencial (O Passado):** Dashboard web interativo com filtros por data, estado e categoria.
2. **Página de Insights (A Inteligência):** Key Results e descobertas de negócio em formato HTML dinâmico.
3. **Página do Simulador (O Futuro):** Formulário web onde o usuário insere CEP, produto e categoria, acionando a API.

**Backend (Server-Side):**
- **Olist API (FastAPI):** Recebe requisições JSON do frontend, invoca o modelo XGBoost, calcula o risco de atraso (0 a 100%) e retorna os resultados.
- **Olist MCP:** Permite que IAs parceiras consultem o motor preditivo e bases de dados do Olist Logistics.

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
