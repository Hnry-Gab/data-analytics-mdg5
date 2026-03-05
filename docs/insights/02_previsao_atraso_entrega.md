# 02 - Previsão de Atraso na Entrega

## O Objetivo e Motivação
Na Olist, como a logística é complexa em um país de dimensões continentais como o Brasil, o cumprimento do prazo de entrega (`order_estimated_delivery_date` vs `order_delivered_customer_date`) afeta tudo, do cancelamento às métricas do vendedor. Este modelo tem o objetivo de prever:
**Qual o risco de um pedido chegar atrasado assim que ele for emitido?**

O grande ganho prático é logístico. Prever isso antes mesmo do vendedor enviar sua carga para a transportadora permite ajustar a malha (trocar o operador ou fretar vias rápidas) e notificar o usuário para que a expectativa seja ajustada. Reduz cancelamentos e ações judiciais.

## Tabela de Construção Preditiva

Para montar (Merge) os dados e usar em modelos como Random Forest ou XGBoost para classificação binária:

**Tabelas e Variáveis Essenciais:**

1.  **A Base Logística (`olist_orders` e `olist_geolocation`)**
    *   *A meta*: O pacote demorou ou não? (Você vai criar a variável target a partir das diferenças das datas na tabela de ordens `olist_orders_dataset`).
    *   *CEP (Zip_code)*: Calcular a distância Haversine em Geocalização entre o vendedor (`olist_sellers`) e o cliente final (`olist_customers`) usando o `olist_geolocation`. Uma feature fundamental para entender rotas de risco e áreas longínquas.
2.  **A Base Operacional (`olist_products` e `olist_order_items`)**
    *   *Variáveis Chave*: Tamanho em centímetros do pacote e seu peso (`weight_g`). Produtos fora do padrão ou muito pequenos podem ser negligenciados pelo frete, gerando atraso por manuseio extra.
3.  **Vendedores (`olist_sellers`)**
    *   *Feature Engineering Crítica:* Calcular um *Score de Confiabilidade* histórico do vendedor. Quantos dias ele leva, em média, desde a aprovação do pedido até postar no correio? Ele trabalha sábados ou atrasa às segundas-feiras?

### Por Que É Ideal para a Equipe?
É o tipo de projeto que tem impacto financeiro absurdo e valor imediato numa entrevista de portfólio de Ciência de Dados. Tratar outliers no preço do frete, calcular distâncias geográficas e mapear desempenho de parceiros de entrega num país gigante é real e valioso.
