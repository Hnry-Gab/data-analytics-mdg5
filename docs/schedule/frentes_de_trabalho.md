# Frentes de Trabalho do Projeto Olist

Para garantir uma entrega do mais alto nível técnico e estratégico (focado em negócios), nosso projeto será dividido e atacado simultaneamente nas seguintes frentes de trabalho:

---

## 1. Insights Mais Valiosos dos Dados (A Base Estratégica)
**O que é:** O trabalho investigativo (EDA - Análise Exploratória de Dados) focado em encontrar as raízes dos problemas de negócio da empresa.
**Objetivo da Entrega:** Nenhuma Inteligência Artificial funciona bem sem que um humano tenha entendido o problema primeiro. Esta frente será responsável por vasculhar a base de dados em busca de correlações imperceptíveis a olho nu.
**Exemplos de Entregas:**
*   Descobrir se o tamanho do produto ou a distância ditam os atrasos logísticos na entrega.
*   Encontrar os "Ofensores de Pareto" da rede de Supply Chain (uma minoria de lojistas/transportadoras responsáveis pela grande maioria dos atrasos).
*   Documentar as regras de negócio logísticas que impactam diretamente a retenção de clientes (Growth).

## 2. Dashboard Interativo (Visualização Executiva)
**O que é:** A interface humana de alto nível para observadores e diretores não-técnicos do projeto.
**Objetivo da Entrega:** Tangibilizar milhões de linhas de dados logísticos (CSV) em visuais dinâmicos. Mostrar de forma interativa o acompanhamento das métricas de atraso e gargalos de entrega.
**Exemplos de Entregas:**
*   Construção de um App ou Painel utilizando exclusivamente Frontend/FastAPI (Python).
*   Mapas de calor logístico das rotas do Brasil.
*   Visão global da saúde da operação Olist de acordo com os filtros de Tempo e Vendedor selecionados na tela.
*   Essa frente trabalhará em conjunto com a Frente 3 para criar um dashboard que mostre as métricas vitais de atraso logístico aos envolvidos.

## 3. Modelagem Preditiva (Treinamento e Inferência)
**O que é:** O motor cognitivo do projeto. Transformar os *insights* humanos da fase anterior em um aprendizado de máquina contínuo (Machine Learning).
**Objetivo da Entrega:** Criar o modelo matemático capaz de prever o futuro (classificação) com as regras do passado. 
**Exemplos de Entregas:**
*   Desenvolvimento do *Feature Engineering* (juntar variáveis, normalizar textos e datas).
*   Separação da base de dados (80% Treino / 20% Teste) e execução do Algoritmo Preditivo (XGBoost ou Random Forest) num ambiente Cloud, como Google Colab.
*   Aprovação técnica do Modelo: Comprovar que o algoritmo consegue prever, com alta taxa de acerto, quais pacotes vão atrasar antes mesmo de serem despachados pela Olist.

---

## 🚀 O Extra, Diferencial para Destaque MÁXIMO (Nível Cloudwalk)
### 4. API de Decisão Inteligente (Deploy e Produtização)
**O que é:** Retirar o modelo preditivo construído pelos Cientistas de Dados do ambiente "laboratório" Jupyter Notebook e criar uma ferramenta utilizável pela "Ponta" da operação (os colaboradores reais do E-commerce).
**Objetivo da Entrega:** Mostrar alto potencial de Arquitetura de Software em conjunto com IA. 
**Exemplos Práticos de Aplicação:** 
Um sistema "plugado" no banco de dados em tempo real. Quando um colaborador de Logística na esteira vai despachar um produto crítico (ex: um móvel caro para o interior da Bahia), ele aperta um botão no sistema. O *Backend* consulta silenciosamente o Modelo de Inteligência Artificial treinado (nossa Frente 2) passando as variáveis.
**O Retorno (Inferência ao Vivo):** A API devolve pra tela do colaborador na hora:
> *"Com base no histórico dos últimos 3 anos, se você enviar pela Transportadora Padrão, o risco de atraso desta localidade é de **87%**. Sugerimos a **Transportadora Premium B** para esta rota."*

Isso fecha o ciclo: Do banco de dados sujo ao aplicativo de operação na mão do empregado, usando Inferência de ML construída especificamente para o cenário singular do lojista.

O resultado disso é a redução de cancelamentos e custos estornos, além de um melhor desempenho da operação Olist, alavancando as métricas de Growth da empresa.
