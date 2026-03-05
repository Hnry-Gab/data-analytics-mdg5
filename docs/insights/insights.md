# Insights do Dataset Olist: Por que Churn não é o ideal?

## O Problema Principal
Ao analisar a base de dados (`olist_orders` + `olist_customers`), o resultado da taxa de recompra demonstra que a retenção não é o foco principal desse e-commerce:

*   **Total de Pedidos:** 99.441
*   **Clientes Únicos:** 96.096
*   **Taxa de Recompra:** Apenas **~3,11%** (2.997 clientes compraram mais de uma vez).

**Conclusão:** 
Como ~97% dos clientes compram apenas uma vez, o modelo não terá dados suficientes para aprender o comportamento de um cliente fiel que de repente decide parar de consumir (Churn). O "abandono" é, na verdade, o padrão natural.

---

## Soluções Promissoras para Modelagem Preditiva

Listamos abaixo as abordagens com muito mais probabilidade de sucesso usando este dataset, focadas na relação entre logística e a retenção de clientes (Growth). Veja as explicações detalhadas:

1.  **Previsão de Atraso na Entrega (Motor Logístico):**
    *   Foco logístico para prever proativamente se um pacote não chegará a tempo.
    *   [Leia mais](./02_previsao_atraso_entrega.md)
    *   *Nota:* O contexto de "Satisfação do Cliente (Review Score)" foi despriorizado para focar 100% da inteligência da equipe num único motor logístico de alta precisão devido ao prazo de 4 dias. Regularemos a retenção e o *Growth* focando em entregar no prazo.
