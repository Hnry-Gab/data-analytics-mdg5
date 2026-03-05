# Relatório Final Consolidado — EDA & Feature Engineering

> **Projeto:** Olist Logistics Growth — Previsão de Atrasos
> **Esquadrão:** Alpha (Maurício, Henry, Lucas)
> **Data:** 05/03/2026

---

## 1. Sobre esta pasta

A pasta `final_analysis/` contém a **versão consolidada e definitiva** de toda a análise exploratória realizada pelo Esquadrão Alpha. Todos os arquivos necessários estão aqui — as pastas individuais podem ser removidas sem perda de informação.

### Estrutura dos Arquivos

```
final_analysis/
├── relatorio_final_eda.md          ← ESTE RELATÓRIO (leia primeiro)
├── 01_eda_correlacao_atributos.py   ← Notebook EDA Nichada (Maurício)
├── 01_eda_correlacao_atributos.ipynb ← Versão Jupyter do notebook EDA
├── 02_normalizacao_dados.py         ← Notebook sobre Normalização (Maurício)
├── 02_normalizacao_dados.ipynb      ← Versão Jupyter do notebook Normalização
├── 03_pipeline_completo.py          ← Pipeline de dados completo (Lucas)
├── notas_tecnicas_henry.md          ← Anotações e hipóteses técnicas (Henry)
├── tabela_resumo_correlacoes.csv    ← Ranking final de features (CSV)
├── dataset_treino_v1.csv            ← Dataset de treino final (110k x 7 cols)
└── images/                          ← Gráficos gerados pela EDA
    ├── Força da correlação entre feature candidata vs foi_atraso.png
    ├── Relação entre atrasados e entregues no prazo.png
    ├── Taxa de atraso - Rota Intraestadual vs Interestadual.png
    ├── Taxa de atraso por Estado DO VENDEDOR.png
    ├── Taxa de atraso por estado DO CLIENTE.png
    └── Top 10 categorias com maior taxa de atraso.png
```

---

## 2. O que cada notebook faz

### 01 — EDA Nichada (`01_eda_correlacao_atributos`)
**Autor:** Maurício | **Formato:** .py (executável) + .ipynb (Jupyter)

O notebook principal da análise. Cobre:
1. Carga e merge de 6 tabelas (orders, customers, items, products, sellers, geolocation)
2. Filtro de segurança (apenas `delivered` com data de entrega real)
3. Criação da variável alvo `foi_atraso` (binária)
4. Feature Engineering: 6 features derivadas com hipóteses de negócio
5. Correlação de Pearson/Point-Biserial (numéricas) e Cramér's V (categóricas)
6. Análise de multicolinearidade
7. Tabela-resumo rankeada + gráficos de suporte

**Resultado principal:** Ranking completo das features vs `foi_atraso`.

### 02 — Normalização (`02_normalizacao_dados`)
**Autor:** Maurício | **Formato:** .py + .ipynb

Estudo didático provando que o XGBoost não precisa de normalização:
- Demonstração visual de Min-Max e Z-Score com dados reais
- Prova empírica: XGBoost sem normalizar (ROC-AUC **0.7452**) vs com normalizar (**0.7438**)
- Diferença de **0.0014** (irrelevante)

**Conclusão:** Normalização **não será aplicada** no nosso modelo.

### 03 — Pipeline Completo (`03_pipeline_completo`)
**Autor:** Lucas | **Formato:** .py

Pipeline robusto com etapas adicionais que complementam a EDA do Maurício:
- Tratamento de nulos em products (preenchimento com mediana)
- Feature Engineering expandida (10 features, incluindo `total_itens_pedido`, `ticket_medio_alto`, `seller_regiao`, `customer_regiao`)
- **Piores vendedores** (Top 10 com mínimo 30 pedidos)
- **Piores categorias** de produto (Top 10 com mínimo 100 pedidos)
- **Heatmap de rotas** Estado→Estado (taxa de atraso por origem/destino)
- **Heatmap de macro-regiões** (Norte, Nordeste, Sudeste, Sul, Centro-Oeste)

### Notas Técnicas Henry (`notas_tecnicas_henry`)
**Autor:** Henry | **Formato:** .md

Hipóteses técnicas e sugestões de feature engineering:
- Target Encoding no CEP (com `min_samples_leaf` para evitar overfitting)
- Region Cross (`seller_state + customer_state`) para capturar barreiras fiscais
- Macro-Região Postal (1º dígito do CEP como proxy de região)
- Variáveis de calendário (dia da semana, mês)

---

## 3. Dados Base (Consenso do Squad)

Todos os membros convergiram nos mesmos critérios:

- **Base:** 6 tabelas (orders, customers, items, products, sellers, geolocation)
- **Filtro:** Apenas pedidos `delivered` com `order_delivered_customer_date` não nulo
- **Resultado:** ~110.189 linhas após merge
- **Variável alvo:** `foi_atraso` (1 = atrasou, 0 = no prazo)
- **Desbalanceamento:** 93.41% no prazo vs 6.59% atrasados
- **Métrica principal:** ROC-AUC (acurácia é proibida devido ao desbalanceamento)

---

## 4. Ranking Final Unificado das Features

| # | Feature | Correlação | Método | Status |
|:--|:--|:--|:--|:--|
| 1 | `velocidade_lojista_dias` | **+0.2143** | Pearson | ✅ Obrigatória |
| 2 | `customer_state` (encoded) | **0.1336** | Cramér's V | ✅ Obrigatória |
| 3 | `distancia_haversine_km` | **+0.0753** | Pearson | ⚠️ Forte candidata |
| 4 | `seller_state` (encoded) | **0.0507** | Cramér's V | ⚠️ Candidata |
| 5 | `freight_value` | **+0.0467** | Pearson | ⚠️ Candidata |
| 6 | `rota_interestadual` | **+0.0380** | Pearson | ⚠️ Candidata |

### Features descartadas (com justificativa)

| Feature | Correlação | Motivo |
|:--|:--|:--|
| `volume_cm3` | +0.0222 | Sinal fraco isoladamente |
| `frete_ratio` | +0.0185 | Redundante com `freight_value` |
| `dia_semana_compra` | -0.0106 | Efeito de fim de semana quase nulo |
| `product_category_name` | 0.0324 | Cardinalidade alta, sinal fraco |
| `total_itens_pedido` | -0.0147 | Mais itens por pedido não causa atraso |
| `ticket_medio_alto` | — | Não validado estatisticamente |
| `prazo_estimado_dias` | -0.0626 | Variável óbvia e circular (proxy do sistema antigo) |
| `qtd_parcelas` | +0.004 | Método de pagamento não afeta logística |

---

## 5. Achados de Negócio (para o Esquadrão Omega)

### 5.1 Alagoas lidera os atrasos
Via Target Encoding, **Alagoas (AL) tem 20.84% de taxa de atraso** (3x a média nacional). Seguido por Maranhão (18.00%) e Sergipe (16.27%). O Nordeste domina o ranking de atrasos, confirmando a hipótese de que a infraestrutura logística da região impacta diretamente os prazos.

### 5.2 Piores vendedores
Lucas identificou os Top 10 piores vendedores (mínimo 30 pedidos) com taxas de atraso muito acima da média. **Ação sugerida:** Equipe de operações poderia auditar esses sellers e criar programas de melhoria.

### 5.3 Piores categorias
As categorias com maior taxa de atraso foram identificadas. Categorias volumosas e pesadas (ex: móveis, eletrodomésticos) lideram, confirmando a hipótese de dificuldade logística.

### 5.4 Rotas mais problemáticas
Os heatmaps de rotas revelam que entregas do **Sudeste para o Norte/Nordeste** são as mais problemáticas. As rotas intra-estaduais têm taxa de atraso consistentemente menor que as interestaduais.

---

## 6. Validação Cruzada (Maurício vs Lucas)

| Aspecto | Maurício | Lucas | Convergem? |
|:--|:--|:--|:--|
| Tabelas usadas (6) | ✅ | ✅ | ✅ |
| Filtro `delivered` | ✅ | ✅ | ✅ |
| Variável alvo `foi_atraso` | ✅ | ✅ | ✅ |
| Feature #1 (`velocidade_lojista`) | ✅ | ✅ | ✅ |
| Cálculo Haversine | ✅ | ✅ | ✅ |
| Sem multicolinearidade > 0.7 | ✅ | ✅ | ✅ |
| Desbalanceamento (~93/7%) | ✅ | ✅ | ✅ |

---

## 7. Dataset de Treino Final

**Arquivo:** `dataset_treino_v1.csv`

| Especificação | Valor |
|:--|:--|
| Linhas | 110.189 |
| Colunas | 7 (6 features + target) |
| Valores nulos | 0 (tratados com mediana) |
| Encoding | Target Encoding (estados → taxa de atraso) |
| Normalização | Não aplicada (desnecessária para XGBoost) |

**Colunas finais:**
1. `velocidade_lojista_dias` (float)
2. `distancia_haversine_km` (float)
3. `freight_value` (float)
4. `rota_interestadual` (int: 0 ou 1)
5. `customer_state_encoded` (float: taxa de atraso do estado)
6. `seller_state_encoded` (float: taxa de atraso do estado)
7. `foi_atraso` (int: 0 ou 1) — **TARGET**

---

## 8. Viabilidade do Modelo (Projeção)

Com base na qualidade dos dados e benchmark da prova empírica (notebook 02):

| Métrica | Projeção Realista |
|:--|:--|
| **ROC-AUC** | 0.70 — 0.80 |
| **Recall** | 55% — 70% |

O modelo **é viável** e deve ser capaz de identificar entre 55% e 70% dos atrasos antes que eles aconteçam, permitindo ações preventivas da equipe de logística.

---

## 9. Próximos Passos

- [ ] Treinar XGBoost baseline com as 6 features
- [ ] Tuning de hiperparâmetros (max_depth, n_estimators, learning_rate)
- [ ] Avaliar com ROC-AUC, Recall, F1-Score e Matriz de Confusão
- [ ] Exportar modelo treinado (.pkl)
- [ ] Integrar com Frontend (FastAPI + HTML/CSS/JS)

---

*Relatório consolidado pelo Esquadrão Alpha — Olist Logistics Growth*
