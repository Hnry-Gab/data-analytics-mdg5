# [ALPHA-07] Split Treino/Teste Estratificado

**Responsável:** Mauricio, Lucas
**Dia:** 2 (Sexta-feira)
**Prioridade:** 🔴 Crítica
**Branch:** `feat/alpha-07-split-treino-teste`

---

## Descrição

Dividir o DataFrame final (com as features selecionadas) em 80% treino e 20% teste, garantindo que a proporção de ~7% de atrasos seja mantida em ambos os conjuntos.

### Passo a Passo

```python
from sklearn.model_selection import train_test_split

X = df[features_selecionadas]
y = df['foi_atraso']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# Validar proporção
print(y_train.value_counts(normalize=True))
print(y_test.value_counts(normalize=True))
```

## Critério de Aceite

- [ ] Split 80/20 realizado
- [ ] `stratify=y` utilizado (proporção idêntica nos dois conjuntos)
- [ ] `random_state=42` para reprodutibilidade
- [ ] Sem data leakage (nenhuma informação do teste vazou pro treino)

## Dependências
- ALPHA-06 (features selecionadas e encodadas)

## Entregável
Variáveis `X_train`, `X_test`, `y_train`, `y_test` prontas para treino
