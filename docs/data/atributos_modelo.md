# Insights do Dataset: Guia de Features (Atributos) para o Treinamento do Modelo Logístico

Este documento lista formalmente o arsenal de *Features* (variáveis independentes) que as tabelas originais da Olist possuem, para serem cruzadas pelo Esquadrão Alpha contra a nossa Variável Alvo (`Foi_Atraso`). O segredo do XGBoost não é apenas usar as colunas puras, mas a criação de novas a partir destas (Feature Engineering).

---

## 📦 1. Atributos Físicos e de Volume
**Origem:** Tabela `olist_products_dataset`
**A hipótese de negócio:** Quanto maior, mais pesado ou de categoria atípica o pacote for, maior a dificuldade da transportadora em alocar espaço nos caminhões, resultando em possíveis taxas maiores de atraso por manuseio.

*   `product_weight_g`: Peso bruto do item.
*   `product_category_name`: A categoria (ex: "moveis_decoracao" vs "telefonia") possui influência inata no prazo real?
*   **Feature Criada (Volume Cúbico):** Multiplicação direta geométrica: `product_length_cm` * `product_height_cm` * `product_width_cm`.

## 💸 2. Atributos Financeiros e Relevância
**Origem:** Tabelas `olist_order_items_dataset` e `olist_orders_dataset`
**A hipótese de negócio:** Produtos com tickets muito altos recebem prioridade logística dos próprios lojistas na fila de embalagem? Pagar um frete proporcionalmente alto garante imunidade contra SLA não cumprido?

*   `price`: Valor bruto do produto (Ticket).
*   `freight_value`: O que o cliente pagou de frete final.
*   **Feature Criada (Frete/Ticket Ratio):** A divisão simples `freight_value` / `price`. Se o cliente comprou uma caneta de R$ 2 e pagou R$ 40 de frete na região Norte (Índice 20x), a tolerância ao atraso é quase nula. O modelo deve flagrar isso.

## ⏱️ 3. Atributos Temporais da Cadeia de Suprimentos
**Origem:** Tabela de Tempo Real `olist_orders_dataset`
**A hipótese de negócio:** Como isolar se o atraso final na porta do cliente foi culpa da rodovia brasileira ou da lerdeza interna do Seller (Lojista) em montar a caixa e levar no correio? Efeitos de fim de semana geram cascata de paradas?

*   **Feature Criada (Velocidade do Lojista):** `order_delivered_carrier_date` - `order_approved_at`. O tempo em dias que o pedido demorou para sair da mão do dono da loja da Olist e ser finalmente bipado pela caminhonete dos correios (Lead Time Interno).
*   **Feature Criada (Efeito Sazonal / Final de Semana):** O Machine Learning deve receber a extração do *Dia da Semana* do campo `order_purchase_timestamp` (0=Segunda, 6=Domingo). Pedidos confirmados na sexta-feira à noite tendem a encalhar nos pátios no final de semana?

## 🗺️ 4. Atributos Geográficos Puros (A Rota Logística)
**Origem:** Cruzamento `olist_customers`, `olist_sellers` acompanhado do `olist_geolocation`
**A hipótese de negócio:** Pedidos cruzando fronteiras estaduais, rotas com falta de motoristas parceiros ou distâncias colossais em rotas do Norte/Nordeste ditam as estatísticas do SLA na vida real.

*   **Feature Criada (Rota Interestadual Boleana):** 1 se o `seller_state` for diferente de `customer_state`, caso contrário 0. O pacote cruzará divisas (ICMS, blitze fiscais) ou ficará na mesma unidade da federação?
*   **Feature Criada (Distância Haversine):** Aproveitando a tabela `geolocation`, será calculado a quilometragem exata (linha reta) entre o lat/long do Armazém do lojista (`seller`) até a casa do cliente (`customer`). Esta costuma ser a Feature Rei disparada no XGBoost em predições logísticas complexas.
