# [ALPHA-10] Feature Importance e Métricas Finais

**Responsável:** Henry
**Dia:** 3 (Sábado)
**Prioridade:** 🟡 Alta
**Branch:** `feat/alpha-10-feature-importance`

---

## Descrição

Extrair do modelo treinado (após tuning) quais features foram as mais importantes para a predição. Esses dados alimentam diretamente o Esquadrão Omega (narrativa de negócio) e o Esquadrão Delta (Aba 2 — Insights).

### Passo a Passo

1. Extrair `model.feature_importances_` do XGBoost.
2. Gerar gráfico de barras horizontal com as top 10 features por importância.
3. Gerar a Matriz de Confusão visual.
4. Calcular métricas finais: ROC-AUC, Recall, F1-Score, Precision.
5. Exportar os gráficos como imagens (PNG) para uso nos slides do Omega.

## Critério de Aceite

- [ ] Gráfico de Feature Importance gerado
- [ ] Matriz de Confusão gerada
- [ ] Métricas finais documentadas e comparadas com as metas de `criterios_sucesso.md`
- [ ] Imagens exportadas para o Esquadrão Omega

## Dependências
- ALPHA-09 (modelo otimizado)

## Entregável
Gráficos e métricas exportados + Notebook documentado
