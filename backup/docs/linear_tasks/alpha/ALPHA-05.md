# [ALPHA-05] Feature Engineering (Criação de Variáveis Derivadas)

**Responsável:** Henry
**Dia:** 2 (Sexta-feira)
**Prioridade:** 🔴 Crítica
**Branch:** `feat/alpha-05-feature-engineering`

---

## Descrição

Criar as features derivadas (variáveis que não existem nas tabelas originais) que foram mapeadas no guia de atributos. Essas features são o "tempero" que faz o XGBoost alcançar alta performance.

### Features a Criar

| Feature | Fórmula | Tipo |
|:--|:--|:--|
| `volume_cm3` | `product_length_cm * product_height_cm * product_width_cm` | numérica |
| `frete_ratio` | `freight_value / price` | numérica |
| `velocidade_lojista_dias` | `(order_delivered_carrier_date - order_approved_at).days` | numérica |
| `dia_semana_compra` | `order_purchase_timestamp.dt.dayofweek` | numérica (0-6) |
| `rota_interestadual` | `1 se seller_state != customer_state, senão 0` | binária |
| `distancia_haversine_km` | Cálculo via lat/lng do geolocation | numérica |

### Tratamento de Valores Especiais
- `frete_ratio`: Se `price == 0`, preencher com a mediana da coluna.
- `volume_cm3`: Se qualquer dimensão for `NaN`, preencher com a mediana.
- `velocidade_lojista_dias`: Valores negativos (erro de sistema) devem ser removidos.
- `distancia_haversine_km`: Usar a fórmula de Haversine com lat/lng da tabela `geolocation`, fazendo merge pelo `zip_code_prefix`.

### Referências
- `docs/data/atributos_modelo.md` → Lista completa das features
- `spec/data_schema.md` → Schema final esperado

## Critério de Aceite

- [ ] Todas as 6 features criadas sem `NaN` (ou tratados)
- [ ] Nenhum valor infinito (`inf`) nas colunas derivadas
- [ ] DataFrame atualizado e salvo

## Dependências
- ALPHA-04 (revisão anti data-leakage aprovada)

## Entregável
DataFrame enriquecido com as 6 novas colunas
