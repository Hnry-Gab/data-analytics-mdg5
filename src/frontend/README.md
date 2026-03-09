# Frontend — Olist Logistics

Interface web do projeto de previsão de atrasos logísticos, desenvolvida com **HTML, CSS e JavaScript vanilla**.

## 📁 Estrutura

```
frontend/
├── index.html          # Página principal com 3 abas
├── server.py           # Servidor HTTP para desenvolvimento
├── css/
│   └── style.css       # Estilos gerais
├── js/
│   └── script.js       # Lógica de navegação e predição
└── assets/             # (Imagens, ícones, etc - future use)
```

## 🚀 Como Rodar

### Opção 1: Python HTTP Server (Recomendado)

```bash
cd frontend
python server.py
```

Abrir no navegador: **http://localhost:8000**

### Opção 2: Node.js HTTP Server

```bash
cd frontend
npx http-server
```

### Opção 3: VS Code Live Server

1. Instale a extensão "Live Server"
2. Clique direito em `index.html` → "Open with Live Server"

## 📋 Features Implementadas

### ✅ Painel Gerencial (Dashboard)
- KPIs principais (Total de pedidos, Taxa de atraso, etc)
- Filtro por estado
- Placeholder para mapa de calor

### ✅ Insights
- Cards de descobertas de negócio
- Botões para análises detalhadas (TODO: implementar)

### ✅ Motor de Predição
- Formulário com inputs para:
  - CEP origem/destino
  - Categoria do produto
  - Peso e preço do frete
  - ID do vendedor
- Resultado com probabilidade e status de risco
- Simulação de predição (TODO: conectar com API)

## 🔧 Próximos Passos

### 1. Backend API
Criar endpoints Python/FastAPI para:
- `POST /predict` — Fazer predição com modelo XGBoost
- `GET /metrics` — Buscar métricas do dashboard
- `GET /insights` — Buscar dados de insights

### 2. Integração com ML
- Conectar formulário com endpoint de predição
- Passar dados reais do modelo

### 3. Visualizações
- Gráficos interativos (Chart.js ou D3.js)
- Mapa do Brasil com heatmap

### 4. Dados em Tempo Real
- Dashboard com dados dinâmicos
- Filtros funcionais

## 📝 Modificar

### Adicionar nova aba
1. Criar nova `<section>` no HTML com `data-tab="nome"`
2. Adicionar `<button>` de navegação com `data-tab="nome"`
3. Adicionar CSS com classe `.active`

### Conectar com API
No arquivo `js/script.js`, trocar a função `makePrediction()`:
```javascript
async function makePrediction(data) {
    const response = await fetch('http://localhost:8001/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return await response.json();
}
```

## 🎨 Personalizações

Editar cores em `css/style.css` seção `:root`:
```css
--primary-color: #2563eb;
--secondary-color: #f59e0b;
--success-color: #10b981;
--danger-color: #ef4444;
```

## 🛠️ Dependências

- ✅ Nenhuma dependência externa (vanilla JS)
- Python 3.6+ (para rodar `server.py`)
- Navegador moderno (Chrome, Firefox, Safari, Edge)

---

**Status**: 🚧 Em desenvolvimento  
**Última atualização**: Mar 5, 2026
