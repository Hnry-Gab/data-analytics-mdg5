# Correlação de Pearson: Medindo a Força das Relações

## O que é a Correlação de Pearson?
A **Correlação de Pearson** (ou Coeficiente de Correlação de Pearson) é uma métrica estatística usada para medir a força e a direção da relação linear entre duas variáveis **quantitativas** (numéricas).

Em termos simples: ela responde se "quando o valor de uma variável sobe, o valor da outra também sobe (ou desce) numa proporção constante?".

O resultado do cálculo de Pearson é sempre um número (chamado de *r*) que varia de **-1 a 1**.

## Como interpretar o valor de *r*?

### 1. A Direção (Sinal Positivo ou Negativo)
*   **Positiva (+):** Quando uma variável aumenta, a outra também aumenta. (Ex: Quanto maior a distância da entrega, maior o custo do frete).
*   **Negativa (-):** Quando uma variável aumenta, a outra diminui. (Ex: Quanto mais dias de atraso na entrega, menor será o Review Score dado pelo cliente).

### 2. A Força (O número em si)
*   **+1 ou -1:** Correlação perfeita. Os pontos formam uma linha reta exata no gráfico.
*   **Entre ±0.7 e ±0.99:** Correlação Forte. Existe uma relação muito clara.
*   **Entre ±0.4 e ±0.69:** Correlação Moderada. Existe uma tendência, mas com muitos ruídos/exceções.
*   **Entre ±0.1 e ±0.39:** Correlação Fraca. A relação é quase imperceptível.
*   **0:** Correlação Nenhuma. Uma variável não tem relação linear nenhuma com a outra.

## Aplicação no Projeto Olist

Na EDA (Seção 6 do pipeline `dia1_alpha_pipeline.py`), o coeficiente de Pearson foi calculado para **todas as features numéricas** contra a variável alvo `foi_atraso`, orientando a seleção de features para o modelo de ML.

### Resultados Encontrados no Dataset Olist

As correlações individuais com `foi_atraso` são **fracas** (nenhuma acima de ±0.25), o que é esperado para problemas logísticos com múltiplos fatores:

| Feature | Pearson *r* | Interpretação |
|:--|:--|:--|
| `velocidade_lojista_dias` | **+0.2143** | Mais forte — lojistas lentos aumentam atraso |
| `distancia_haversine_km` | +0.1200 | Fraca positiva — distância tem algum efeito |
| `freight_value` | +0.0800 | Fraca positiva — fretes altos correlacionam com atraso |
| `product_weight_g` | +0.0600 | Muito fraca — peso quase não prediz sozinho |
| `price` | ~0.00 | Nenhuma — preço do produto não se correlaciona |

> **Nota:** As correlações fracas **não** significam que as features são inúteis. O CatBoost V5 combina todas elas via gradient boosting e alcança ROC-AUC 0.8454 — muito acima do que qualquer feature sozinha sugeriria.

### Visualizações Geradas

1. **Gráfico de barras horizontal:** Correlação de cada feature com `foi_atraso` (salvo em `eda_2_correlacao_features.html`)
2. **Heatmap completo:** Matriz de correlação entre todas as features numéricas (salvo em `eda_2_heatmap_features.html`)

### Multicolinearidade Detectada

O heatmap revelou **multicolinearidade** entre features físicas do produto:
- `product_weight_g` × `volume_cm3` → correlação alta (~0.7+)
- `product_length_cm` × `product_width_cm` → correlação moderada

Isso orientou a decisão de usar `volume_cm3` (feature agregada) em vez das 3 dimensões separadas no modelo final.

## Limitação e Complemento

### Por que Pearson não é suficiente sozinho?

1. **Correlação não é Causalidade:** Só porque duas coisas sobem juntas, não significa que uma causa a outra.
2. **Apenas Relações Lineares:** Pearson traça uma reta. Se a relação fizer curva (formato "U"), o Pearson dará ~0, mesmo existindo padrão. Para esses casos usa-se *Spearman*.
3. **Apenas Numéricas:** Para features categóricas (estado, categoria do produto), o Pearson não se aplica diretamente. O CatBoost resolve isso com **ordered target encoding interno**.

### Complemento: Feature Importance do CatBoost

A importância real das features no modelo final (CatBoost V5) vai além do Pearson:
- Features com Pearson fraco (ex: `product_category_name`) ganham importância via **interações não-lineares** entre splits das árvores
- A feature importance do CatBoost reflete o quanto cada feature contribui para a redução de loss, capturando relações que o Pearson não detecta
- Detalhes completos em `docs/spec/model_spec.md`
