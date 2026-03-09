# [ALPHA-02] Criar a Variável Alvo (`foi_atraso`)

**Responsável:** Henry, Lucas
**Dia:** 1 (Quinta-feira)
**Prioridade:** 🔴 Crítica
**Branch:** `feat/alpha-02-variavel-alvo`

---

## Descrição

Fabricar a coluna Target (Y) que o XGBoost vai aprender a prever. A Olist não fornece essa variável pronta — precisamos criá-la a partir da diferença entre a data real de entrega e a data prometida.

### Passo a Passo

1. No DataFrame unificado (resultado do ALPHA-01):
   ```python
   df['dias_diferenca'] = (df['order_delivered_customer_date'] - df['order_estimated_delivery_date']).dt.days
   df['foi_atraso'] = (df['dias_diferenca'] > 0).astype(int)
   ```
2. Validar a distribuição: espera-se ~93% classe 0 e ~7% classe 1.
3. Imprimir `df['foi_atraso'].value_counts(normalize=True)` para confirmar.
4. Atualizar o CSV unificado com essa nova coluna.

### Referências
- `spec/data_schema.md` → Fórmula oficial da variável alvo
- `docs/data/atributos_modelo.md` → Contexto das features

## Critério de Aceite

- [ ] Coluna `foi_atraso` criada corretamente (0 ou 1)
- [ ] Coluna `dias_diferenca` criada (numérica, positiva = atraso)
- [ ] Distribuição validada (~93%/7%)
- [ ] Nenhuma linha com `NaN` na coluna `foi_atraso`

## Dependências
- ALPHA-01 (DataFrame unificado)

## Entregável
Coluna `foi_atraso` adicionada ao `dataset_unificado_v1.csv`
