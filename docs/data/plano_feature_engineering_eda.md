# Plano: Feature Engineering EDA — Pipeline Geografico, Temporal e Derivado

## Contexto

O notebook `dia1_henry.ipynb` completou o Loop 1 (Tasks 1-4): merge de 5 tabelas, target `foi_atraso` (93.2%/6.8%), correlacoes Pearson. O dataset unificado tem 96,470 pedidos delivered e 31 colunas.

**Problema:** As correlacoes com `foi_atraso` sao fracas (todas < 0.04 exceto `dias_diferenca` que e leakage). Precisamos de features derivadas — geograficas, temporais e operacionais — para dar ao modelo sinais reais de atraso.

**Objetivo:** Plano modular de Feature Engineering EDA, dividido em context windows de densidade media, pronto para implementacao sequencial.

---

## Arquitetura: 3 Context Windows

```
Window 1 (Fundacao)          Window 2 (Geografia)         Window 3 (Documentacao)
+- Task 5: ZIP Normalize     +- Task 8: Region Cross      +- Task 11: Target Encoding
+- Task 6: Macro-Regiao      +- Task 9: Geocoding +           (analise + doc only)
+- Task 7: Calendario        |          Haversine
+- Task 10: Features ALPHA05 +- Task 10b: Export v2.csv
   (volume, frete_ratio,
    velocidade_lojista)
```

**Dependencias:** Task 5 -> Task 6, Task 5 -> Task 9. Tudo mais e independente.

---

## Window 1 — Transformacoes Fundamentais

### Task 5: Normalizacao de Prefixos CEP
- Converter `customer_zip_code_prefix` e `seller_zip_code_prefix` de int64 para string 5 digitos com zero a esquerda
- 24.1% dos customer e 35.9% dos seller tem <5 digitos atualmente
- ALERTA: Qualquer reload futuro do CSV deve usar `dtype=str` para prefixos

### Task 6: Macro-Regiao Postal
- Extrair 1o digito do prefixo normalizado -> `customer_macro_regiao`, `seller_macro_regiao`
- Regioes postais brasileiras: 0-9 representando macro-regioes geograficas
- Achado esperado: regiao '6' (Nordeste interior) ~13% atraso vs '1' (SP metro) ~4.5%

### Task 7: Variaveis de Calendario
- Extrair de `order_purchase_timestamp`: `dia_semana_compra` (0-6) e `mes_compra` (1-12)
- Mes tem sinal forte (marco ~15% vs junho ~2%). Dia da semana sinal fraco (~1.2pp)
- Nota: `mes_compra` deve ser tratado como categorico na modelagem, nao numerico continuo

### Task 10: Features Derivadas do ALPHA-05
- `volume_cm3 = length * height * width` — dropar 18 rows com NaN (0.02%)
- `frete_ratio = freight_value / price` — dropar rows com price==0 se existirem
- `velocidade_lojista_dias = (carrier_date - approved_at).days` — SEMI-LEAKAGE, dropar ~16 rows NaN

---

## Window 2 — Features Geograficas

### Task 8: Region Cross (Rota Interestadual)
- `rota_interestadual = (seller_state != customer_state).astype(int)` — binario
- `rota_seller_customer = seller_state + "_" + customer_state` — 409 combinacoes, alta cardinalidade
- Achado esperado: 64% interestaduais, delay rate ~8% vs 4.5% intraestadual

### Task 9: Geocoding + Haversine
- Carregar `olist_geolocation_dataset.csv` (1M rows, 19k prefixos unicos)
- Filtrar outliers: lat fora de [-34, 6] ou lng fora de [-74, -34] (42 rows)
- Agregar por prefixo: mediana de lat e lng (robusto a outliers)
- Merge por customer e seller zip_code_prefix -> lat/lng
- Calcular distancia Haversine em km (R=6371km)
- NaN: ~478 rows (0.5%) sem match — manter NaN, XGBoost lida nativamente
- Esta e a "Feature Rei" do projeto

---

## Window 3 — Documentacao Target Encoding

### Task 11: Target Encoding (DOC ONLY)
- Encoding real implementado na fase de modelagem (evitar data leakage)
- Documentar: cardinalidade, min_samples_leaf recomendado, snippet de implementacao
- Alternativa: `distancia_haversine_km` + `macro_regiao` ja capturam sinal geografico

---

## Novas Colunas Produzidas

| Coluna | Tipo | Task | Window |
|:--|:--|:--|:--|
| `customer_zip_code_prefix` | str(5) | 5 | 1 |
| `seller_zip_code_prefix` | str(5) | 5 | 1 |
| `customer_macro_regiao` | str(1) | 6 | 1 |
| `seller_macro_regiao` | str(1) | 6 | 1 |
| `dia_semana_compra` | int 0-6 | 7 | 1 |
| `mes_compra` | int 1-12 | 7 | 1 |
| `volume_cm3` | float | 10 | 1 |
| `frete_ratio` | float | 10 | 1 |
| `velocidade_lojista_dias` | float | 10 | 1 |
| `rota_interestadual` | int 0/1 | 8 | 2 |
| `rota_seller_customer` | str | 8 | 2 |
| `customer_lat` | float | 9 | 2 |
| `customer_lng` | float | 9 | 2 |
| `seller_lat` | float | 9 | 2 |
| `seller_lng` | float | 9 | 2 |
| `distancia_haversine_km` | float | 9 | 2 |

**Total:** 14 novas + 2 modificadas. Dataset final: ~44-46 colunas, ~96,450 rows.

---

## Riscos e Alertas

1. **Reload CSV com dtype errado:** Apos normalizar ZIP para string, todo `pd.read_csv()` precisa de `dtype=str`
2. **Outliers geolocalizacao:** 42 rows com coordenadas fora do Brasil. Filtrar com bounding box antes de agregar
3. **`velocidade_lojista_dias` e semi-leakage:** So existe pos-despacho. Marcar com flag no notebook
4. **`rota_seller_customer` alta cardinalidade:** 409 categorias, 196 com <10 amostras. Usar `rota_interestadual` binario como proxy principal
5. **Class imbalance 93/7%:** Nenhuma task de FE resolve isso. Tratar na modelagem (SMOTE, `scale_pos_weight`)

---

## Verificacao End-to-End

1. `df.info()` — confirmar dtypes e non-null counts
2. `df.isnull().sum()` — NaN counts batem com esperado
3. `df.describe()` — ranges fazem sentido (distancia 0-4500km, volume > 0)
4. Correlacao com `foi_atraso` — verificar se features novas tem sinal
5. Salvar `dataset_unificado_v2.csv` e validar shape (~96,450 rows, ~44 cols)
