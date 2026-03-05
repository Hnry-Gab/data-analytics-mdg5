# Cronograma de Análise de Dados e Modelagem Preditiva

Este cronograma serve como o "GPS" analítico do nosso projeto usando os dados do Olist. Ele descreve o passo a passo exato desde o primeiro contato cego com as tabelas até o *deploy* do modelo preditivo que vai antecipar problemas logísticos e retenção.

---

### Fase 1: Conhecimento e Exploração Global
**1. EDA Geral (Análise Exploratória de Dados)**
*   **O que é?** O primeiro mergulho cego no banco de dados para entender "o que o dataset nos oferece?".
*   **Ações:** Conferir quantas linhas, colunas, valores nulos, os tipos de dados (Datas, Textos, Números) e cruzar de maneira abrangente. Como o negócio da Olist opera em seu panorama histórico de anos.

**2. Escolha de Nicho / Contexto (Business Understanding)**
*   **O que é?** A filtragem do ruído perante os achados da etapa 1. Diante do que o dataset entrega com qualidade, o que há de mais valioso financeiramente para prever?
*   **Ações:** Nosso grupo já realizou esta etapa e decidiu afunilar os mundos para uma frente principal: **Previsão de Atraso Logístico focada em Growth (Retenção e Custo)**. Descartamos "Churn Clássico", "MKT Basket" e "Review Score", para concentrar o prazo curto numa entrega impecável de um único modelo de alto valor.

---

### Fase 2: Exploração aprofundada (Onde estamos hoje)
**3. EDA Nichada**
*   **O que é?** Uma nova Análise Exploratória, mas agora focando exclusivamente nos nichos escolhidos, buscando os fatores causadores da dor (Atraso/Nota 1) nos contextos.
*   **Ações:** Validar as Hipóteses listadas no arquivo [Fase EDA Nichada](fase_eda_nichada.md). Vamos gerar Heatmaps, Gráficos de Dispersão e realizar os Testes de [Correlação de Pearson](../algorithms/explicacao_correlacao_pearson.md) focando principalmente nos relacionamentos com as tabelas de Geolocation.

---

### Fase 3: Engenharia e Tratamento (Data Preparation)
**4. Normalização e Tratamento dos Atributos Selecionados**
*   **O que é?** A "limpeza" dos dados para que o computador (os algoritmos) extraiam valor e não erro. Machine Learning exige dados estruturados e limpos.
*   **Ações:** Transformar datas em variáveis inteiras (Ex: "Faltam X Dias"), transformar Categoria de Texto em ID Numérico (Encoding), deletar *Outliers* bizarros (pedidos com "500 dias de atraso" no sistema, CEPs inexistentes), imputar dados faltantes (Null).

**5. Fechamento de Insights (Interpretação da EDA Pós-Limpeza)**
*   **O que é?** A consolidação humana e de negócio após a limpeza final. Analisar a versão polida dos atributos e tirar a decisão final sobre o que diz cada número.
*   **Ações:** Montar o painel/dashboard final (Em Python/Frontend/FastAPI) com as respostas exatas para: "Sim, os atrasos gerados pela transportadora Y na região Norte estão custando Z mil reais em perda de retenção/Growth".

**6. Formulação das *Features* mais Valiosas (Feature Engineering)**
*   **O que é?** Escolher ou CRIAR as colunas exatas (a partir de contas ou da união de duas variáveis) que serão entregues como o "Gabarito de Treinamento" final para o Robô de Machine Learning aprender sozinho.
*   **Ações:** Talvez a Distância Absoluta + Peso juntas com o Histórico do Vendedor criem sozinhas o Coeficiente perfeito para o Atraso; Deixaremos apenas as *"Features Vencedoras"*, excluindo atributos ruins (com Correlação 0 de Pearson).

---

### Fase 4: O Machine Learning (Modelagem Preditiva)
**7. Algoritmo Preditivo: O Treino (80%) e Inferência (20%)**
*   **O que é?** A execução da Inteligência Artificial em Random Forest ou algoritmos baseados em Gradient Boosting (XGBoost).
*   **Ações:** Separar nossa base de milhões de linhas da Olist em:
    *   **Treino (80%):** Daremos ao robô as Features selecionadas e diremos a ele o resultado original ("Isto aqui atrasou 5 dias"). Ele aprenderá todas as equações secretas ali durante horas processando.
    *   **Teste / Inferência (20%):** Esconderemos do robô o Prazo e o status do pacote. Daremos só as variáveis (Peso, Localização, etc) e diremos: "Preveja agora se isso vai atrasar!". Se ele acertar ou chegar muito perto do fato de ter atrasado, testificamos e o modelo preditivo foi um Sucesso de Negócio.
