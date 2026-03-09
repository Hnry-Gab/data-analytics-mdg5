# [ALPHA-08] Treinar Baseline XGBoost

**Responsável:** Mauricio
**Dia:** 2 (Sexta-feira)
**Prioridade:** 🔴 Crítica
**Branch:** `feat/alpha-08-baseline-xgboost`

---

## Descrição

Treinar a primeira versão do modelo XGBoost (o "rascunho") com hiperparâmetros padrão para verificar se o algoritmo consegue aprender os padrões de atraso. O objetivo NÃO é ter a melhor performance, mas validar que o pipeline funciona de ponta a ponta.

### Passo a Passo

```python
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, roc_auc_score

model = XGBClassifier(
    objective='binary:logistic',
    eval_metric='auc',
    scale_pos_weight=13.76,  # 89941 / 6535
    random_state=42
)

model.fit(X_train, y_train)
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

print(f"ROC-AUC: {roc_auc_score(y_test, y_proba):.4f}")
print(classification_report(y_test, y_pred))
```

### Referências
- `spec/model_spec.md` → Hiperparâmetros sugeridos e metas

## Critério de Aceite

- [ ] Modelo treinado sem erros
- [ ] ROC-AUC calculado e reportado
- [ ] Classification report (Precision, Recall, F1) gerado
- [ ] Resultado printado no notebook para análise

## Dependências
- ALPHA-07 (split treino/teste)

## Entregável
Notebook `notebooks/model_baseline.ipynb` com métricas do primeiro rascunho
