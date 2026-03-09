# [ALPHA-04] Revisão Anti Data-Leakage

**Responsável:** Mauricio
**Dia:** 1 (Quinta-feira)
**Prioridade:** 🔴 Crítica
**Branch:** `feat/alpha-04-revisao-leakage`

---

## Descrição

Revisar todo o código gerado pelo Henry e Lucas para garantir que nenhuma informação do futuro esteja "vazando" para o treinamento do modelo. Data Leakage é o erro #1 que invalida modelos de ML em produção.

### O que verificar

1. **Leak Temporal:** A coluna `order_delivered_customer_date` NÃO pode ser usada como feature (é informação do futuro — você só sabe quando o pacote chegou DEPOIS que ele chegou). Ela só deve ser usada para CALCULAR a variável alvo.
2. **Leak de Target:** A coluna `dias_diferenca` NÃO pode entrar como feature (é derivada direta do target).
3. **Leak de Review:** A coluna `review_score` NÃO deve ser feature (o review acontece DEPOIS da entrega, não antes).
4. **Leak de Status:** `order_status` deve ter sido filtrado para `delivered` apenas — se houver `canceled`, o modelo aprende padrões errados.

### Checklist de Revisão

- [ ] Nenhuma coluna de data posterior ao despacho está como feature
- [ ] `review_score` não está nas features
- [ ] `dias_diferenca` não está nas features
- [ ] `order_status` filtrado corretamente
- [ ] Nenhuma coluna com informação de ID (order_id, customer_id) está como feature

## Dependências
- ALPHA-02 (DataFrame com target)

## Entregável
Revisão aprovada (Go/No-Go) para o time prosseguir com Feature Engineering
