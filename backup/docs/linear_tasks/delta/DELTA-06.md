# [DELTA-06] Aba 3 — Simulador de Predição

**Responsável:** Pablo
**Dia:** 3 (Sábado)
**Prioridade:** 🔴 Crítica (é o coração do produto)
**Branch:** `feat/delta-06-simulador-predicao`

---

## Descrição

Criar o formulário interativo "Simulador de Nova Venda" onde o usuário insere os dados de um pedido hipotético e o modelo XGBoost retorna a probabilidade de atraso em tempo real.

### Passo a Passo

1. Carregar o modelo `models/xgboost_atraso_v1.pkl` com `joblib.load()`.
2. Criar formulário com `st.form()`:
   - `st.selectbox("Estado do Cliente")` → lista de UFs
   - `st.selectbox("Estado do Vendedor")` → lista de UFs
   - `st.number_input("Peso do Produto (g)")` → 100 a 30000
   - `st.number_input("Valor do Frete (R$)")` → 0 a 300
   - `st.number_input("Preço do Produto (R$)")` → 1 a 5000
   - `st.selectbox("Categoria do Produto")` → lista de categorias
3. Ao clicar "Simular", montar um DataFrame com as features na ordem exata do treinamento.
4. Rodar `model.predict_proba(input_df)` e mostrar o resultado.
5. Exibir com `st.metric()`:
   - "Probabilidade de Atraso: 73%"
   - Cor verde (< 30%), amarela (30-60%), vermelha (> 60%)
6. Mostrar sugestões de ação baseadas no risco.

## Critério de Aceite

- [ ] Formulário aceitando inputs do usuário
- [ ] Modelo `.pkl` carregado e fazendo predições
- [ ] Probabilidade exibida com cores indicativas
- [ ] Sugestões de ação ao usuário
- [ ] Não quebra com inputs extremos (peso 0, frete 0)

## Dependências
- ALPHA-11 (modelo `.pkl` exportado)

## Entregável
Aba 3 funcional com simulador de predição em tempo real
