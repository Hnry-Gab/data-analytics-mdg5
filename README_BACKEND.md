# 🚀 Backend FastAPI - Olist Logistics

Backend em FastAPI para predição de atrasos logísticos, desenvolvido por Douglas.

## 📋 Visão Geral

Este backend fornece:
- **API REST** para predições de atraso
- **Servidor de arquivos estáticos** (HTML/CSS/JS)
- **Integração com XGBoost** para ML
- **Validação de dados** com Pydantic
- **Documentação automática** com Swagger

## 🏗️ Estrutura do Projeto

```
src/
├── main.py                 # Aplicação FastAPI principal
├── config.py               # Configurações
├── models/
│   └── schemas.py          # Schemas Pydantic
├── api/
│   └── routes.py           # Endpoints REST
├── core/
│   ├── ml_model.py         # Carregamento do modelo XGBoost
│   ├── data_loader.py      # Carregamento de dados CSV
│   └── feature_engineering.py  # Processamento de features
├── static/                 # Arquivos HTML/CSS/JS
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js
└── utils/
    ├── logger.py           # Logging
    └── exceptions.py       # Exceções customizadas
```

## ⚙️ Instalação

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

Copie `.env.example` para `.env` e ajuste os valores:

```bash
cp .env.example .env
```

Variáveis importantes:
- `MODEL_PATH`: Caminho para o modelo `.pkl` (do Alpha squad)
- `CSV_PATH`: Caminho para dados históricos
- `PORT`: Porta do servidor (padrão: 8000)

### 3. Preparar Modelo ML

**Importante:** O modelo XGBoost deve ser fornecido pelo **Alpha squad**.

Certifique-se de que existe:
- `models/xgboost_model.pkl` (modelo treinado)
- `data/olist_processed.csv` (opcional, para features)
- `data/olist_geolocation_dataset.csv` (opcional, para distâncias)

## 🚀 Executar o Backend

### Modo Desenvolvimento

```bash
# Opção 1: Usando uvicorn diretamente
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Opção 2: Usando Python
python -m src.main
```

### Modo Produção

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

A API estará disponível em:
- **Frontend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/api/health

## 📡 Endpoints da API

### POST `/api/predict`

Prediz probabilidade de atraso de um pedido.

**Request:**
```json
{
  "cep_cliente": "01310100",
  "cep_vendedor": "20040020",
  "categoria_produto": "eletronicos",
  "peso_produto_kg": 2.5,
  "preco_frete": 15.00,
  "peso_produto_volume_cm3": 5000.0
}
```

**Response:**
```json
{
  "probabilidade_atraso": 23.45,
  "classe_predicao": "No Prazo",
  "confianca": 76.55,
  "features_utilizadas": {
    "distancia_km": 450.5,
    "categoria_encoded": 1,
    "peso_kg": 2.5,
    "preco_frete": 15.00
  }
}
```

### GET `/api/features`

Lista features aceitas pela API.

**Response:**
```json
{
  "features": [
    "cep_cliente",
    "cep_vendedor",
    "categoria_produto",
    "peso_produto_kg",
    "preco_frete",
    "peso_produto_volume_cm3"
  ],
  "description": "Features obrigatórias..."
}
```

### GET `/api/health`

Verifica status da API.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "data_loaded": true
}
```

## 🧪 Testar a API

### Usando cURL

```bash
curl -X POST "http://localhost:8000/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "cep_cliente": "01310100",
    "cep_vendedor": "20040020",
    "categoria_produto": "eletronicos",
    "peso_produto_kg": 2.5,
    "preco_frete": 15.00,
    "peso_produto_volume_cm3": 5000
  }'
```

### Usando Python

```python
import requests

url = "http://localhost:8000/api/predict"
data = {
    "cep_cliente": "01310100",
    "cep_vendedor": "20040020",
    "categoria_produto": "eletronicos",
    "peso_produto_kg": 2.5,
    "preco_frete": 15.00,
    "peso_produto_volume_cm3": 5000.0
}

response = requests.post(url, json=data)
print(response.json())
```

### Usando o Frontend

Acesse http://localhost:8000 e preencha o formulário.

## 🎨 Frontend (HTML/CSS/JS)

Os arquivos estáticos estão em `src/static/`:

- **index.html**: Formulário de predição
- **css/style.css**: Estilos (dark mode, glassmorphism)
- **js/app.js**: Lógica de chamadas à API

**Pablo** será responsável por aprimorar e expandir esses arquivos.

## 📦 Deploy

### Render.com

1. Criar conta em https://render.com
2. Conectar repositório GitHub
3. Configurar:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
4. Adicionar variáveis de ambiente (`MODEL_PATH`, etc.)

### Railway.app

1. Criar conta em https://railway.app
2. Importar repositório
3. Configurar variáveis de ambiente
4. Deploy automático

## 🔧 Troubleshooting

### Modelo não carregado

**Erro:** `Modelo não encontrado: models/xgboost_model.pkl`

**Solução:**
1. Certifique-se de que o Alpha squad gerou o modelo
2. Coloque o arquivo `.pkl` em `models/xgboost_model.pkl`
3. Ou ajuste `MODEL_PATH` no `.env`

### Geolocalização não disponível

**Aviso:** `Geolocalização não carregada`

**Impacto:** Distâncias serão estimadas (1000km padrão)

**Solução:**
1. Baixe `olist_geolocation_dataset.csv` do Kaggle
2. Coloque em `data/olist_geolocation_dataset.csv`

### CORS bloqueado

**Erro:** `CORS policy: No 'Access-Control-Allow-Origin'`

**Solução:** Ajuste `ALLOWED_ORIGINS` em `config.py` ou `.env`

## 📝 Logs

Logs são salvos em:
- **Console:** stdout
- **Arquivo:** `logs/app.log`

Níveis de log: DEBUG, INFO, WARNING, ERROR

## 🤝 Integração com Alpha Squad

Douglas depende do **Alpha squad** para:

1. **Modelo XGBoost treinado** (`xgboost_model.pkl`)
2. **Especificação de features** (`spec/data_schema.md`)
3. **Dados processados** (opcional, para cache)

## 📚 Referências

- **FastAPI:** https://fastapi.tiangolo.com/
- **Pydantic:** https://docs.pydantic.dev/
- **Uvicorn:** https://www.uvicorn.org/
- **XGBoost:** https://xgboost.readthedocs.io/

## 👤 Responsável

**Douglas** - Backend FastAPI + Servir HTML/CSS/JS

**Pablo** - Frontend HTML/CSS/JS (colaboração)

---

**Branch:** `feat/backend-fastapi`
**Status:** ✅ Implementado
