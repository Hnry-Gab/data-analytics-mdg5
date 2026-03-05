# [DELTA-05] Aba 2 — Insights Textuais

**Responsável:** Douglas
**Dia:** 3 (Sábado)
**Prioridade:** 🟡 Alta
**Branch:** `feat/delta-05-aba-insights`

---

## Descrição

Montar a Aba 2 do Frontend/FastAPI com os principais insights de negócio traduzidos pelo Esquadrão Omega. Os insights são apresentados como "Key Results" visuais com gráficos de apoio.

### Conteúdo Esperado

1. **Cards de Insight** (formato `st.info()` ou `st.success()`):
   - "X% dos atrasos são causados por rotas interestaduais"
   - "Categoria Y tem 3x mais atrasos que a média"
   - "Vendedores que demoram >3 dias para despachar têm 40% mais atrasos"

2. **Gráficos de Apoio:**
   - Feature Importance do modelo (gráfico recebido do ALPHA-10)
   - Comparativo de atrasos por rota (intraestadual vs interestadual)

3. **Texto narrativo** recebido do Esquadrão Omega.

## Critério de Aceite

- [ ] Pelo menos 3 insights destacados visualmente
- [ ] Pelo menos 1 gráfico de apoio
- [ ] Texto claro e orientado a negócios (não técnico)

## Dependências
- ALPHA-10 (Feature Importance)
- OMEGA-03 (narrativa de negócio)

## Entregável
Aba 2 funcional com insights e gráficos
