# Especificação do Modelo de Machine Learning

> XGBoost para Classificação Binária de Atraso Logístico na Olist.

---

## Tipo de Problema

**Classificação Binária Supervisionada**
- Input (X): Features logísticas do pedido (peso, frete, distância, estado, etc.)
- Output (Y): `foi_atraso` → 0 (no prazo) ou 1 (atrasou)

## Algoritmo Principal

**XGBoost Classifier** (`xgboost.XGBClassifier`)

### Hiperparâmetros Iniciais Sugeridos (Baseline)

```python
model = XGBClassifier(
    objective='binary:logistic',
    eval_metric='auc',
    scale_pos_weight=13.76,       # ratio: 89941 / 6535 (balancear classes)
    max_depth=6,
    learning_rate=0.1,
    n_estimators=200,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)
```

> O parâmetro `scale_pos_weight` é crucial para forçar o modelo a não ignorar a classe minoritária (atrasos = 6,77%).

## Divisão dos Dados

- **80% Treino / 20% Teste**
- Usar `train_test_split(stratify=y)` para garantir a proporção de 6,77% de atrasos nos dois conjuntos.

## Métricas de Avaliação

| Métrica | Função | Meta Mínima |
|:--|:--|:--|
| **ROC-AUC** (Principal) | Capacidade geral de separar classes | ≥ 0.70 |
| **Recall** | % de atrasos reais encontrados pela IA | ≥ 0.60 |
| **F1-Score** | Equilíbrio entre Precisão e Recall | ≥ 0.50 |
| **Matriz de Confusão** | Visualizar falsos positivos/negativos | Análise visual |

> Se o ROC-AUC ficar abaixo de 0.70, considerar:
> 1. Revisar as features (remover ruído ou adicionar novas)
> 2. Testar Random Forest como alternativa
> 3. Aplicar SMOTE para oversampling da classe minoritária

## Exportação do Modelo Final

```python
import joblib
joblib.dump(model, 'models/xgboost_atraso_v1.pkl')
```

O Esquadrão Delta (Pablo/Douglas) carregará o `.pkl` no Streamlit para a Aba 3 (Simulador):

```python
model = joblib.load('models/xgboost_atraso_v1.pkl')
prediction = model.predict_proba(input_data)
```

## Plano de Contingência

| Cenário | Ação |
|:--|:--|
| ROC-AUC < 0.65 | Trocar para Random Forest |
| Modelo muito lento no Streamlit | Reduzir `n_estimators` para 100 |
| Deploy Streamlit Cloud falhar | Usar Render como alternativa gratuita |
