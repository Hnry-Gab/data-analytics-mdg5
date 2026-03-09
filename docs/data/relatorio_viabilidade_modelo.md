# Relatório de Viabilidade — Modelo Preditivo de Atrasos Logísticos

> **Data:** 05/03/2026 | **Autor:** Esquadrão Alpha | **Status:** Análise concluída — Modelo CatBoost V5 em produção

---

## 1. Resumo da EDA Nichada

### O que fizemos
Cruzamos 6 tabelas do dataset Olist (orders, customers, items, products, sellers, geolocation) em um DataFrame unificado de **109.637 linhas × 59 colunas**, criamos a variável alvo `foi_atraso` e testamos **22 atributos** (diretos + criados + ocultos) usando Pearson, Point-Biserial e Cramér's V.

### Distribuição da Variável Alvo

| Classe | Quantidade | % |
|:--|:--|:--|
| No prazo (0) | 102.925 | 93,41% |
| Atrasou (1) | 7.264 | 6,59% |

**Dataset fortemente desbalanceado** → Acurácia é métrica proibida. Usamos ROC-AUC, Recall e F1-Score.

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

### Features Fracas (guardadas para testes no treino)

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
| `prazo_estimado_dias` | orders | -0.0626 | Nota: reincluída no CatBoost V5 por contribuir em combinação com outras features |
| `qtd_parcelas` | payments | +0.0045 | Irrelevante — forma de pagamento não afeta logística |
| `qtd_itens` | items | -0.0147 | Mínima — pedidos com vários itens não atrasam mais |
| `product_photos_qty` | products | -0.0020 | Zero sinal |
| `product_name_lenght` | products | +0.0056 | Zero sinal |
| `hora_compra` | orders | +0.0096 | Irrelevante |
| `payment_type` (boleto vs cartão) | payments | 8.6% vs 7.7% | Diferença ínfima entre métodos |

### Multicolinearidade
- `freight_value` ↔ `product_weight_g`: correlação moderada (~0.6) — ambos podem coexistir
- `volume_cm3` ↔ dimensões individuais: alta (~0.7+) — resolvido usando `volume_cm3` em vez das 3 dimensões separadas
- Nenhum par remanescente com correlação > 0.7 → sem redundância grave

---

## 3. Análise de Viabilidade — Faz sentido treinar o modelo?

### A resposta honesta: **SIM, e os resultados confirmaram.**

#### ✅ Pontos a favor (hipóteses da EDA)

1. **Temos uma feature dominante.** A `velocidade_lojista_dias` (Pearson 0.2143) é forte o suficiente para servir de "âncora" do modelo.

2. **Gradient boosting aprende combinações.** O Pearson mede relações individuais e lineares. O CatBoost descobre combinações não-lineares. Exemplo: `velocidade_lojista = 3 dias` E `distancia = 2.500km` E `rota_interestadual = 1` → atraso quase certo.

3. **Volume de dados é adequado.** ~110 mil registros com ~7.200 atrasos, complementados com SMOTE (strategy=0.3, +18.891 amostras sintéticas).

4. **As features são do mundo real.** Velocidade do lojista, distância geográfica e estado do cliente são variáveis operacionais que a equipe de logística controla ou monitora.

#### ✅ Resultados Obtidos (CatBoost V5)

| Métrica | Projeção da EDA | Resultado Real | Status |
|:--|:--|:--|:--|
| ROC-AUC | 0.70–0.80 | **0.8454** | ✅ Superou a projeção |
| Recall | 55–70% | **41.5%** | ⚠️ Abaixo (threshold conservador) |
| F1-Score | — | **0.4676** | ⚠️ Próximo de 0.50 |
| Multiplicador vs Acaso | — | **8.11x** | ✅ Excelente |

O ROC-AUC de 0.8454 **superou** a projeção otimista de 0.80. O Recall ficou abaixo porque o threshold foi calibrado em 0.54 (acima do default 0.50) para priorizar Precision — cada "alerta de atraso" tem mais confiança, reduzindo alarmes falsos.

#### ⚠️ Riscos e limitações confirmados

1. **Correlações individuais fracas se confirmaram.** Das 6 candidatas da EDA, apenas `velocidade_lojista_dias` ultrapassa 0.10. Porém o CatBoost extraiu valor das combinações, validando a hipótese.

2. **Recall de 41.5% significa:** de cada 10 pacotes que vão atrasar, o modelo detecta ~4. Os outros 6 passam despercebidos. Isso é aceitável para **priorização logística** (focar nos 4 detectados), mas não para **garantia de prazo**.

3. **Os dados não capturam caos real:** greves, chuvas, feriados regionais, falta de motoristas — isso coloca um teto natural na precisão.

### Evolução: XGBoost v1 → CatBoost V5

| Aspecto | XGBoost v1 (Baseline) | CatBoost V5 (Final) |
|:--|:--|:--|
| ROC-AUC | 0.7452 | **0.8454** (+13%) |
| Features | 10 (todas numéricas) | **19** (15 num + 4 cat nativas) |
| Balanceamento | `scale_pos_weight` | **SMOTE** (strategy=0.3) |
| Encoding | LabelEncoder manual | **Nativo** (ordered target encoding) |
| Threshold | 0.50 (default) | **0.54** (otimizado F1) |

---

## 4. Conclusão Final

> O modelo **valeu a pena ser construído** e superou as projeções otimistas da EDA. O CatBoost V5 com ROC-AUC 0.8454 e multiplicador 8.11x é uma ferramenta concreta para a equipe de logística priorizar pacotes com alto risco de atraso. A migração de XGBoost para CatBoost trouxe +13% de ROC-AUC graças ao tratamento nativo de categóricas (estado, rota, categoria) e SMOTE para balanceamento.

**Próximos passos sugeridos:**
- Baixar threshold para 0.45–0.48 se Recall > 50% for prioritário
- Adicionar dados externos (feriados, clima) para quebrar o teto natural
- Monitorar drift temporal conforme novos dados entram

---

*Documento gerado pelo Esquadrão Alpha — Olist Logistics Growth*
