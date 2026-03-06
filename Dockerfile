# Imagem base mais fina do Python 3.10
FROM python:3.10-slim

# Definir diretório de trabalho principal da aplicação
WORKDIR /app

# Variáveis de ambiente para o Python otimizado em contêiner
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependências do sistema necessárias para o catboost e fastapi
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar apenas os requerimentos primeiro para usar cache do Docker
COPY requirements.txt .

# Instalar dependências da aplicação
# Ignoramos dependências de análise de dados pesadas ou jupyter em produção
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o resto da base de código necessária para execução
# Excluímos (.dockerignore resolverá pastas inúteis como spec/ e notebooks/)
COPY src/ /app/src/
COPY frontend/ /app/frontend/
COPY models/v5/ /app/models/v5/
COPY dataset/processed/ /app/dataset/processed/

# Criar o arquivo de ambiente em branco (caso não seja passado, o app roda com defaults do config.py)
RUN touch .env

# Expor a porta que a API usará internamente
EXPOSE 8000

# Comando para iniciar o servidor via Uvicorn (focado em produção, portanto workers podem ser adicionados)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
