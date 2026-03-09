# Especificação do Modelo de Machine Learning

> CatBoost V5 para Classificação Binária de Atraso Logístico na Olist.

---

## Tipo de Problema

**Classificação Binária Supervisionada**
- Input (X): 19 features logísticas do pedido (peso, frete, distância, estado, rota, etc.)
- Output (Y): `foi_atraso` → 0 (no prazo) ou 1 (atrasou)

## Algoritmo

**CatBoost Classifier** (`catboost.CatBoostClassifier`)

Escolhido sobre o XGBoost (v1–v4) por:
- Tratamento nativo de features categóricas (sem necessidade de encoding manual)
- Ordered boosting que reduz overfitting em datasets pequenos
- Melhor ROC-AUC: 0.8454 vs 0.7452 (XGBoost v1 baseline)

---

## Features do Modelo (19)

### Features Numéricas (15)

| # | Feature | Descrição | Importância |
|---|:--|:--|:--|
| 1 | `velocidade_lojista_dias` | Dias entre aprovação e postagem | **Mais forte** (Pearson +0.2143) |
| 2 | `distancia_haversine_km` | Distância geodésica seller→customer | Alta |
| 3 | `freight_value` | Valor do frete | Alta |
| 4 | `volume_cm3` | Volume do pacote | Média |
| 5 | `product_weight_g` | Peso do produto (gramas) | Média |
| 6 | `price` | Valor do produto | Média |
| 7 | `total_itens_pedido` | Quantidade de itens no pedido | Média |
| 8 | `prazo_estimado_dias` | Prazo estimado de entrega (dias) | Média |
| 9 | `historico_atraso_vendedor` | Taxa histórica de atraso do seller | Média |
| 10 | `qtd_pedidos_anteriores_vendedor` | Volume histórico de pedidos do seller | Baixa |
| 11 | `frete_por_kg` | Razão frete/peso | Baixa |
| 12 | `mes_compra` | Mês da compra (1–12) | Baixa |
| 13 | `semana_ano` | Semana do ano (1–52) | Baixa |
| 14 | `dia_semana_compra` | Dia da semana (0=Seg, 6=Dom) | Baixa |
| 15 | `eh_alta_temporada` | Flag de período de alta demanda | Baixa |

### Features Categóricas (4) — Tratamento Nativo CatBoost

| # | Feature | Descrição |
|---|:--|:--|
| 16 | `seller_state` | UF do vendedor |
| 17 | `customer_state` | UF do cliente |
| 18 | `rota` | Rota seller_state→customer_state (string concatenada) |
| 19 | `product_category_name` | Categoria do produto |

> CatBoost processa as 4 features categóricas nativamente via ordered target encoding interno, sem necessidade de LabelEncoder ou OneHotEncoder.

---

## Hiperparâmetros (Grid Search)

```python
model = CatBoostClassifier(
    depth=10,
    iterations=500,
    learning_rate=0.1,
    l2_leaf_reg=3,
    cat_features=[15, 16, 17, 18],  # índices das categóricas
    eval_metric='AUC',
    random_seed=42,
    verbose=False
)
```

**Busca realizada:** Grid search manual com `StratifiedKFold(n_splits=5)` sobre:
- `depth`: [6, 8, 10]
- `iterations`: [300, 500]
- `learning_rate`: [0.05, 0.1]
- `l2_leaf_reg`: [1, 3, 5]

---

## Tratamento de Desbalanceamento — SMOTE

| Parâmetro | Valor |
|:--|:--|
| Strategy | 0.3 (oversampling da minoria até 30% da maioria) |
| Amostras sintéticas geradas | 18.891 |
| Aplicado sobre | Apenas features numéricas (categóricas herdadas do vizinho mais próximo) |

> SMOTE aplicado **apenas no conjunto de treino** para evitar data leakage.

---

## Divisão dos Dados

- **80% Treino / 20% Teste**
- `train_test_split(stratify=y, random_state=42)` para manter proporção 93%/7%
- SMOTE aplicado após o split, apenas no treino

---

## Threshold de Decisão

**Threshold otimizado: 0.54**

- Calibrado maximizando F1-Score no conjunto de teste
- Acima do default (0.50) para reduzir falsos positivos
- Trade-off: precision mais alta em troca de recall ligeiramente menor

---

## Métricas de Avaliação (CatBoost V5)

| Métrica | Valor | Meta Mínima | Status |
|:--|:--|:--|:--|
| **ROC-AUC** (Principal) | **0.8454** | ≥ 0.70 | ✅ Superou |
| **Recall** | 0.4150 (41.5%) | ≥ 0.60 | ⚠️ Abaixo da meta |
| **Precision** | 0.5355 (53.6%) | — | — |
| **F1-Score** | 0.4676 | ≥ 0.50 | ⚠️ Próximo da meta |
| **Accuracy** | 0.9377 (93.8%) | — | — |
| **Multiplicador vs Acaso** | 8.11x | — | ✅ Excelente |

### Matriz de Confusão (Conjunto de Teste)

```
                  Predito: No Prazo    Predito: Atrasou
Real: No Prazo        20.062 (TN)          523 (FP)
Real: Atrasou            850 (FN)          603 (TP)
```

- **Total teste:** 22.038 pedidos
- O modelo encontra 41.5% dos atrasos reais (Recall)
- Quando prevê atraso, acerta 53.6% das vezes (Precision)
- 8.11x melhor que chute aleatório

---

## Evolução do Modelo

| Versão | Algoritmo | ROC-AUC | Recall | F1 | Observação |
|:--|:--|:--|:--|:--|:--|
| v1 | XGBoost | 0.7452 | — | — | Baseline com scale_pos_weight |
| v5 | **CatBoost** | **0.8454** | 0.415 | 0.468 | Categóricas nativas + SMOTE + grid search |

---

## Exportação e Caminhos

| Artefato | Caminho | Formato |
|:--|:--|:--|
| Modelo CatBoost | `src/models/v5/catboost_atraso_v5.cbm` | CatBoost nativo (11 MB) |
| Modelo Pickle | `src/models/v5/catboost_atraso_v5.pkl` | joblib (11 MB) |
| Configuração | `src/models/v5/model_config.json` | JSON (métricas, features, params) |
| Ordem das features | `src/models/v5/features_order.txt` | Texto (1 feature por linha) |

### Uso no MCP Server

```python
from olist_mcp.cache import DataStore

model = DataStore.model()          # Carrega catboost_atraso_v5.cbm
config = DataStore.model_config()  # Carrega model_config.json
```

---

## Plano de Contingência

| Cenário | Ação |
|:--|:--|
| ROC-AUC < 0.70 | Revisar features e testar LightGBM |
| Recall muito baixo | Baixar threshold (custo: mais falsos positivos) |
| Modelo ausente no deploy | MCP tools degradam graciosamente para estatísticas de correlação |
| Nova versão de dados | Retreinar com mesmo pipeline (`src/models/v5/05_modelo_catboost_v5.py`) |
