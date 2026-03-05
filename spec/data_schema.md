# Schema de Dados — DataFrame Final para Treinamento

> Este documento define o DataFrame unificado que o Esquadrão Alpha deve construir após os merges das tabelas Olist.

---

## Tabelas Envolvidas nos Merges

```
olist_orders_dataset         (Base principal — contém as datas de entrega)
  ├── olist_customers_dataset  (JOIN via customer_id — traz estado/CEP do cliente)
  ├── olist_order_items_dataset (JOIN via order_id — traz preço, frete, produto, vendedor)
  │     ├── olist_products_dataset (JOIN via product_id — traz peso, dimensões, categoria)
  │     └── olist_sellers_dataset  (JOIN via seller_id — traz estado/CEP do vendedor)
  └── olist_geolocation_dataset   (JOIN via zip_code_prefix — traz lat/lng para distância)
```

## Filtro Obrigatório Antes do Merge

- Manter apenas pedidos com `order_status == 'delivered'`
- Remover (dropar) linhas onde `order_delivered_customer_date` é `NaN` (pacotes nunca entregues)

---

## Variável Alvo (Target / Y)

| Coluna | Tipo | Fórmula |
|:--|:--|:--|
| `foi_atraso` | `int` (0 ou 1) | `1` se `order_delivered_customer_date > order_estimated_delivery_date`, senão `0` |

**Distribuição real no dataset:** ~93% classe 0 (no prazo) / ~7% classe 1 (atrasou) → Dataset desbalanceado.

---

## Features Candidatas (X)

### Diretas (vindas das tabelas originais)
| Feature | Origem | Tipo |
|:--|:--|:--|
| `product_weight_g` | products | numérica |
| `price` | order_items | numérica |
| `freight_value` | order_items | numérica |
| `product_category_name` | products | categórica (encoding) |
| `customer_state` | customers | categórica (encoding) |
| `seller_state` | sellers | categórica (encoding) |

### Criadas (Feature Engineering pelo Esquadrão Alpha)
| Feature | Fórmula | Tipo |
|:--|:--|:--|
| `volume_cm3` | `product_length_cm * product_height_cm * product_width_cm` | numérica |
| `frete_ratio` | `freight_value / price` | numérica |
| `velocidade_lojista_dias` | `(order_delivered_carrier_date - order_approved_at).days` | numérica |
| `dia_semana_compra` | `order_purchase_timestamp.dayofweek` (0=Seg, 6=Dom) | numérica |
| `rota_interestadual` | `1` se `seller_state != customer_state`, senão `0` | binária |
| `distancia_haversine_km` | Cálculo via lat/lng do geolocation (seller → customer) | numérica |

---

## Estatísticas da Base

| Métrica | Valor |
|:--|:--|
| Total de pedidos entregues | 96.476 |
| Pedidos no prazo (classe 0) | 89.941 (93,22%) |
| Pedidos atrasados (classe 1) | 6.535 (6,77%) |
