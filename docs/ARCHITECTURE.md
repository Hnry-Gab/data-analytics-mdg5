# Arquitetura do Projeto — Olist Analytics

> Visão geral dos componentes, fluxo de dados e integração MCP↔Chatbot.

---

## Diagrama de Alto Nível

```
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND (HTML/CSS/JS)                                     │
│  └─ chat.js → SSE stream ─────────────────────┐             │
└───────────────────────────────────────────────┤─────────────┘
                                                │
                                          POST /chat
                                          SSE stream
                                                │
┌───────────────────────────────────────────────┤─────────────┐
│  BACKEND (FastAPI + Uvicorn)                                │
│                                                             │
│  ┌─────────────┐  ┌──────────────────┐  ┌───────────────┐   │
│  │ routes.py   │→ │ orchestrator.py  │→ │ mcp_client.py │───┤──→ stdio
│  │ (SSE)       │  │ (LLM ↔ Tools)    │  │ (MCP SDK)     │   │
│  └─────────────┘  └──────────────────┘  └───────────────┘   │
│         │                  │                                │
│         │         ┌────────┴────────┐                       │
│         │         │ openrouter_     │                       │
│         │         │ client.py       │                       │
│         │         │ (httpx async)   │                       │
│         │         └────────┬────────┘                       │
│         │                  │                                │
│         │            OpenRouter API                         │
│         │         (Gemini 2.5 Flash Lite)                   │
│  ┌──────┴──────┐                                            │
│  │ session_    │                                            │
│  │ manager.py  │ (in-memory, max 50 msgs, 1h cleanup)       │
│  └─────────────┘                                            │
└─────────────────────────────────────────────────────────────┘
                          │ stdio
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  MCP SERVER (FastMCP, stdio transport)                      │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ DataStore (Singleton, thread-safe, lazy-load)       │    │
│  │  ├─ df()           → DataFrame 109K×59              │    │
│  │  ├─ model()        → CatBoost V5 (.cbm)             │    │
│  │  └─ model_config() → JSON (metrics, features)       │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──────────────┐      │
│  │dataset_ │ │dynamic_ │ │catboost_ │ │business_     │      │
│  │stats(5) │ │query(5) │ │ml(4)     │ │insights(2)   │      │
│  └─────────┘ └─────────┘ └──────────┘ └──────────────┘      │
│  ┌──────────────┐ ┌──────────────┐                          │
│  │visualization │ │calculator(3) │                          │
│  │(7)           │ │              │                          │
│  └──────────────┘ └──────────────┘                          │
│                                                             │
│  Total: 22 tools across 6 modules                           │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  DADOS                                                      │
│  ├─ src/notebooks/dataset_unificado_v1.csv  (109K×59)       │
│  ├─ src/models/v5/catboost_atraso_v5.cbm    (CatBoost)      │
│  ├─ src/models/v5/model_config.json         (métricas)      │
│  └─ src/notebooks/*.html                    (gráficos EDA)  │
└─────────────────────────────────────────────────────────────┘
```

---

## Componentes

### 1. Frontend (`src/frontend/`)
- HTML5 + CSS3 + Vanilla JS
- `chat.js` envia mensagens via `POST /chat` e consome SSE stream
- Renderiza respostas com markdown e gráficos inline

### 2. Backend (`src/backend/`)

| Arquivo | Responsabilidade |
|:--|:--|
| `main.py` | FastAPI app, mount routes, CORS, startup |
| `chatbot/routes.py` | SSE endpoint `/chat`, streaming de tokens |
| `chatbot/orchestrator.py` | Loop LLM↔Tools: recebe prompt, chama LLM, executa tools, retorna resposta |
| `chatbot/mcp_client.py` | Conecta ao MCP server via stdio, converte tools para schema OpenAI |
| `chatbot/openrouter_client.py` | Client HTTP async para OpenRouter (streaming via httpx) |
| `chatbot/session_manager.py` | Histórico de conversação (in-memory, max 50 msgs, cleanup 1h) |
| `chatbot/tool_converter.py` | Converte MCP tool schemas → OpenAI function calling format |
| `chatbot/system_prompt.py` | System prompt com contexto do dataset e instruções |

### 3. MCP Server (`src/olist_mcp/`)

**Transport:** stdio (zero network config — backend spawna como subprocess)

**Framework:** FastMCP + Pydantic

**Caching:** DataStore singleton com lazy-loading thread-safe (~800ms no primeiro load, depois instantâneo)

#### Catálogo de Tools (22)

| Módulo | Tools | Descrição |
|:--|:--|:--|
| **dataset_stats** (5) | `get_dataset_overview`, `get_column_statistics`, `get_dataset_schema`, `search_orders_by_order_id`, `calculate_haversine_distance_tool` | Estatísticas básicas e busca |
| **dynamic_query** (5) | `dynamic_aggregate`, `group_by_metrics`, `top_n_query`, `batch_query`, `compare_groups` | Consultas flexíveis com filtro e agrupamento |
| **catboost_ml** (4) | `predict_delay_catboost`, `get_catboost_model_info`, `get_catboost_feature_importance`, `simulate_scenario` | Predição de atraso e análise do modelo |
| **business_insights** (2) | `get_business_summary`, `get_seller_profile` | Resumos executivos e perfis de vendedores |
| **visualization** (7) | `list_available_charts`, `get_chart_as_base64`, `get_html_chart_content`, `generate_delay_by_state_chart`, `generate_correlation_bar_chart`, `generate_route_heatmap`, `generate_time_series_chart` | Gráficos estáticos e gerados dinamicamente |
| **calculator** (3) | `math_operation`, `percentage_calc`, `calculate_growth` | Operações matemáticas auxiliares |

### 4. Modelo ML (`src/models/v5/`)

- **CatBoost V5** — 19 features, ROC-AUC 0.8454, threshold 0.54
- Detalhes completos em `docs/spec/model_spec.md`

### 5. Pipeline EDA (`src/notebooks/`)

- `dia1_alpha_pipeline.py` — Pipeline completo de EDA (8 seções)
- Gera dataset unificado + gráficos HTML interativos

---

## Fluxo de uma Pergunta do Usuário

```
1. Usuário digita: "Qual o estado com mais atrasos?"
2. chat.js → POST /chat { message, session_id }
3. routes.py abre SSE stream
4. orchestrator.py envia mensagem + tools disponíveis ao LLM (OpenRouter)
5. LLM decide chamar tool: group_by_metrics(group_by="customer_state", metrics=["mean"], column="foi_atraso")
6. orchestrator.py → mcp_client.py → stdio → MCP server
7. MCP server executa query no DataFrame cached → retorna JSON
8. orchestrator.py envia resultado ao LLM como tool_result
9. LLM formula resposta em linguagem natural
10. SSE stream envia tokens progressivos ao frontend
11. chat.js renderiza a resposta com formatação markdown
```

---

## Decisões Arquiteturais

| Decisão | Alternativa Descartada | Motivo |
|:--|:--|:--|
| stdio (MCP transport) | HTTP/SSE | Zero config de rede, subprocess gerenciado pelo backend |
| FastMCP | MCP SDK raw | Menos boilerplate, Pydantic integrado |
| OpenRouter | API direta OpenAI/Google | Acesso a múltiplos modelos com uma API key |
| DataStore singleton | Carregar por request | Dataset de 55MB não pode ser carregado a cada chamada |
| CatBoost nativo categórico | LabelEncoder + XGBoost | +13% ROC-AUC, sem preprocessing manual |
| SMOTE | scale_pos_weight | Melhor generalização para classe minoritária |
