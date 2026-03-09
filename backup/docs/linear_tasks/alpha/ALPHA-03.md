# [ALPHA-03] Análise de Correlações de Pearson

**Responsável:** Henry
**Dia:** 1 (Quinta-feira)
**Prioridade:** 🟡 Alta
**Branch:** `feat/alpha-03-correlacoes-pearson`

---

## Descrição

Rodar a primeira bateria de correlações para descobrir quais variáveis numéricas do DataFrame unificado possuem relação linear significativa com a variável alvo `foi_atraso`.

### Passo a Passo

1. Selecionar apenas colunas numéricas do DataFrame.
2. Calcular `df.corr(method='pearson')['foi_atraso'].sort_values()`.
3. Gerar um heatmap visual (Plotly ou Seaborn temporário) das top 10 correlações.
4. Documentar achados: "Quais variáveis mais correlacionam positiva e negativamente com atraso?"
5. Investigar correlações espúrias (ex: `price` e `freight_value` são altamente correlacionadas entre si? Se sim, uma delas pode ser removida).

### Referências
- `docs/algorithms/explicacao_correlacao_pearson.md` → Fundamentação teórica
- `docs/schedule/fase_eda_nichada.md` → Hipóteses a validar

## Critério de Aceite

- [ ] Matriz de correlação gerada e salva como imagem ou HTML
- [ ] Lista das top 5 variáveis mais correlacionadas com `foi_atraso`
- [ ] Multicolinearidade identificada (variáveis duplicadas)
- [ ] Notebook documentado com conclusões

## Dependências
- ALPHA-02 (variável alvo criada)

## Entregável
Notebook `notebooks/eda_correlacoes.ipynb` com gráficos e conclusões
