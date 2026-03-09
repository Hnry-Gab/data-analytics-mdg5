# [ALPHA-06] Seleção Final das Top Features

**Responsável:** Henry
**Dia:** 2 (Sexta-feira)
**Prioridade:** 🟡 Alta
**Branch:** `feat/alpha-06-selecao-features`

---

## Descrição

Com base nas correlações (ALPHA-03) e nas features criadas (ALPHA-05), bater o martelo e definir quais 5-8 variáveis finais entrarão no treinamento do modelo. Features com correlação muito baixa (<0.05) ou com alta multicolinearidade devem ser descartadas.

### Passo a Passo

1. Recalcular a matriz de correlação com as novas features derivadas.
2. Rodar `feature_importances_` de um Random Forest rápido (sem tuning) para ranking.
3. Remover features redundantes (ex: se `customer_state` e `rota_interestadual` dizem a mesma coisa, manter apenas uma).
4. Listar as top 5-8 features finais com justificativa.
5. Fazer encoding das variáveis categóricas (`product_category_name`, `customer_state`) com `LabelEncoder` ou `OneHotEncoder`.

## Critério de Aceite

- [ ] Lista final de 5-8 features documentada
- [ ] Justificativa para cada feature incluída/excluída
- [ ] Variáveis categóricas encodadas (numéricas)
- [ ] DataFrame final pronto para split treino/teste

## Dependências
- ALPHA-05 (features criadas)

## Entregável
DataFrame final limpo com apenas as colunas selecionadas + `foi_atraso`
