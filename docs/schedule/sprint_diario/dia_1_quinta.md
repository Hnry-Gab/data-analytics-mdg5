# Dia 1 (Quinta-feira): EDA Nichada e Preparação da Base

**Fase do Cronograma:** Limpeza de Dados e Análise Exploratória (EDA) Focada em Logística.
**Objetivo do Dia:** Transformar os CSVs originais cheios de ruído em uma base limpa e unificada, enquanto as outras frentes preparam a estrutura visual e de negócios.

---

### 🐺 Esquadrão Alpha (Insights & ML)
**Membros:** Mauricio, Henry e Lucas.
*   **O que farão hoje:**
    *   **Henry e Lucas:** Vão colocar a mão pesada no Pandas. A missão de hoje é fazer os `merges` corretos entre as tabelas de Pedidos, Itens, Produtos e Localização. Precisam tratar variáveis de data (calcular a diferença de dias entre a data estimada e a data real de entrega para criar a coluna alvo "Foi_Atraso").
    *   **Henry:** Começa a rodar as primeiras Correlações de Pearson para descobrir, por exemplo, se a distância afeta o atraso.
    *   **Mauricio:** Faz a revisão lógica do código para garantir que as bases geradas não tenham vazamento de dados (*data leakage*) e que estarão perfeitamente desenhadas para o treinamento do modelo de ML amanhã.
*   **Entregável do Fim do Dia:** Um (ou mais) arquivos CSV "limpos" (ex: `dataset_limpo_v1.csv`) salvos na máquina, prontos para a Feature Engineering.

---

### 🦅 Esquadrão Delta (Painel Visual/App)
**Membros:** Pablo e Douglas.
*   **O que farão hoje:**
    *   **Pablo:** Inicia o projeto Full-Stack. Cria o arquivo `app.py`, configura o servidor local e desenha o esqueleto completo das 3 telas/abas do aplicativo (Dashboard Histórico, Insights, Simulador de Predição).
    *   **Douglas:** Como o CSV real ainda está sendo mastigado pelo Alpha, ele ajuda o Pablo gerando "dados falsos" (mockados) para as telas já terem algum gráfico de teste rodando. Estuda a arquitetura de como o Frontend/FastAPI receberá o modelo preditivo no futuro.
*   **Entregável do Fim do Dia:** A interface do Frontend/FastAPI rodando localmente no navegador, sem erros de código, aguardando apenas serem "plugadas" aos dados reais.

---

### 🦉 Esquadrão Omega (Negócios & Storytelling)
**Membros:** Anderson e Gabriel.
*   **O que farão hoje:**
    *   Ficam "corujando" os primeiros gráficos sujos ou informações que o Henry exportar do Pandas (ex: "tem muito pedido pro RJ atrasado").
    *   Começam a rabiscar a estrutura de Slides/PPT da apresentação final.
    *   Definem qual será a "dor" atacada na narrativa: Por que atrasos destroem o Growth e a Retenção da Olist?
*   **Entregável do Fim do Dia:** O "Esqueleto" (índice) pronto.
