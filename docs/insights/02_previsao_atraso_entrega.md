# 02 - Previsão de Atraso na Entrega

## O Objetivo e Motivação
Na Olist, como a logística é complexa em um país de dimensões continentais como o Brasil, o cumprimento do prazo de entrega (`order_estimated_delivery_date` vs `order_delivered_customer_date`) afeta tudo, do cancelamento às métricas do vendedor. Este modelo tem o objetivo de prever:
**Qual o risco de um pedido chegar atrasado assim que ele for emitido?**

O grande ganho prático é logístico. Prever isso antes mesmo do vendedor enviar sua carga para a transportadora permite ajustar a malha (trocar o operador ou fretar vias rápidas) e notificar o usuário para que a expectativa seja ajustada. Reduz cancelamentos e ações judiciais.

---

## Modelo Implementado: CatBoost V5

### Algoritmo e Abordagem

**CatBoost Classifier** (Gradient Boosting com tratamento nativo de features categóricas)

| Parâmetro | Valor |
|:--|:--|
| Tipo | Classificação binária (`foi_atraso`: 0 ou 1) |
| Algoritmo | CatBoost (ordered boosting) |
| Features | 19 (15 numéricas + 4 categóricas nativas) |
| Threshold | 0.54 (otimizado para F1-Score) |
| Balanceamento | SMOTE (strategy=0.3, +18.891 amostras sintéticas) |
| Split | 80/20 estratificado (random_state=42) |

### Por que CatBoost sobre XGBoost?

O XGBoost v1 (baseline) atingiu ROC-AUC 0.7452. O CatBoost V5 alcançou **0.8454** (+13%) graças a:
1. **Categóricas nativas**: `seller_state`, `customer_state`, `rota`, `product_category_name` são processadas sem encoding manual
2. **Ordered boosting**: reduz overfitting em datasets com classe minoritária pequena
3. **SMOTE** no treino: gera amostras sintéticas da classe minoritária (vs `scale_pos_weight` do XGBoost)

---

## As 19 Features do Modelo

### Top 5 Features por Importância

| # | Feature | Descrição | Por que funciona |
|:--|:--|:--|:--|
| 1 | `velocidade_lojista_dias` | Dias entre aprovação e postagem | Lojistas lentos = atraso cascata. Pearson +0.2143 |
| 2 | `distancia_haversine_km` | Distância geodésica seller→customer | Brasil continental, distância importa |
| 3 | `freight_value` | Valor do frete | Proxy de complexidade logística |
| 4 | `rota` | String seller_state→customer_state | Captura rotas problemáticas (ex: SP→MA) |
| 5 | `prazo_estimado_dias` | Prazo estimado pela Olist | Prazos apertados têm mais risco de estouro |

### Lista Completa

**Numéricas (15):** velocidade_lojista_dias, distancia_haversine_km, freight_value, volume_cm3, product_weight_g, price, total_itens_pedido, prazo_estimado_dias, historico_atraso_vendedor, qtd_pedidos_anteriores_vendedor, frete_por_kg, mes_compra, semana_ano, dia_semana_compra, eh_alta_temporada

**Categóricas (4):** seller_state, customer_state, rota, product_category_name

---

## Resultados

### Métricas de Avaliação

| Métrica | Valor | Interpretação |
|:--|:--|:--|
| **ROC-AUC** | **0.8454** | O modelo distingue bem entre pedidos pontuais e atrasados |
| **Recall** | 41.5% | Detecta 4 em cada 10 atrasos reais |
| **Precision** | 53.6% | Quando alerta atraso, acerta ~54% das vezes |
| **F1-Score** | 0.4676 | Equilíbrio precision/recall |
| **Accuracy** | 93.8% | (Inflada pelo desbalanceamento — não usar como métrica principal) |
| **Multiplicador** | **8.11x** | 8x melhor que chute aleatório |

### Matriz de Confusão (Conjunto de Teste — 22.038 pedidos)

```
                  Predito: No Prazo    Predito: Atrasou
Real: No Prazo        20.062 (TN)          523 (FP)
Real: Atrasou            850 (FN)          603 (TP)
```

### O que isso significa na prática?

- **603 atrasos detectados corretamente** → a logística pode intervir nesses pedidos
- **523 alarmes falsos** → pedidos flagrados como "risco" mas que chegaram no prazo (custo: atenção desperdiçada)
- **850 atrasos não detectados** → o modelo não pegou esses (custo: cliente insatisfeito)

---

## Simulações e Cenários

O MCP Server expõe a tool `simulate_scenario` que permite variar uma feature e ver o impacto na probabilidade de atraso. Exemplos:

| Cenário | Probabilidade de Atraso |
|:--|:--|
| Lojista rápido (1 dia) + SP→SP | ~3% |
| Lojista lento (5 dias) + SP→MA | ~45% |
| Lojista médio (3 dias) + distância 2.500km | ~25% |

> Essas simulações permitem à equipe de logística **quantificar o impacto** de cada variável operacional.

---

## Tabela de Construção Preditiva (Pipeline)

### Fontes de Dados

| Tabela Olist | Features Extraídas | Pipeline |
|:--|:--|:--|
| `olist_orders` | Timestamps (5), target `foi_atraso`, `prazo_estimado_dias` | Seção 1–3 do pipeline |
| `olist_customers` | `customer_state`, `customer_zip_code_prefix` → lat/lng | Seção 1 + geocoding |
| `olist_sellers` | `seller_state`, `historico_atraso_vendedor`, `qtd_pedidos_anteriores` | Seção 1 + feature engineering |
| `olist_order_items` | `price`, `freight_value`, `total_itens_pedido` | Seção 1 |
| `olist_products` | `product_weight_g`, dimensões → `volume_cm3`, `product_category_name` | Seção 1 |
| `olist_geolocation` | lat/lng → `distancia_haversine_km` | Seção 4 (Haversine) |

### Pipeline de Treino

1. **Merge** → 6 tabelas unificadas em DataFrame de ~110K linhas
2. **Feature Engineering** → 19 features criadas/selecionadas
3. **Split** → 80% treino / 20% teste (estratificado)
4. **SMOTE** → Oversampling da minoria no treino (strategy=0.3)
5. **Grid Search** → CatBoost com StratifiedKFold(5) sobre depth, iterations, lr, l2
6. **Threshold** → Otimização F1 → 0.54
7. **Export** → `catboost_atraso_v5.cbm` + `model_config.json`

### Código-fonte

- **Pipeline EDA:** `src/notebooks/dia1_alpha_pipeline.py` (seções 1–8)
- **Treino CatBoost V5:** `src/models/v5/05_modelo_catboost_v5.py`
- **MCP Integration:** `src/olist_mcp/catboost_ml.py` (4 tools: predict, info, importance, simulate)

---

### Por Que É Ideal para a Equipe?
É o tipo de projeto que tem impacto financeiro absurdo e valor imediato num portfólio de Ciência de Dados. Tratar desbalanceamento com SMOTE, calcular distâncias geográficas com Haversine, processar categóricas nativas com CatBoost e expor tudo via MCP para um chatbot é um stack completo e real.
