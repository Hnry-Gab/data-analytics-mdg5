# Dia 2 (Sexta-feira): Feature Engineering e o Primeiro Rascunho da IA

**Fase do Cronograma:** Seleção de Variáveis (Features) e Treinamento do Modelo Preditivo (Baseline).
**Objetivo do Dia:** Finalizar as descobertas de negócios com dados reais, gerar os primeiros gráficos originais da Olist no painel e ter um robô (Machine Learning) básico funcionando e conseguindo prever alguma coisa.

---

### 🐺 Esquadrão Alpha (Insights & ML)
**Membros:** Mauricio, Henry e Lucas.
*   **O que farão hoje:**
    *   **Henry:** Baseado nos testes de quinta, vai bater o martelo e listar qual é o "Gabarito" de colunas: Quais são as 5 ou 6 variáveis (features) com maior impacto de causar atraso logístico na vida real (ex: Estado de destino, Valor de Frete, Volume da Caixa).
    *   **Mauricio e Lucas:** Pegam essas 5/6 colunas de Ouro do Henry, dividem os dados limpos em uma base de Treino (80%) e uma base de Teste (20%).
    *   **Mauricio:** Treina a primeira versão grossa do código de algoritmo (o *baseline* em Random Forest ou XGBoost) para ver se ele consegue prever minimamente os atrasos em cima dos 20% de teste.
*   **Entregável do Fim do Dia:** O primeiro modelo de Rascunho da IA treinado e com métricas superficiais de acerto rodando no Jupyter/Colab.

---

### 🦅 Esquadrão Delta (Painel Visual/App)
**Membros:** Pablo e Douglas.
*   **O que farão hoje:**
    *   Apagam os "dados falsos" que usaram na quinta-feira.
    *   Recebem o CSV totalmente limpo do Henry (Esquadrão Alpha) e conectam o código puramente nesse arquivo real.
    *   **Pablo e Douglas:** Codificam os gráficos gerenciais da Olist na "Tela 1" do App. Se sobrar tempo, formatam visualmente a "Tela 2" (aba de Insights Textuais) para receber as conclusões finais que o Esquadrão Omega for soltando.
*   **Entregável do Fim do Dia:** As primeiras abas do Dashboard Web oficialmente funcionando e demonstrando a verdade crua do banco de dados na tela, através de gráficos interativos (ECharts/Chart.js).

---

### 🦉 Esquadrão Omega (Negócios & Storytelling)
**Membros:** Anderson e Gabriel.
*   **O que farão hoje:**
    *   Com a confirmação do Henry sobre "quais são as variáveis que mais causam atrasos", eles traduzem isso para a linguagem corporativa.
    *   Iniciam o preenchimento maciço do PPT com as narrativas: Tamanho do problema de Supply Chain da Olist.
    *   Estratégia prática: Como a Olist pode usar a predição desenvolvida pelo Mauricio para atuar proativamente na retenção de usuários.
*   **Entregável do Fim do Dia:** Narrativa estratégica concluída e rascunho dos textos principais para os slides preenchidos.
