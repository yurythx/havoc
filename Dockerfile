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
RUN mkdir -p /app/logs /app/media /app/staticfiles

# Criar script de entrypoint simples
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Aguardando banco de dados..."\n\
while ! nc -z ${DB_HOST:-db} ${DB_PORT:-5432}; do\n\
  sleep 1\n\
done\n\
echo "Executando migrações..."\n\
python manage.py migrate --noinput\n\
echo "Coletando arquivos estáticos..."\n\
python manage.py collectstatic --noinput --clear\n\
echo "Criando superusuário..."\n\
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='\''admin'\'').exists() or User.objects.create_superuser('\''admin'\'', '\''admin@havoc.com'\'', '\''admin123'\'')"\n\
echo "Iniciando aplicação..."\n\
exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3' > /entrypoint.sh && chmod +x /entrypoint.sh

# Expor porta
EXPOSE 8000

# Entrypoint e comando padrão
ENTRYPOINT ["/entrypoint.sh"]
