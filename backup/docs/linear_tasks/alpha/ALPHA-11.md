# [ALPHA-11] Exportar Modelo `.pkl` Final

**Responsável:** Mauricio
**Dia:** 3 (Sábado)
**Prioridade:** 🔴 Crítica (bloqueia o Esquadrão Delta)
**Branch:** `feat/alpha-11-exportar-modelo`

---

## Descrição

Serializar (salvar) o modelo XGBoost otimizado como um arquivo `.pkl` que o Esquadrão Delta carregará no Streamlit para o Simulador de Predição (Aba 3).

### Passo a Passo

```python
import joblib

# Salvar o modelo
joblib.dump(model, 'models/xgboost_atraso_v1.pkl')

# Testar o carregamento
model_loaded = joblib.load('models/xgboost_atraso_v1.pkl')
test_pred = model_loaded.predict_proba(X_test[:5])
print(test_pred)  # Deve retornar probabilidades
```

### Importante
- Salvar também a lista de features na ordem exata usada no treino (o Streamlit precisa enviar os dados na mesma ordem).
- Salvar o encoder (se `LabelEncoder` ou `OneHotEncoder` foi usado) junto com o modelo.

## Critério de Aceite

- [ ] Arquivo `models/xgboost_atraso_v1.pkl` criado e funcional
- [ ] Teste de carregamento (`joblib.load`) bem-sucedido
- [ ] Lista de features na ordem correta documentada
- [ ] Encoder salvo (se aplicável)

## Dependências
- ALPHA-09 (modelo otimizado)

## Entregável
`models/xgboost_atraso_v1.pkl` + lista de features documentada
