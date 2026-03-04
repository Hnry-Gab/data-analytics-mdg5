🛠️ 1. Tech Stack
Para focar em Growth, entregar um dashboard interativo e garantir uma arquitetura testável e escalável, a stack foi expandida:
 * Linguagem: Python (com foco em clean code e modularidade).
 * Manipulação de Dados: pandas, numpy.
 * Visualização: plotly (melhor para integrar no Streamlit) ou seaborn.
 * Machine Learning (Clusters e Preditivo): scikit-learn, xgboost ou lightgbm (para propensão e churn).
 * Inferência Causal e NLP: causalml (para Uplift Modeling), nltk ou spacy (para análise de sentimento nos reviews).
 * Deploy/Dashboard: streamlit.
 * Testes e Integração: pytest (para validação de dados) e uso de MCPs como playwright (para testes E2E no frontend) e context7 (para retomar e manter a documentação da stack atualizada).
🔄 2. Flow (Growth, CI & Engineering Focus)
1. Receber Dados (Data Ingestion, Joins & Modularidade)
 * Baixar os múltiplos CSVs do Kaggle.
 * Mapear o esquema e fazer os merges cruciais: customers + orders + order_items + payments + reviews.
 * Expansão: Isolar a lógica de ingestão em módulos independentes para evitar código espaguete e facilitar a futura transição para um banco de dados em nuvem. Adicionar testes unitários básicos para garantir que os joins não dupliquem registros.
2. Tratar Dados (Data Cleaning & Feature Engineering Avançado)
 * Lidar com valores nulos (especialmente datas de entrega).
 * Feature Engineering (Crucial para Growth): Criar novas colunas como tempo de entrega real vs. estimado, Ticket Médio por cliente, tempo de vida do cliente (Lifetime) e Recência da última compra.
 * Expansão: Mapeamento de variáveis de texto. Limpar e tokenizar os textos das avaliações para preparar os dados para algoritmos de Processamento de Linguagem Natural (NLP).
3. Analisar Dados (Growth Analytics & Inferência Causal)
 * Análise de Cohort: Entender a retenção de clientes ao longo dos meses.
 * Matriz RFM (Recência, Frequência, Valor Monetário): A base da inteligência de cliente para e-commerce.
 * Geolocalização: Mapear quais estados possuem maior LTV (Lifetime Value) e onde o custo de frete impacta a conversão.
 * Expansão (Causalidade vs. Correlação): Aplicar técnicas de Uplift Modeling para separar clientes que reagem a incentivos daqueles que comprariam organicamente, protegendo a margem de lucro.
4. Modelagem de Inteligência Avançada (Scikit-Learn, XGBoost & NLP)
 * Aplicar o algoritmo K-Means sobre os dados de RFM para criar clusters automáticos (ex: "Clientes Campeões", "Em Risco", "Novos Clientes Promissores").
 * Expansão (NLP): Aplicar análise de sentimentos e modelagem de tópicos nos reviews para descobrir os motivos exatos de insatisfação por cluster.
 * Expansão (Preditiva): Treinar um modelo de classificação (XGBoost/LightGBM) para prever a probabilidade exata de churn (abandono) de cada cliente nos próximos 30 dias.
5. Captar Insights (Actionable Growth & Forecasting)
 * Traduzir os dados em ações: Ex: "Clientes que sofrem atraso na entrega têm 80% menos chance de recompra. Sugestão: Criar campanha de retenção com cupom de desconto para clientes do cluster 'Em Risco' que tiveram atraso."
 * Expansão: Utilizar modelos de forecasting para prever picos de demanda por região, permitindo que a operação se antecipe a gargalos logísticos.
6. Gerar Dashboard e Interface (Streamlit App & UX/UI)
 * Criar uma aplicação com abas (tabs) modulares:
   * Visão Geral: KPIs de receita e volume de pedidos.
   * Inteligência de Cliente: Gráficos da análise RFM e os clusters preditivos.
   * Alavancas de Growth: Impacto de avaliações (reviews) e frete no faturamento.
 * Expansão (Design System): Desenvolvimento focado em UX/UI, criando um Design System coerente com a cor principal sendo marrom, garantindo contraste, padronização visual e legibilidade executiva.
 * Expansão (Garantia de Qualidade): Implementação de testes automatizados de interface rodando no frontend para garantir que os filtros e componentes do Streamlit funcionem de ponta a ponta.

# Flow
.ralph
fix_plan.md

PRD.md

começo > meio > fim

opus 4.6

## github
main -> PRODUCTION
development -> DEVELOPMENT

branch -> data cleaning;

PR

feat/feature
fix/fix
integration/features_names
chore/doc
refactor/feature
