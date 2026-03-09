# Getting Started — Olist Analytics

Guia rápido para configurar, rodar e testar o projeto.

---

## Pré-requisitos

- Python 3.10+
- pip (gerenciador de pacotes)
- Git

---

## 1. Clonar e Instalar

```bash
git clone https://github.com/Hnry-Gab/data-analytics-mdg5.git
cd data-analytics-mdg5

# Instalar dependências do MCP server
pip install -r src/olist_mcp/requirementsANALISE.txt

# Instalar dependências do backend (se usar chatbot)
pip install fastapi uvicorn httpx python-dotenv mcp
```

---

## 2. Verificar o Dataset

```bash
python -c "
import pandas as pd
df = pd.read_csv('src/notebooks/dataset_unificado_v1.csv', nrows=5)
print(f'Dataset OK: {df.shape[1]} colunas')
print(f'Target: foi_atraso presente = {\"foi_atraso\" in df.columns}')
"
```

Saída esperada:
```
Dataset OK: 59 colunas
Target: foi_atraso presente = True
```

---

## 3. Testar o MCP Server

### Executar diretamente (stdio)

```bash
cd src
python -m olist_mcp.server
```

O server inicia e aguarda comandos JSON-RPC via stdin. Para sair: `Ctrl+C`.

### Executar testes

```bash
cd src
python -m pytest olist_mcp/tests/ -v --tb=short
```

---

## 4. Integrar com Claude Desktop

Adicione ao `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "olist-analytics": {
      "command": "python",
      "args": ["-m", "olist_mcp.server"],
      "cwd": "/caminho/para/data-analytics-mdg5/src"
    }
  }
}
```

Reinicie o Claude Desktop. As 22 tools aparecerão automaticamente.

### Integrar com Claude Code

```bash
claude mcp add olist-analytics -- python -m olist_mcp.server
```

---

## 5. Rodar o Chatbot (Backend + Frontend)

### Configurar variáveis de ambiente

```bash
cp .env.example .env
# Editar .env com sua chave OpenRouter:
# OPENROUTER_API_KEY=sk-or-v1-...
```

### Iniciar o servidor

```bash
cd src
uvicorn backend.main:app --reload --port 8000
```

Acesse `http://localhost:8000` no navegador.

---

## 6. Exemplos de Perguntas para o Chatbot

| Pergunta | Tool Acionada |
|:--|:--|
| "Qual a taxa de atraso por estado?" | `group_by_metrics` |
| "Quais os 10 vendedores mais problemáticos?" | `top_n_query` |
| "Preveja se esse pedido vai atrasar: SP→MA, 3kg, R$50 frete" | `predict_delay_catboost` |
| "Qual a feature mais importante do modelo?" | `get_catboost_feature_importance` |
| "Mostre o heatmap de rotas" | `generate_route_heatmap` |
| "Compare atrasos de rotas interestaduais vs intraestaduais" | `compare_groups` |
| "Resumo executivo do dataset" | `get_business_summary` |

---

## 7. Estrutura de Diretórios

```
data-analytics-mdg5/
├── docs/                    # Documentação do projeto
│   ├── ARCHITECTURE.md      # Arquitetura e fluxo de dados
│   ├── GETTING_STARTED.md   # Este arquivo
│   ├── algorithms/          # Explicações de algoritmos
│   ├── data/                # Dicionário de dados e relatórios
│   ├── insights/            # Insights de negócio
│   └── spec/                # Especificações técnicas
├── src/
│   ├── backend/             # FastAPI + Chatbot
│   │   ├── chatbot/         # Orchestrator, MCP client, OpenRouter
│   │   ├── api/             # Rotas REST
│   │   └── core/            # Data loader, feature engineering
│   ├── frontend/            # HTML/CSS/JS
│   ├── models/v5/           # CatBoost V5 model artifacts
│   ├── notebooks/           # Pipeline EDA + dataset CSV
│   └── olist_mcp/           # MCP Server (22 tools)
│       ├── cache.py         # DataStore singleton
│       ├── config.py        # Paths e configuração
│       ├── server.py        # Entry point
│       └── tools/           # 6 módulos de tools
└── data/                    # CSVs brutos do Olist (9 tabelas)
```

---

## Troubleshooting

| Problema | Solução |
|:--|:--|
| `ModuleNotFoundError: olist_mcp` | Execute de dentro de `src/`: `cd src && python -m olist_mcp.server` |
| `FileNotFoundError: dataset_unificado_v1.csv` | Verifique se o arquivo existe em `src/notebooks/` |
| MCP server não responde | Verifique se o `cwd` no config aponta para `src/` |
| `catboost` não instalado | `pip install catboost>=1.2.0` |
| Testes falhando | `pip install -r src/olist_mcp/requirementsANALISE.txt` e rode de `src/` |
