# Usar imagem leve do Python
FROM python:3.10-slim

# Evitar que o Python gere arquivos .pyc e garantir logs em tempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências de sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação e arquivos estáticos
COPY src/ ./src/
COPY frontend/ ./frontend/
COPY dataset/ ./dataset/
COPY models/ ./models/
COPY run_backend.py .

# Expor a porta que o FastAPI usará
EXPOSE 8000

# Comando para rodar a aplicação em produção
# Usamos workers para melhor performance
CMD ["uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
