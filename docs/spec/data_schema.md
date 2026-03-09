# Schema de Dados — DataFrame Final Unificado

> Estrutura consolidada do dataset `dataset_unificado_v1.csv` utilizado pelo pipeline de ML e pelo servidor MCP.

---

## Tabelas Envolvidas nos Merges

```
olist_orders_dataset         (Base principal — contém as datas de entrega)
  ├── olist_customers_dataset  (JOIN via customer_id — traz estado/CEP do cliente)
  ├── olist_order_items_dataset (JOIN via order_id — traz preço, frete, produto, vendedor)
  │     ├── olist_products_dataset (JOIN via product_id — traz peso, dimensões, categoria)
  │     └── olist_sellers_dataset  (JOIN via seller_id — traz estado/CEP do vendedor)
  ├── olist_order_payments_dataset (JOIN via order_id — tipo de pagamento principal)
  └── olist_geolocation_dataset   (JOIN via zip_code_prefix — traz lat/lng para distância)
```

## Filtro Obrigatório Antes do Merge

- Manter apenas pedidos com `order_status == 'delivered'`
- Remover linhas onde `order_delivered_customer_date` é `NaN` (pacotes nunca entregues)
- Deduplicação por `order_id` (manter primeiro item quando há múltiplos itens por pedido)

---

## Variável Alvo (Target / Y)

| Coluna | Tipo | Fórmula |
|:--|:--|:--|
| `foi_atraso` | `Int64` (0 ou 1) | `1` se `order_delivered_customer_date > order_estimated_delivery_date`, senão `0` |

**Distribuição real no dataset:** ~93% classe 0 (no prazo) / ~7% classe 1 (atrasou) — Dataset desbalanceado.

---

## Colunas do Dataset Final (59 colunas)

### Identificadores e Status

| # | Coluna | Tipo | Origem | Descrição |
|---|:--|:--|:--|:--|
| 1 | `order_id` | string | orders | Identificador único do pedido |
| 2 | `customer_id` | string | orders | ID do cliente neste pedido |
| 3 | `order_status` | string | orders | Status do pedido (sempre `delivered` após filtro) |
| 4 | `customer_unique_id` | string | customers | ID permanente do cliente na plataforma |
| 5 | `order_item_id` | Int64 | order_items | Número sequencial do item no pedido |
| 6 | `product_id` | string | order_items | ID do produto |
| 7 | `seller_id` | string | order_items | ID do vendedor |

### Timestamps

| # | Coluna | Tipo | Origem | Descrição |
|---|:--|:--|:--|:--|
| 8 | `order_purchase_timestamp` | datetime | orders | Momento da compra |
| 9 | `order_approved_at` | datetime | orders | Momento da aprovação do pagamento |
| 10 | `order_delivered_carrier_date` | datetime | orders | Momento da postagem na transportadora |
| 11 | `order_delivered_customer_date` | datetime | orders | Momento da entrega ao cliente |
| 12 | `order_estimated_delivery_date` | datetime | orders | Prazo estimado informado ao cliente |
| 13 | `shipping_limit_date` | datetime | order_items | Prazo para o vendedor despachar |

### Dados Financeiros

| # | Coluna | Tipo | Origem | Descrição |
|---|:--|:--|:--|:--|
| 14 | `price` | Float64 | order_items | Valor do produto |
| 15 | `freight_value` | Float64 | order_items | Valor do frete |

### Dados do Produto

| # | Coluna | Tipo | Origem | Descrição |
|---|:--|:--|:--|:--|
| 16 | `product_category_name` | string | products | Categoria do produto (pt-BR) |
| 17 | `product_name_lenght` | Float64 | products | Caracteres no nome do produto |
| 18 | `product_description_lenght` | Float64 | products | Caracteres na descrição |
| 19 | `product_photos_qty` | Float64 | products | Número de fotos do anúncio |
| 20 | `product_weight_g` | Float64 | products | Peso em gramas |
| 21 | `product_length_cm` | Float64 | products | Comprimento em cm |
| 22 | `product_height_cm` | Float64 | products | Altura em cm |
| 23 | `product_width_cm` | Float64 | products | Largura em cm |

### Dados Geográficos (Originais)

| # | Coluna | Tipo | Origem | Descrição |
|---|:--|:--|:--|:--|
| 24 | `customer_zip_code_prefix` | Int64 | customers | CEP do cliente (5 dígitos) |
| 25 | `customer_city` | string | customers | Cidade do cliente |
| 26 | `customer_state` | string | customers | UF do cliente |
| 27 | `seller_zip_code_prefix` | Int64 | sellers | CEP do vendedor (5 dígitos) |
| 28 | `seller_city` | string | sellers | Cidade do vendedor |
| 29 | `seller_state` | string | sellers | UF do vendedor |
| 30 | `seller_lat` | Float64 | geolocation | Latitude do vendedor |
| 31 | `seller_lng` | Float64 | geolocation | Longitude do vendedor |
| 32 | `customer_lat` | Float64 | geolocation | Latitude do cliente |
| 33 | `customer_lng` | Float64 | geolocation | Longitude do cliente |

### Dados de Pagamento

| # | Coluna | Tipo | Origem | Descrição |
|---|:--|:--|:--|:--|
| 34 | `tipo_pagamento_principal` | string | payments | Tipo de pagamento principal usado |

### Variável Alvo e Métricas de Atraso

| # | Coluna | Tipo | Origem | Descrição |
|---|:--|:--|:--|:--|
| 35 | `dias_diferenca` | Int64 | engenharia | Diferença em dias entre entrega real e estimada |
| 36 | `foi_atraso` | Int64 | **TARGET** | 1 = atrasou, 0 = no prazo |
| 37 | `dias_atraso` | Int64 | engenharia | Dias de atraso (0 se no prazo) |

### Features Engenheiradas — Físicas/Financeiras

| # | Coluna | Tipo | Fórmula | Descrição |
|---|:--|:--|:--|:--|
| 38 | `volume_cm3` | Float64 | `length * height * width` | Volume do pacote |
| 39 | `frete_ratio` | Float64 | `freight_value / price` | Proporção frete/preço |
| 40 | `valor_total_pedido` | Float64 | `price + freight_value` | Valor total do pedido |
| 41 | `total_itens_pedido` | Int64 | contagem por order_id | Itens no pedido |
| 42 | `ticket_medio_alto` | Int64 | threshold sobre valor | Flag de ticket alto |

### Features Engenheiradas — Temporais

| # | Coluna | Tipo | Fórmula | Descrição |
|---|:--|:--|:--|:--|
| 43 | `velocidade_lojista_dias` | Float64 | `(carrier_date - approved_at).days` | Velocidade de despacho do vendedor |
| 44 | `velocidade_transportadora_dias` | Float64 | `(delivered_date - carrier_date).days` | Tempo da transportadora |
| 45 | `dia_semana_compra` | Int64 | `purchase_timestamp.dayofweek` | Dia da semana (0=Seg, 6=Dom) |
| 46 | `compra_fds` | Int64 | `dia_semana_compra >= 5` | Flag de compra no fim de semana |
| 47 | `mes_compra` | Int64 | `purchase_timestamp.month` | Mês da compra |
| 48 | `hora_compra` | Int64 | `purchase_timestamp.hour` | Hora da compra |
| 49 | `ano_compra` | Int64 | `purchase_timestamp.year` | Ano da compra |
| 50 | `ano` | Int64 | `purchase_timestamp.year` | Ano (redundante) |
| 51 | `trimestre` | Int64 | `purchase_timestamp.quarter` | Trimestre |
| 52 | `ano_mes` | string | `YYYY-MM` | Período ano-mês |
| 53 | `ano_trimestre` | string | `YYYY-QN` | Período ano-trimestre |

### Features Engenheiradas — Geográficas/Rota

| # | Coluna | Tipo | Fórmula | Descrição |
|---|:--|:--|:--|:--|
| 54 | `rota_interestadual` | Int64 | `seller_state != customer_state` | Flag de rota interestadual |
| 55 | `distancia_haversine_km` | Float64 | Haversine(seller, customer) | Distância geodésica em km |
| 56 | `seller_regiao` | string | primeiro dígito do CEP | Macro-região do vendedor |
| 57 | `customer_regiao` | string | primeiro dígito do CEP | Macro-região do cliente |
| 58 | `destino_tipo` | string | classificação da cidade | Tipo de destino (capital, interior, etc.) |

### Features Engenheiradas — Vendedor

| # | Coluna | Tipo | Fórmula | Descrição |
|---|:--|:--|:--|:--|
| 59 | `historico_atraso_seller` | Float64 | taxa histórica de atraso | Histórico de atrasos do vendedor |

---

## Estatísticas da Base

| Métrica | Valor |
|:--|:--|
| Total de linhas no dataset | ~109.637 |
| Pedidos entregues (após filtro) | 96.476 |
| Pedidos no prazo (classe 0) | 89.941 (93,22%) |
| Pedidos atrasados (classe 1) | 6.535 (6,77%) |
| Colunas totais | 59 |
| Features usadas pelo modelo CatBoost V5 | 19 (15 numéricas + 4 categóricas) |

---

## Validação

```bash
python -c "from olist_mcp.cache import DataStore; df = DataStore.df(); print(f'Shape: {df.shape}'); print(f'Columns: {len(df.columns)}')"
```
