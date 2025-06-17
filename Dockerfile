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
    netcat-traditional \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar as dependências do projeto
COPY requirements.txt requirements-prod.txt ./
RUN pip install --upgrade pip && pip install -r requirements-prod.txt

# Copiar o restante do código
COPY . .

# Criar diretórios necessários
RUN mkdir -p /app/logs /app/media /app/staticfiles /app/static

# Criar script de entrypoint melhorado
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Função para aguardar banco\n\
wait_for_db() {\n\
    echo "🔍 Aguardando banco de dados ${DB_HOST:-db}:${DB_PORT:-5432}..."\n\
    local max_attempts=60\n\
    local attempt=1\n\
    \n\
    while [ $attempt -le $max_attempts ]; do\n\
        if nc -z ${DB_HOST:-db} ${DB_PORT:-5432}; then\n\
            echo "✅ Banco de dados está disponível!"\n\
            return 0\n\
        fi\n\
        echo "⏳ Tentativa $attempt/$max_attempts - aguardando..."\n\
        sleep 2\n\
        attempt=$((attempt + 1))\n\
    done\n\
    \n\
    echo "❌ Timeout: banco de dados não ficou disponível"\n\
    exit 1\n\
}\n\
\n\
# Função para testar conexão com banco\n\
test_db_connection() {\n\
    echo "🔗 Testando conexão com banco..."\n\
    python manage.py check --database default || {\n\
        echo "❌ Falha na conexão com banco"\n\
        return 1\n\
    }\n\
    echo "✅ Conexão com banco OK!"\n\
}\n\
\n\
# Aguardar banco\n\
wait_for_db\n\
\n\
# Testar conexão\n\
test_db_connection\n\
\n\
echo "📦 Executando migrações..."\n\
python manage.py migrate --noinput\n\
\n\
echo "📁 Coletando arquivos estáticos..."\n\
python manage.py collectstatic --noinput --clear\n\
\n\
echo "👤 Criando superusuário..."\n\
python manage.py create_default_superuser\n\
\n\
echo "🚀 Iniciando aplicação..."\n\
exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120' > /entrypoint.sh && chmod +x /entrypoint.sh

# Expor porta
EXPOSE 8000

# Entrypoint e comando padrão
ENTRYPOINT ["/entrypoint.sh"]
