# Imagem base
FROM python:3.12-slim

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar as dependências do projeto
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar o restante do código
COPY . .

# Comando padrão do container (pode ser sobrescrito pelo docker-compose)
CMD ["gunicorn", "havoc.wsgi:application", "--bind", "0.0.0.0:8000"]