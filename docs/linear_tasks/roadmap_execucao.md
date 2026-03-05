# Roadmap de Execução — Ordem Otimizada para Mínimo Bloqueio

> Este documento organiza os 23 cards do projeto na ordem exata de execução, destacando o que roda em **paralelo** e o que **bloqueia** o próximo passo. Cada card possui sua própria branch.

---

## Dia 1 — Quinta-feira

### Bloco 1 (Manhã) — Início Simultâneo, Zero Dependência

| Ordem | Card | Responsável | Branch | Depende de |
|:--|:--|:--|:--|:--|
| 🟢 | **ALPHA-01** Merge das tabelas | Henry, Lucas | `feat/alpha-01-merge-tabelas` | — |
| 🟢 | **DELTA-01** Setup Frontend/FastAPI + 3 abas | Pablo | `feat/delta-01-Frontend/FastAPI-setup` | — |
| 🟢 | **OMEGA-02** Índice da apresentação | Anderson, Gabriel | `docs/omega-02-indice-apresentacao` | — |

### Bloco 2 (Tarde) — Após ALPHA-01

| Ordem | Card | Responsável | Branch | Depende de |
|:--|:--|:--|:--|:--|
| ⏩ | **ALPHA-02** Criar variável alvo | Henry, Lucas | `feat/alpha-02-variavel-alvo` | ALPHA-01 |
| 🟢 | **DELTA-02** Dados mockados | Douglas | `feat/delta-02-dados-mockados` | DELTA-01 |

### Bloco 3 (Final do Dia) — Após ALPHA-02

| Ordem | Card | Responsável | Branch | Depende de |
|:--|:--|:--|:--|:--|
| ⏩ | **ALPHA-03** Correlações de Pearson | Henry | `feat/alpha-03-correlacoes-pearson` | ALPHA-02 |
| ⏩ | **ALPHA-04** Revisão anti data-leakage | Mauricio | `feat/alpha-04-revisao-leakage` | ALPHA-02 |
| ⏩ | **OMEGA-01** Analisar gráficos do Alpha | Anderson, Gabriel | `docs/omega-01-analise-graficos` | ALPHA-03 |

### Entregáveis do Dia 1
- [ ] CSV unificado com variável alvo (`foi_atraso`)
- [ ] Frontend/FastAPI rodando localmente com mockups
- [ ] Primeiras correlações e índice de slides definido

---

## Dia 2 — Sexta-feira

### Bloco 4 (Manhã)

| Ordem | Card | Responsável | Branch | Depende de |
|:--|:--|:--|:--|:--|
| ⏩ | **ALPHA-05** Feature Engineering | Henry | `feat/alpha-05-feature-engineering` | ALPHA-04 |
| 🟢 | **DELTA-03** Plugar CSV real (Aba 1) | Pablo, Douglas | `feat/delta-03-csv-real` | ALPHA-01 |

### Bloco 5 (Meio do Dia)

| Ordem | Card | Responsável | Branch | Depende de |
|:--|:--|:--|:--|:--|
| ⏩ | **ALPHA-06** Seleção top features | Henry | `feat/alpha-06-selecao-features` | ALPHA-05 |
| 🟢 | **DELTA-04** Gráficos Plotly (Aba 1) | Pablo, Douglas | `feat/delta-04-graficos-plotly` | DELTA-03 |
| ⏩ | **OMEGA-03** Narrativa de negócio | Anderson, Gabriel | `docs/omega-03-narrativa-negocios` | ALPHA-06 |

### Bloco 6 (Tarde)

| Ordem | Card | Responsável | Branch | Depende de |
|:--|:--|:--|:--|:--|
| ⏩ | **ALPHA-07** Split treino/teste | Mauricio, Lucas | `feat/alpha-07-split-treino-teste` | ALPHA-06 |
| ⏩ | **ALPHA-08** Treinar baseline XGBoost | Mauricio | `feat/alpha-08-baseline-xgboost` | ALPHA-07 |

### Entregáveis do Dia 2
- [ ] Features criadas e selecionadas
- [ ] Primeiro modelo baseline treinado
- [ ] Aba 1 do Frontend/FastAPI com gráficos reais
- [ ] Narrativa de negócio redigida

---

## Dia 3 — Sábado

### Bloco 7 (Manhã)

| Ordem | Card | Responsável | Branch | Depende de |
|:--|:--|:--|:--|:--|
| ⏩ | **ALPHA-09** Tuning hiperparâmetros | Mauricio | `feat/alpha-09-tuning-modelo` | ALPHA-08 |
| ⏩ | **ALPHA-10** Feature Importance | Henry | `feat/alpha-10-feature-importance` | ALPHA-09 |
| 🟢 | **DELTA-05** Aba 2 — Insights | Douglas | `feat/delta-05-aba-insights` | OMEGA-03 |

### Bloco 8 (Tarde) — Momento Crítico: `.pkl` libera o Simulador

| Ordem | Card | Responsável | Branch | Depende de |
|:--|:--|:--|:--|:--|
| ⏩ | **ALPHA-11** Exportar modelo `.pkl` | Mauricio | `feat/alpha-11-exportar-modelo` | ALPHA-09 |
| ⏩ | **DELTA-06** Aba 3 — Simulador | Pablo | `feat/delta-06-simulador-predicao` | ALPHA-11 |
| 🟢 | **OMEGA-04** Slides com dados reais | Anderson, Gabriel | `docs/omega-04-slides-dados-reais` | ALPHA-10 |

### Entregáveis do Dia 3
- [ ] Modelo otimizado e exportado `.pkl`
- [ ] Simulador de Predição funcional
- [ ] Slides 90% preenchidos

---

## Dia 4 — Domingo

### Bloco 9 (Manhã)

| Ordem | Card | Responsável | Branch | Depende de |
|:--|:--|:--|:--|:--|
| ⏩ | **DELTA-07** Deploy Render/Vercel | Pablo | `feat/delta-07-deploy` | DELTA-06 |

### Bloco 10 (Tarde)

| Ordem | Card | Responsável | Branch | Depende de |
|:--|:--|:--|:--|:--|
| ⏩ | **OMEGA-05** Ensaio geral | Todos | — | Todos |

### Entregáveis do Dia 4
- [ ] App publicado (URL pública)
- [ ] Apresentação ensaiada e cronometrada

---

## Mapa Completo de Branches (23)

### Esquadrão Alpha (11 branches)

| Branch | Card | Dia |
|:--|:--|:--|
| `feat/alpha-01-merge-tabelas` | ALPHA-01 | 1 |
| `feat/alpha-02-variavel-alvo` | ALPHA-02 | 1 |
| `feat/alpha-03-correlacoes-pearson` | ALPHA-03 | 1 |
| `feat/alpha-04-revisao-leakage` | ALPHA-04 | 1 |
| `feat/alpha-05-feature-engineering` | ALPHA-05 | 2 |
| `feat/alpha-06-selecao-features` | ALPHA-06 | 2 |
| `feat/alpha-07-split-treino-teste` | ALPHA-07 | 2 |
| `feat/alpha-08-baseline-xgboost` | ALPHA-08 | 2 |
| `feat/alpha-09-tuning-modelo` | ALPHA-09 | 3 |
| `feat/alpha-10-feature-importance` | ALPHA-10 | 3 |
| `feat/alpha-11-exportar-modelo` | ALPHA-11 | 3 |

### Esquadrão Delta (7 branches)

| Branch | Card | Dia |
|:--|:--|:--|
| `feat/delta-01-Frontend/FastAPI-setup` | DELTA-01 | 1 |
| `feat/delta-02-dados-mockados` | DELTA-02 | 1 |
| `feat/delta-03-csv-real` | DELTA-03 | 2 |
| `feat/delta-04-graficos-plotly` | DELTA-04 | 2 |
| `feat/delta-05-aba-insights` | DELTA-05 | 3 |
| `feat/delta-06-simulador-predicao` | DELTA-06 | 3 |
| `feat/delta-07-deploy` | DELTA-07 | 4 |

### Esquadrão Omega (5 branches)

| Branch | Card | Dia |
|:--|:--|:--|
| `docs/omega-01-analise-graficos` | OMEGA-01 | 1 |
| `docs/omega-02-indice-apresentacao` | OMEGA-02 | 1 |
| `docs/omega-03-narrativa-negocios` | OMEGA-03 | 2 |
| `docs/omega-04-slides-dados-reais` | OMEGA-04 | 3 |
| — | OMEGA-05 (ensaio presencial) | 4 |

---

## Legenda

- 🟢 = Pode iniciar sem esperar ninguém (paralelo)
- ⏩ = Depende de um card anterior (sequencial)
