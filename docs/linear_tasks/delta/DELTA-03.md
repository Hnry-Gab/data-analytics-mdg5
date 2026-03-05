# [DELTA-03] Plugar CSV Real nos Gráficos (Aba 1)

**Responsável:** Pablo, Douglas
**Dia:** 2 (Sexta-feira)
**Prioridade:** 🔴 Crítica
**Branch:** `feat/delta-03-csv-real`

---

## Descrição

Substituir os dados mockados (DELTA-02) pelo CSV real gerado pelo Esquadrão Alpha. Conectar o DataFrame unificado ao código da Aba 1 (Painel Gerencial).

### Passo a Passo

1. Receber o arquivo `dataset_unificado_v1.csv` do Henry.
2. Apagar ou comentar o `mock_data.py`.
3. Criar `src/data/load_data.py` com função `@st.cache_data` para carregar o CSV real.
4. Substituir todos os `# TODO` por chamadas ao DataFrame real.
5. Testar se os gráficos da Aba 1 renderizam com dados reais.

## Critério de Aceite

- [ ] Nenhum dado mockado restante na Aba 1
- [ ] `@st.cache_data` implementado (evita recarregar CSV a cada interação)
- [ ] Gráficos renderizando com dados reais da Olist

## Dependências
- ALPHA-01 (CSV unificado pronto)
- DELTA-02 (mockups a serem substituídos)

## Entregável
Aba 1 funcionando 100% com dados reais
