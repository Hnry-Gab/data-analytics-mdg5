# [ALPHA-01] Merge das Tabelas e Criação do DataFrame Unificado

**Responsável:** Henry, Lucas
**Dia:** 1 (Quinta-feira)
**Prioridade:** 🔴 Crítica (bloqueia todo o projeto)
**Branch:** `feat/alpha-01-merge-tabelas`

---

## Descrição

Realizar o JOIN sequencial das tabelas CSV originais para criar um DataFrame Master unificado contendo todas as informações necessárias para a EDA e o modelo de ML.

### Passo a Passo

1. Carregar `olist_orders_dataset.csv` como base principal.
2. Filtrar apenas pedidos com `order_status == 'delivered'`.
3. Remover linhas onde `order_delivered_customer_date` é `NaN`.
4. JOIN com `olist_customers_dataset` via `customer_id` → traz `customer_state`, `customer_zip_code_prefix`.
5. JOIN com `olist_order_items_dataset` via `order_id` → traz `price`, `freight_value`, `seller_id`, `product_id`.
6. JOIN com `olist_products_dataset` via `product_id` → traz `product_weight_g`, dimensões e `product_category_name`.
7. JOIN com `olist_sellers_dataset` via `seller_id` → traz `seller_state`, `seller_zip_code_prefix`.
8. Converter todas as colunas de data para `datetime`.
9. Salvar o resultado como `dataset_unificado_v1.csv`.

### Referências
- `spec/data_schema.md` → Schema completo do DataFrame final
- `docs/data/dicionario_dados.md` → Descrição de cada coluna

## Critério de Aceite

- [ ] DataFrame unificado com todas as colunas listadas em `spec/data_schema.md`
- [ ] Sem linhas duplicadas por `order_id`
- [ ] Colunas de data convertidas para `datetime`
- [ ] Apenas pedidos `delivered` (nenhum `canceled`, `shipped`, etc.)
- [ ] Arquivo salvo em `notebooks/dataset_unificado_v1.csv`

## Dependências
Nenhuma — é a primeira task do projeto.

## Entregável
`notebooks/dataset_unificado_v1.csv`
