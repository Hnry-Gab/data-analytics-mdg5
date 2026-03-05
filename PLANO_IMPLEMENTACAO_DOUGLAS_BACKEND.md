# 🚀 Plano de Implementação — Backend FastAPI (Douglas)

**Projeto:** Olist Logistics Growth — Previsão de Atrasos
**Responsável:** Douglas
**Colega:** Pablo (Páginas HTML/CSS/JS)
**Branch:** `feat/backend-fastapi`
**Duração:** 4 dias (Quinta → Domingo)
**Status:** Planejamento

---

## 📋 Resumo Executivo

Douglas será responsável por **implementar o Backend em FastAPI** que:
1. Serve arquivos HTML/CSS/JS estáticos (páginas que Pablo criará)
2. Recebe requisições HTTP do Frontend (HTML/JS) com dados de um novo pedido
3. Valida dados de entrada com Pydantic
4. Invoca o modelo XGBoost treinado pelo Alpha para prever risco de atraso
5. Retorna probabilidade de atraso (0-100%) em formato JSON

**Nota Importante:** Não incluir dados mockados. O backend conectará diretamente com:
- Modelo XGBoost pré-treinado (arquivo `.pkl` gerado pelo Alpha)
- Dataset real ou CSV carregado em memória (responsabilidade do Alpha)

---

## 🏗️ Arquitetura do Backend

### Estrutura de Pastas

```
src/
├── main.py                 # Aplicação FastAPI principal (entry point)
├── config.py               # Configurações de ambiente
├── models/
│   ├── __init__.py
│   ├── schemas.py          # Pydantic models para validação
│   └── prediction.py       # Lógica de predição XGBoost
├── api/
│   ├── __init__.py
│   └── routes.py           # Endpoints REST
├── core/
│   ├── __init__.py
│   ├── ml_model.py         # Carregamento e cache do modelo .pkl
│   ├── data_loader.py      # Carregamento do CSV real
│   └── feature_engineering.py  # Transformações de features
├── static/                 # Pasta para servir HTML/CSS/JS estáticos
│   ├── index.html          # Página inicial (será criada por Pablo)
│   ├── css/
│   │   └── style.css       # Estilos (será criado por Pablo)
│   └── js/
│       └── app.js          # Lógica frontend (será criado por Pablo)
├── utils/
│   ├── __init__.py
│   ├── logger.py           # Logging
│   └── exceptions.py       # Exceções customizadas
└── requirements.txt        # Dependências Python
```

---

## 🔧 Implementação Fase por Fase

### **FASE 1: Setup Inicial (Dia 1 — Quinta)**

#### 1.1 Criar Branch
```bash
git checkout -b feat/backend-fastapi
```

#### 1.2 Estrutura de Pastas e Arquivos Base
- [x] Criar diretório `src/` com subpastas conforme acima
- [x] Criar `requirements.txt` com dependências mínimas
- [x] Criar `src/config.py` para variáveis de ambiente

**Dependências Python mínimas:**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pandas==2.1.3
numpy==1.26.2
xgboost==2.0.1
joblib==1.3.2
python-dotenv==1.0.0
```

#### 1.3 Arquivo Principal: `src/main.py`
- Inicializar FastAPI app com CORS habilitado
- Configurar logging
- Servir arquivos estáticos (HTML/CSS/JS) da pasta `src/static/`
- Importar rotas de `api/routes.py`
- Endpoint `/health` para verificação de status

**Exemplo básico:**
```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router
from pathlib import Path

app = FastAPI(title="Olist Logistics API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos (HTML/CSS/JS)
app.mount("/static", StaticFiles(directory="src/static"), name="static")

app.include_router(api_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
async def root():
    """Redireciona para página inicial"""
    return FileResponse("src/static/index.html")
```

---

### **FASE 2: Modelos de Dados e Validação (Dia 1 — Quinta)**

#### 2.1 Criar `src/models/schemas.py`
Define estruturas Pydantic para **validação de entrada/saída**:

```python
from pydantic import BaseModel, Field, validator

class PedidoInput(BaseModel):
    """Dados de entrada para predição de atraso"""
    cep_cliente: str = Field(..., description="CEP do cliente (8 dígitos)")
    cep_vendedor: str = Field(..., description="CEP do vendedor")
    categoria_produto: str = Field(..., description="Categoria do produto")
    peso_produto_kg: float = Field(..., gt=0, description="Peso do produto em kg")
    preco_frete: float = Field(..., gt=0, description="Preço do frete em R$")
    peso_produto_volume_cm3: float = Field(..., gt=0, description="Volume em cm³")
    # Adicionar mais features conforme spec/data_schema.md

class PredictionOutput(BaseModel):
    """Resposta da predição"""
    probabilidade_atraso: float = Field(..., ge=0, le=100, description="Risco de atraso 0-100%")
    classe_predicao: str = Field(..., description="'No Prazo' ou 'Atrasado'")
    confianca: float = Field(..., description="Confiança da predição")
    features_utilizadas: dict = Field(..., description="Features processadas")
```

**Validadores:**
- CEP deve ter 8 dígitos ou ser válido
- Pesos/preços devem ser positivos
- Categoria deve existir no dataset histórico

---

### **FASE 3: Carregamento do Modelo ML (Dia 1 — Quinta-Sexta)**

#### 3.1 Criar `src/core/ml_model.py`
Carrega e **cacheia em memória** o modelo XGBoost:

```python
import joblib
import os
from pathlib import Path

class MLModelLoader:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_model(self, model_path: str):
        """Carrega modelo .pkl do Alpha squad"""
        if self._model is None:
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Modelo não encontrado: {model_path}")
            self._model = joblib.load(model_path)
        return self._model

    def predict(self, features_array):
        """Faz predição e retorna probabilidade"""
        if self._model is None:
            raise RuntimeError("Modelo não carregado")

        proba = self._model.predict_proba(features_array)
        return proba[0][1]  # Probabilidade da classe 1 (atraso)

# Singleton global
ml_model = MLModelLoader()
```

#### 3.2 Criar `src/core/data_loader.py`
Carrega dataset real (CSV) do Alpha:

```python
import pandas as pd
from pathlib import Path

class DataLoader:
    _instance = None
    _data = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_csv(self, csv_path: str) -> pd.DataFrame:
        """Carrega CSV real do Alpha"""
        if self._data is None:
            self._data = pd.read_csv(csv_path)
        return self._data

    def get_feature_stats(self):
        """Retorna estatísticas para normalização"""
        return {
            "mean": self._data.mean().to_dict(),
            "std": self._data.std().to_dict(),
        }

data_loader = DataLoader()
```

---

### **FASE 4: Endpoints REST (Dia 2 — Sexta)**

#### 4.1 Criar `src/api/routes.py`
Define endpoints HTTP que o Frontend chamará:

```python
from fastapi import APIRouter, HTTPException
from models.schemas import PedidoInput, PredictionOutput
from core.ml_model import ml_model
from core.feature_engineering import process_features

router = APIRouter(prefix="/api", tags=["Predição"])

@router.post("/predict", response_model=PredictionOutput)
async def predict_delay(pedido: PedidoInput) -> PredictionOutput:
    """
    Prediz probabilidade de atraso para um novo pedido

    Entrada: Dados do pedido (CEP cliente, vendedor, categoria, peso, frete)
    Saída: Probabilidade de atraso (0-100%)
    """
    try:
        # 1. Validar entrada (Pydantic já faz)
        # 2. Processar features
        features = process_features(pedido)

        # 3. Invocar modelo XGBoost
        prob_atraso = ml_model.predict(features)
        prob_percent = prob_atraso * 100

        # 4. Retornar resultado
        return PredictionOutput(
            probabilidade_atraso=prob_percent,
            classe_predicao="Atrasado" if prob_percent > 50 else "No Prazo",
            confianca=max(prob_atraso, 1 - prob_atraso) * 100,
            features_utilizadas=pedido.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/features")
async def get_available_features():
    """Retorna lista de features aceitas"""
    return {
        "features": [
            "cep_cliente", "cep_vendedor", "categoria_produto",
            "peso_produto_kg", "preco_frete", "peso_produto_volume_cm3"
        ]
    }
```

**Endpoints principais:**
- `POST /api/predict` — Predição principal (chamada pelo Simulador)
- `GET /api/features` — Lista de features aceitas
- `GET /health` — Status do backend

---

### **FASE 5: Feature Engineering (Dia 2 — Sexta)**

#### 5.1 Criar `src/core/feature_engineering.py`
Transforma dados de entrada em features do modelo:

```python
import pandas as pd
import numpy as np
from models.schemas import PedidoInput

def process_features(pedido: PedidoInput) -> np.ndarray:
    """
    Converte PedidoInput em array de features para o XGBoost

    Etapas:
    1. Extrair coordenadas geográficas dos CEPs
    2. Calcular distância (cliente → vendedor)
    3. Normalizar features numéricas
    4. Encod variáveis categóricas
    """

    features_dict = {
        "distancia_km": calcular_distancia(pedido.cep_cliente, pedido.cep_vendedor),
        "categoria_encoded": encode_categoria(pedido.categoria_produto),
        "peso_kg": pedido.peso_produto_kg,
        "preco_frete": pedido.preco_frete,
        "volume_cm3": pedido.peso_produto_volume_cm3,
        "preco_por_peso": pedido.preco_frete / pedido.peso_produto_kg,
    }

    # Normalizar conforme estatísticas históricas
    df = pd.DataFrame([features_dict])
    # df = normalize(df)  # Usar StandardScaler se necessário

    return df.values

def calcular_distancia(cep1: str, cep2: str) -> float:
    """Calcula distância euclidiana entre CEPs (usar geolocation data)"""
    # TODO: Usar dataset olist_geolocation_dataset
    pass

def encode_categoria(categoria: str) -> int:
    """Encoda categoria textual para número"""
    # TODO: Mapeamento da categoria para número
    pass
```

---

### **FASE 6: Servir Páginas HTML Estáticas (Dia 2-3 — Sexta-Sábado)**

#### 6.1 Configurar `StaticFiles` no FastAPI
O arquivo `src/main.py` já terá:
```python
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="src/static"), name="static")
```

#### 6.2 Estrutura de Pastas para Estáticos
- `src/static/index.html` — Página inicial
- `src/static/css/style.css` — Estilos globais
- `src/static/js/app.js` — Lógica do frontend

**Responsabilidades:**
- **Douglas:** Servir os arquivos estáticos via FastAPI
- **Pablo:** Criar os arquivos HTML/CSS/JS

#### 6.3 Exemplo de HTML (criado por Pablo)
```html
<!-- src/static/index.html -->
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Olist Logistics - Simulador</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div id="app">
        <form id="predictionForm">
            <input type="text" name="cep_cliente" placeholder="CEP Cliente" required>
            <input type="text" name="cep_vendedor" placeholder="CEP Vendedor" required>
            <input type="text" name="categoria_produto" placeholder="Categoria" required>
            <input type="number" name="peso_produto_kg" placeholder="Peso (kg)" step="0.01" required>
            <input type="number" name="preco_frete" placeholder="Frete (R$)" step="0.01" required>
            <input type="number" name="peso_produto_volume_cm3" placeholder="Volume (cm³)" step="1" required>
            <button type="submit">Prever Atraso</button>
        </form>
        <div id="result"></div>
    </div>
    <script src="/static/js/app.js"></script>
</body>
</html>
```

#### 6.4 Exemplo de JavaScript (criado por Pablo)
```javascript
// src/static/js/app.js
document.getElementById('predictionForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);

    const response = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    const result = await response.json();
    document.getElementById('result').innerHTML =
        `Probabilidade de Atraso: ${result.probabilidade_atraso.toFixed(2)}%`;
});
```

---

### **FASE 7: Testes e Deploy (Dia 3-4 — Sábado-Domingo)**

#### 7.1 Testes Locais
```bash
# Iniciar backend
uvicorn src.main:app --reload

# Testar endpoint
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

#### 7.2 Deploy em Render/Railway
1. Criar account em Render.com ou Railway.app
2. Conectar repositório GitHub
3. Configurar variáveis de ambiente (caminho do modelo `.pkl`)
4. Deploy automático na branch `feat/backend-fastapi`

**Variáveis de ambiente (`.env`):**
```
MODEL_PATH=./models/xgboost_model.pkl
CSV_PATH=./data/olist_processed.csv
ENVIRONMENT=development
DEBUG=False
```

---

## 📦 Entrega de Arquivo: Modelo XGBoost

**Do squad Alpha para Douglas:**
- Arquivo: `models/xgboost_model.pkl` (modelo treinado)
- Arquivo: `data/olist_processed.csv` (ou estrutura de features)
- Documentação: `spec/data_schema.md` (features esperadas, ordem)

**Douglas aguarda:**
- ✅ Modelo `.pkl` treinado
- ✅ CSV com dados históricos (opcional, para cache)
- ✅ Especificação exata de features em `spec/data_schema.md`

---

## 🎯 Divisão de Responsabilidades: Douglas vs Pablo

### Frontend → Backend Flow

```
[Páginas HTML/CSS/JS estáticas]
        ↓
[Validação JS local]
        ↓
[Fetch POST /api/predict]
        ↓
[Backend processa]
        ↓
[Retorna JSON com probabilidade]
        ↓
[Frontend exibe resultado]
```

**Douglas (Backend) responsável:**
- Criar FastAPI app em `src/main.py` com CORS habilitado
- Servir arquivos estáticos (HTML/CSS/JS) da pasta `src/static/`
- Implementar endpoints `/api/predict`, `/api/features`, `/health`
- Validação de entrada com Pydantic
- Integração com XGBoost do Alpha
- Feature engineering

**Pablo (Frontend) responsável:**
- Criar HTML/CSS/JS em `src/static/` (páginas ainda não existem)
- Formulários web para coleta de dados
- Chamadas Fetch para `POST /api/predict`
- Exibição de resultados (probabilidade de atraso)
- Design responsivo com CSS vanilla

---

## ✅ Checklist de Implementação

### Dia 1 (Quinta)
- [ ] Branch `feat/backend-fastapi` criada
- [ ] Estrutura de pastas criada
- [ ] `requirements.txt` finalizado
- [ ] `src/main.py` com FastAPI app + StaticFiles
- [ ] `src/models/schemas.py` com Pydantic models
- [ ] `src/core/ml_model.py` implementado
- [ ] `src/core/data_loader.py` implementado
- [ ] Pasta `src/static/` criada (vazia, aguardando Pablo)

### Dia 2 (Sexta)
- [ ] `src/api/routes.py` com endpoints `/predict`, `/features`, `/health`
- [ ] `src/core/feature_engineering.py` implementado
- [ ] Testes locais com `uvicorn` funcionando
- [ ] CORS habilitado
- [ ] Documentação automática Swagger em `/docs`
- [ ] StaticFiles servindo arquivos estáticos corretamente

### Dia 3 (Sábado)
- [ ] Deploy em Render/Railway iniciado
- [ ] Testes de integração com Frontend (HTML/CSS/JS de Pablo)
- [ ] Variáveis de ambiente configuradas
- [ ] Endpoints validando dados corretamente

### Dia 4 (Domingo)
- [ ] Testes E2E (Frontend + Backend)
- [ ] Ajustes finais de performance
- [ ] Documentação API finalizada
- [ ] PR para `main` criada e revisada

---

## 🔗 Referências

- **Stack Técnico:** `spec/stack.md`
- **Escopo do Projeto:** `spec/project_spec.md`
- **Schema de Dados:** `spec/data_schema.md`
- **Modelo ML:** `spec/model_spec.md`
- **Documentação FastAPI:** https://fastapi.tiangolo.com/
- **Documentação Pydantic:** https://docs.pydantic.dev/
- **Documentação StaticFiles:** https://fastapi.tiangolo.com/tutorial/static-files/

---

## 📝 Notas Importantes

1. **Sem Mock Data:** Backend conecta diretamente com XGBoost real do Alpha squad
2. **Servir HTML Estáticos:** FastAPI serve arquivos da pasta `src/static/` (criados por Pablo)
3. **CORS Habilitado:** Frontend (HTML/JS) rodará em origin diferente
4. **Singleton Pattern:** Modelo e CSV carregados UMA VEZ em memória (performance)
5. **Async/Await:** FastAPI é assíncrono; usar `async def` nos endpoints
6. **Pydantic Validation:** Erros de validação retornam HTTP 422 automaticamente
7. **Swagger Automático:** FastAPI gera documentação em `/docs`
8. **Arquivos Estáticos:** Usar `app.mount("/static", ...)` para servir HTML/CSS/JS

---

**Status:** ✅ Plano Finalizado
**Data:** 05/03/2026
**Responsável:** Douglas
**Revisado por:** [Pendente]
