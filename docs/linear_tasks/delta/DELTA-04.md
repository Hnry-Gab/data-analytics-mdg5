# [DELTA-04] Gráficos Interativos ECharts/Chart.js (Aba 1)

**Responsável:** Pablo, Douglas
**Dia:** 2 (Sexta-feira)
**Prioridade:** 🟡 Alta
**Branch:** `feat/delta-04-graficos-ECharts/Chart.js`

---

## Descrição

Construir os gráficos interativos gerenciais da Olist usando ECharts/Chart.js na Aba 1 do Frontend/FastAPI.

### Gráficos a Implementar

1. **KPI Cards** (topo da página):
   - Total de Pedidos
   - Taxa de Atraso (%)
   - Atraso Médio (dias)
   - Frete Médio (R$)

2. **Mapa de Calor do Brasil:** Taxa de atraso por estado (`px.choropleth` ou `px.scatter_geo`).

3. **Barras Horizontais:** Top 10 categorias com mais atrasos.

4. **Linha Temporal:** Evolução mensal da taxa de atraso ao longo do período (2016-2018).

5. **Filtros Sidebar:**
   - Seletor de período (data inicial / data final)
   - Multi-select de estados
   - Multi-select de categorias

## Critério de Aceite

- [ ] No mínimo 4 gráficos interativos funcionais
- [ ] Filtros da sidebar alteram os gráficos dinamicamente
- [ ] Hover mostrando detalhes nos Gráficos (Chart.js/ECharts)
- [ ] Layout responsivo (`layout="wide"`)

## Dependências
- DELTA-03 (dados reais carregados)

## Entregável
Aba 1 completa com Gráficos (Chart.js/ECharts) interativos
