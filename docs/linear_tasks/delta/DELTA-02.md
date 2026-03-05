# [DELTA-02] Dados Mockados para Testes Visuais

**Responsável:** Douglas
**Dia:** 1 (Quinta-feira)
**Prioridade:** 🟡 Alta
**Branch:** `feat/delta-02-dados-mockados`

---

## Descrição

Como o Esquadrão Alpha ainda não finalizou o CSV real no Dia 1, criar dados falsos (mockados) para que o Frontend/FastAPI já tenha gráficos de teste aparecendo nas telas. Isso evita que o Delta fique parado esperando o Alpha.

### Passo a Passo

1. Criar um arquivo `src/data/mock_data.py` que gere DataFrames simulados.
2. Simular ~200 linhas com colunas relevantes: `estado`, `foi_atraso`, `freight_value`, `price`, `dias_diferenca`, `product_category`.
3. Gerar gráficos de teste na Aba 1: mapa de calor por estado, gráfico de barras de atrasos por categoria.
4. Marcar claramente no código com `# TODO: substituir por dados reais` para facilitar a troca no Dia 2.

## Critério de Aceite

- [ ] DataFrames mockados gerando gráficos visíveis nas 3 abas
- [ ] Todas as marcações `# TODO` presentes para fácil substituição
- [ ] App não quebra com os dados falsos

## Dependências
- DELTA-01 (esqueleto criado)

## Entregável
Gráficos de teste rodando no Frontend/FastAPI local
