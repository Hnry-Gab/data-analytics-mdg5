# Matriz de Responsabilidades: Força-Tarefa de 4 Dias

Temos **7 membros** e apenas **4 dias** até a entrega final. Como já estamos na Fase 3 (**EDA Nichada**), o projeto a partir de hoje deixa de ser sequencial e passa a ser **paralelo**. 

### Alocação da Força-Tarefa e Perfis (Quinta/Sexta/Sábado/Domingo)
Para entregar as 4 Frentes de Trabalho listadas no arquivo `frentes_de_trabalho.md` em tempo recorde, a equipe foi dividida assim:

*   **Esquadrão Alpha "Insights & ML" (3 Pessoas):** 
    *   **Mauricio:** Líder do Modelo Preditivo (Treinará e afinará o algoritmo XGBoost/Random Forest).
    *   **Henry:** O Detalhista Estatístico (Limpará matematicamente a base, tratará Outliers e achará as Correlações precisas).
    *   **Lucas:** Apoio pesado na manipulação de dados em Pandas e estruturação técnica da base ao lado do Mauricio.
*   **Esquadrão Delta "Painel Visual" (2 Pessoas):** 
    *   **Pablo:** O Monstro do Front-End (Vai fazer o Frontend/FastAPI ficar com cara de sistema profissional, desenhando gráficos e layouts).
    *   **Douglas:** Tem base de IA/Tech. Vai colar no Pablo para garantir que a telinha de *Inputs* do Front-End receba as variáveis corretas para mandar pra IA do Mauricio rodar.
*   **Esquadrão Omega "Negócios / Apresentação" (2 Pessoas):** 
    *   **Anderson e Gabriel:** Os estrategistas. Enquanto os outros 5 esmagam o código, eles mastigam os achados do Henry, traduzem para a liderança, e instalam o "Storytelling" dos Slides focados em como a predição logística evita cancelamentos e alavanca o **Growth/Retenção** de clientes.

## O Histórico do Projeto (Fases Anteriores Concluídas)
Apenas para fins de documentação executiva do encadeamento lógico do time antes de darmos o Sprint final:

| Fase Concluída | Frente 1 (Insights/EDA) | Frente 2 (Dashboard) | Frente 3 (Modelagem ML) | Frente 4 (API/Deploy) |
| :--- | :--- | :--- | :--- | :--- |
| **1. EDA Geral** | **Líder:** Explorou tabelas cruas, achou valores nulos. | *Ouvinte:* Entendeu o negócio e pensou nas telas. | *Apoio:* Avaliou sanidade matemática primária. | *Espera estrutural.* |
| **2. Escolha de Nicho**| **Líder:** Cruzou dados e bateu o martelo no foco (Logística e Reviews). | **Líder:** Idealizou a *wireframe* focada nos contextos. | *Ouvinte:* Avaliou viabilidade de treinar ML baseada no nicho. | *Espera arquitetural*. |

---

## O Cronograma de Sobrevivência (Dia a Dia - Prazo Final)

| Fase Atual | Dia do Projeto (Restante) | Esquadrão 1: Insights & ML (Mauricio, Henry e Lucas) | Esquadrão 2: Front/App (Pablo e Douglas) | Esquadrão 3: Negócios (Anderson e Gabriel) |
| :--- | :--- | :--- | :--- | :--- |
| **EDA Nichada & Limpeza** | **DIA 1 (Quinta)** | **Henry e Lucas** atacam o Pandas. Fazem os `merges`, limpam as datas e geram os primeiros gráficos de correlação. **Mauricio** revisa a lógica. | **Pablo** sobe o servidor local do Frontend/FastAPI e desenha o App. **Douglas** estuda como plugar a predição futura. | Olham os gráficos sujos do Henry e começam a desenhar o esqueleto estratégico do PPT/Slides. |
| **Feature Engineering & ML** | **DIA 2 (Sexta)** | **Henry** fecha quais 5 colunas são o "Gabarito". **Mauricio e Lucas** recebem os dados limpos, quebram em 80/20 e treinam o primeiro Modelo de Rascunho. | **Pablo e Douglas** recebem o CSV limpo, conectam no Frontend/FastAPI e botam os gráficos originais para rodarem oficialmente na Tela 1. | Mapeiam os gargalos lógicos (Ex: Qual estado dá mais dor de cabeça) e montam a narrativa do "Tamanho do Problema". |
| **O Treinamento Final** | **DIA 3 (Sábado)** | **Mauricio** calibra a Inteligência Artificial e dá `export` do robô final num arquivo `.pkl`. Depois, senta com o Douglas para estruturar o backend. | O Dashboard está vivo. **Douglas e Mauricio** estruturam o backend do sistema e **Pablo** finaliza o botão mágico "Prever Transportadora" na Tela 3. | Extraem prints matadores do Painel do Pablo e encaixam tudo dentro dos Slides finais da apresentação. |
| **Apresentação e Deploy** | **DIA 4 (Domingo)** | **Manhã:** Refinam explicações técnicas. **Tarde/Noite:** Ensaiam com todos para a apresentação aos professores. | **Manhã:** Pablo sobe o deploy; Douglas caça bugs. **Tarde/Noite:** Ensaiam com todos para a apresentação aos professores. | **Manhã:** Roteirizam o espetáculo. **Tarde/Noite:** Todos os 7 membros ensaiam exaustivamente a narrativa de Apresentação Final. |

---

### Resumo do Fluxo do Produto:
1.  **Frente 1** mastiga e afunila os dados para o negócio.
2.  **Frente 2** transforma esses dados históricos mastigados em um produto visual (App).
3.  **Frente 3** pega esses dados matematicamente ajustados e ensina o Robô a pensar (IA).
4.  **Frente 4** pega esse Robô treinado e embute em uma interface para uso em produção contínua (API).
