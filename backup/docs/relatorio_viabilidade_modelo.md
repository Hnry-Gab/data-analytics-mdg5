# Relatório de Viabilidade — Modelo Preditivo de Atrasos Logísticos

> **Data:** 05/03/2026 | **Autor:** Esquadrão Alpha | **Status:** Análise concluída

---

## 1. Resumo da EDA Nichada

### O que fizemos
Cruzamos 6 tabelas do dataset Olist (orders, customers, items, products, sellers, geolocation) em um DataFrame unificado de **110.189 linhas**, criamos a variável alvo `foi_atraso` e testamos **22 atributos** (diretos + criados + ocultos) usando Pearson, Point-Biserial e Cramér's V.

### Distribuição da Variável Alvo

| Classe | Quantidade | % |
|:--|:--|:--|
| No prazo (0) | 102.925 | 93,41% |
| Atrasou (1) | 7.264 | 6,59% |

**Dataset fortemente desbalanceado** → Acurácia é métrica proibida. Usaremos ROC-AUC, Recall e F1-Score.

---

## 2. Ranking Final de Atributos

### Features Aprovadas (com sinal estatístico relevante)

| # | Feature | Tipo | Correlação | Método | Veredicto |
|:--|:--|:--|:--|:--|:--|
| 1 | `velocidade_lojista_dias` | Numérica (Criada) | **+0.2143** | Pearson | ✅ Obrigatória |
| 2 | `customer_state` | Categórica | **0.1336** | Cramér's V | ✅ Obrigatória |
| 3 | `distancia_haversine_km` | Numérica (Criada) | **+0.0753** | Pearson | ⚠️ Forte candidata |
| 4 | `seller_state` | Categórica | **0.0507** | Cramér's V | ⚠️ Candidata |
| 5 | `freight_value` | Numérica | **+0.0467** | Pearson | ⚠️ Candidata |
| 6 | `rota_interestadual` | Binária (Criada) | +0.0380 | Pearson | ⚠️ Candidata |

### Features Fracas (guardar para testes no treino)

| Feature | Correlação | Observação |
|:--|:--|:--|
| `product_category_name` | 0.0324 | Saber a categoria quase não altera a chance de atraso |
| `product_weight_g` | +0.0263 | Peso isolado tem pouco impacto |
| `volume_cm3` | +0.0222 | Idem para volume |
| `price` | +0.0230 | Ticket alto não protege contra atraso |
| `frete_ratio` | +0.0185 | Proporção frete/preço sem sinal forte |
| `dia_semana_compra` | -0.0106 | Efeito de fim de semana é quase nulo |

### Features Auditadas e Descartadas (Tabelas ocultas)

| Feature | Fonte | Correlação | Motivo do descarte |
|:--|:--|:--|:--|
| `prazo_estimado_dias` | orders | -0.0626 | Óbvia e circular — o prazo estimado já é calculado pela Olist com base nos mesmos dados. Usá-la faria o modelo ficar "preguiçoso" |
| `qtd_parcelas` | payments | +0.0045 | Irrelevante — forma de pagamento não afeta logística |
| `qtd_itens` | items | -0.0147 | Mínima — pedidos com vários itens não atrasam mais |
| `product_photos_qty` | products | -0.0020 | Zero sinal |
| `product_name_lenght` | products | +0.0056 | Zero sinal |
| `hora_compra` | orders | +0.0096 | Irrelevante |
| `payment_type` (boleto vs cartão) | payments | 8.6% vs 7.7% | Diferença ínfima entre métodos |

### Multicolinearidade
- `freight_value` ↔ `product_weight_g`: correlação moderada (~0.6) — ambos podem coexistir
- Nenhum par com correlação > 0.7 encontrado → sem redundância grave

---

## 3. Análise de Viabilidade — Faz sentido treinar o modelo?

### A resposta honesta: **SIM, mas com expectativas calibradas.**

#### ✅ Pontos a favor

1. **Temos uma feature dominante.** A `velocidade_lojista_dias` (Pearson 0.2143) é forte o suficiente para servir de "âncora" do modelo. Em datasets logísticos reais, uma correlação individual de 0.21 com a variável alvo é um excelente ponto de partida.

2. **O XGBoost aprende combinações.** O Pearson mede relações **individuais e lineares**. Mas o XGBoost é um modelo de árvore que descobre **combinações não-lineares**. Exemplo: `velocidade_lojista = 3 dias` E `distancia = 2.500km` E `rota_interestadual = 1` → atraso quase certo. Essas combinações **não aparecem no Pearson**, mas o modelo as encontra sozinho. Por isso, features com Pearson "fraco" isoladamente (como distância ou frete) podem se tornar poderosas quando combinadas.

3. **Volume de dados é adequado.** 110 mil registros com ~7.200 atrasos dão ao modelo exemplos suficientes para aprender padrões, desde que usemos `scale_pos_weight` para compensar o desbalanceamento.

4. **As features são do mundo real.** Velocidade do lojista, distância geográfica e estado do cliente são variáveis **operacionais** que a equipe de logística da Olist realmente controla ou monitora. Isso dá valor de negócio ao modelo.

#### ⚠️ Riscos e limitações

1. **Correlações individuais são fracas (exceto a #1).** Das 6 candidatas, apenas 1 ultrapassa 0.10 (velocidade_lojista). As demais ficam entre 0.03 e 0.07. Isso significa que o modelo **não terá alta precisão individual** — ele vai errar bastante em previsões específicas, mas deve acertar os padrões gerais.

2. **Recall esperado: 55-70%.** Baseado na qualidade dos dados e benchmarks de problemas logísticos similares com XGBoost, a expectativa realista é que o modelo consiga detectar entre 55% e 70% dos atrasos reais. Ou seja, de cada 10 pacotes que vão atrasar, a IA vai flagrar 5 a 7. Os outros 3-5 passam despercebidos.

3. **ROC-AUC esperado: 0.70-0.80.** Um modelo "perfeito" teria 1.0. Um chute aleatório teria 0.5. Com nossos dados, projetamos ficar na faixa de 0.70-0.80, que é classificado como **"bom"** na literatura (não excelente, mas **útil para negócio**).

4. **Os dados não capturam o caos real:** greves dos Correios, chuvas, feriados regionais, falta de motoristas — nada disso está no dataset. Isso coloca um **teto natural** na precisão do modelo.

### Conclusão Final

> O modelo **vale a pena ser construído**. Mesmo com correlações individuais modestas, o XGBoost é projetado exatamente para extrair valor de features fracas em combinação. A `velocidade_lojista_dias` sozinha já garante que o modelo será melhor que um chute aleatório. Se atingirmos ROC-AUC ≥ 0.75 e Recall ≥ 60%, o modelo será uma ferramenta **concreta** para a equipe de logística da Olist priorizar pacotes com alto risco de atraso antes que eles saiam do armazém.

---

*Documento gerado pelo Esquadrão Alpha — Olist Logistics Growth*
