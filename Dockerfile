# Dockerfile para o projeto Havoc
FROM python:3.12-slim

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    # Dependências básicas
    build-essential \
    curl \
    git \
    # Dependências para PostgreSQL
    libpq-dev \
    # Dependências para MySQL
    default-libmysqlclient-dev \
    pkg-config \
    # Dependências para Pillow (imagens)
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    zlib1g-dev \
    # Dependências para WeasyPrint (PDF)
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libffi-dev \
    shared-mime-info \
    # Utilitários
    gettext \
    wget \
    # Limpeza
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN groupadd -r django && useradd -r -g django django

# Copiar requirements primeiro (para cache do Docker)
COPY requirements.txt requirements-prod.txt ./

# Instalar dependências Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r requirements-prod.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p /app/staticfiles /app/media /app/logs && \
    chown -R django:django /app

# Copiar scripts de entrada
COPY docker/entrypoint.sh /entrypoint.sh
COPY docker/start.sh /start.sh
COPY docker/celery/worker/start.sh /start-celeryworker.sh
COPY docker/celery/beat/start.sh /start-celerybeat.sh
COPY docker/celery/flower/start.sh /start-flower.sh

# Tornar scripts executáveis
RUN chmod +x /entrypoint.sh /start.sh /start-celeryworker.sh /start-celerybeat.sh /start-flower.sh

# Coletar arquivos estáticos
RUN python manage.py collectstatic --noinput --settings=core.settings_prod

# Mudar para usuário não-root
USER django

# Expor porta
EXPOSE 8000

# Definir entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Comando padrão
CMD ["/start.sh"]