# [ALPHA-09] Tuning de Hiperparâmetros

**Responsável:** Mauricio
**Dia:** 3 (Sábado)
**Prioridade:** 🟡 Alta
**Branch:** `feat/alpha-09-tuning-modelo`

---

## Descrição

Otimizar os hiperparâmetros do XGBoost para extrair a melhor performance possível. Se o baseline (ALPHA-08) já atingiu ROC-AUC ≥ 0.70, o tuning busca melhorar ainda mais. Se ficou abaixo, o tuning é obrigatório.

### Hiperparâmetros a Otimizar

| Parâmetro | Range de Busca |
|:--|:--|
| `max_depth` | [3, 5, 6, 8, 10] |
| `learning_rate` | [0.01, 0.05, 0.1, 0.2] |
| `n_estimators` | [100, 200, 300, 500] |
| `subsample` | [0.6, 0.7, 0.8, 1.0] |
| `colsample_bytree` | [0.6, 0.7, 0.8, 1.0] |
| `scale_pos_weight` | [10, 13.76, 15, 20] |

### Método Sugerido
- `GridSearchCV` (se o time tiver tempo) ou `RandomizedSearchCV` (mais rápido).
- Usar `cv=5` (5-fold cross-validation estratificada).
- Métrica de scoring: `roc_auc`.

## Critério de Aceite

- [ ] Pelo menos 3 combinações testadas
- [ ] Melhor combinação documentada
- [ ] ROC-AUC melhorado em relação ao baseline
- [ ] Se ROC-AUC < 0.65 → acionar plano de contingência (testar Random Forest)

## Dependências
- ALPHA-08 (baseline treinado)

## Entregável
Modelo otimizado e melhores hiperparâmetros documentados no notebook
