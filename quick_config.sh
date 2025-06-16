#!/bin/bash

# =============================================================================
# CONFIGURAÇÃO RÁPIDA - HAVOC DEPLOY
# Configurações pré-definidas para diferentes cenários
# =============================================================================

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 CONFIGURAÇÃO RÁPIDA HAVOC${NC}"
echo "=============================="
echo ""

# Função para gerar SECRET_KEY
generate_secret_key() {
    if command -v python3 >/dev/null 2>&1; then
        python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
    else
        openssl rand -base64 50 | tr -d "=+/" | cut -c1-50
    fi
}

# Função para obter IP público
get_public_ip() {
    curl -s --max-time 5 ifconfig.me 2>/dev/null || echo "localhost"
}

echo "Escolha uma configuração pré-definida:"
echo ""
echo "1) 🧪 Desenvolvimento Local (SQLite, Console Email)"
echo "2) 🌐 Servidor de Teste (PostgreSQL, SMTP)"
echo "3) 🚀 Produção (PostgreSQL, SMTP, Redis, HTTPS)"
echo "4) ⚙️  Configuração Personalizada (interativa)"
echo ""

read -p "Escolha uma opção (1-4): " choice

case $choice in
    1)
        echo -e "${YELLOW}📝 Configurando para DESENVOLVIMENTO LOCAL...${NC}"
        
        SECRET_KEY=$(generate_secret_key)
        PUBLIC_IP=$(get_public_ip)
        
        cat > .env << EOF
# =============================================================================
# CONFIGURAÇÃO RÁPIDA - DESENVOLVIMENTO LOCAL
# Gerado em: $(date)
# =============================================================================

# Ambiente
ENVIRONMENT=development
DEBUG=True

# Segurança
SECRET_KEY=$SECRET_KEY
ALLOWED_HOSTS=localhost,127.0.0.1,$PUBLIC_IP
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://$PUBLIC_IP:8000

# Banco de dados (SQLite)
DATABASE_ENGINE=sqlite
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

# Email (Console)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_USE_TLS=False
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@havoc.local

# Cache (Desabilitado)
REDIS_URL=

# HTTPS (Desabilitado)
SECURE_SSL_REDIRECT=False

# Arquivos
STATIC_ROOT=/app/staticfiles
MEDIA_ROOT=/app/media

# Logs
LOG_LEVEL=DEBUG
LOG_FILE=/app/logs/django.log

# Site
SITE_NAME=Havoc Dev
SITE_URL=http://localhost:8000

# Upload
FILE_UPLOAD_MAX_MEMORY_SIZE=5242880
DATA_UPLOAD_MAX_MEMORY_SIZE=5242880

# Container
DJANGO_SETTINGS_MODULE=core.settings_prod
GUNICORN_WORKERS=2
GUNICORN_BIND=0.0.0.0:8000
GUNICORN_TIMEOUT=120
EOF
        
        echo -e "${GREEN}✅ Configuração de desenvolvimento criada!${NC}"
        echo "📝 Arquivo .env criado com SQLite e email console"
        ;;
        
    2)
        echo -e "${YELLOW}📝 Configurando para SERVIDOR DE TESTE...${NC}"
        
        SECRET_KEY=$(generate_secret_key)
        PUBLIC_IP=$(get_public_ip)
        DB_PASSWORD=$(openssl rand -base64 12)
        
        echo ""
        read -p "🔧 Nome do banco [havoc_test]: " db_name
        db_name=${db_name:-havoc_test}
        
        read -p "🔧 Usuário do banco [havoc_user]: " db_user
        db_user=${db_user:-havoc_user}
        
        read -p "📧 Email SMTP (opcional): " email_user
        read -s -p "🔐 Senha email (opcional): " email_pass
        echo ""
        
        cat > .env << EOF
# =============================================================================
# CONFIGURAÇÃO RÁPIDA - SERVIDOR DE TESTE
# Gerado em: $(date)
# =============================================================================

# Ambiente
ENVIRONMENT=production
DEBUG=False

# Segurança
SECRET_KEY=$SECRET_KEY
ALLOWED_HOSTS=localhost,127.0.0.1,$PUBLIC_IP
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://$PUBLIC_IP:8000

# Banco de dados (PostgreSQL)
DATABASE_ENGINE=postgresql
DB_NAME=$db_name
DB_USER=$db_user
DB_PASSWORD=$DB_PASSWORD
DB_HOST=db
DB_PORT=5432

# Email
EMAIL_BACKEND=$([ -n "$email_user" ] && echo "django.core.mail.backends.smtp.EmailBackend" || echo "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=$email_user
EMAIL_HOST_PASSWORD=$email_pass
DEFAULT_FROM_EMAIL=${email_user:-noreply@havoc.local}

# Cache (Redis)
REDIS_URL=redis://redis:6379/1

# HTTPS (Desabilitado)
SECURE_SSL_REDIRECT=False

# Arquivos
STATIC_ROOT=/app/staticfiles
MEDIA_ROOT=/app/media

# Logs
LOG_LEVEL=INFO
LOG_FILE=/app/logs/django.log

# Site
SITE_NAME=Havoc Test
SITE_URL=http://$PUBLIC_IP:8000

# Upload
FILE_UPLOAD_MAX_MEMORY_SIZE=5242880
DATA_UPLOAD_MAX_MEMORY_SIZE=5242880

# Container
DJANGO_SETTINGS_MODULE=core.settings_prod
GUNICORN_WORKERS=3
GUNICORN_BIND=0.0.0.0:8000
GUNICORN_TIMEOUT=120
EOF
        
        echo -e "${GREEN}✅ Configuração de teste criada!${NC}"
        echo "📝 Arquivo .env criado com PostgreSQL e Redis"
        echo "🔐 Senha do banco: $DB_PASSWORD"
        ;;
        
    3)
        echo -e "${YELLOW}📝 Configurando para PRODUÇÃO...${NC}"
        
        SECRET_KEY=$(generate_secret_key)
        PUBLIC_IP=$(get_public_ip)
        DB_PASSWORD=$(openssl rand -base64 16)
        
        echo ""
        read -p "🌐 Domínio do site (ex: meusite.com): " domain
        read -p "🔧 Nome do banco [havoc_prod]: " db_name
        db_name=${db_name:-havoc_prod}
        
        read -p "🔧 Usuário do banco [havoc_user]: " db_user
        db_user=${db_user:-havoc_user}
        
        read -p "📧 Email SMTP: " email_user
        read -s -p "🔐 Senha email: " email_pass
        echo ""
        
        # Configurar hosts
        if [ -n "$domain" ]; then
            allowed_hosts="localhost,127.0.0.1,$PUBLIC_IP,$domain,www.$domain"
            csrf_origins="http://localhost:8000,http://$PUBLIC_IP:8000,https://$domain,https://www.$domain"
            site_url="https://$domain"
        else
            allowed_hosts="localhost,127.0.0.1,$PUBLIC_IP"
            csrf_origins="http://localhost:8000,http://$PUBLIC_IP:8000"
            site_url="http://$PUBLIC_IP:8000"
        fi
        
        cat > .env << EOF
# =============================================================================
# CONFIGURAÇÃO RÁPIDA - PRODUÇÃO
# Gerado em: $(date)
# =============================================================================

# Ambiente
ENVIRONMENT=production
DEBUG=False

# Segurança
SECRET_KEY=$SECRET_KEY
ALLOWED_HOSTS=$allowed_hosts
CSRF_TRUSTED_ORIGINS=$csrf_origins

# Banco de dados (PostgreSQL)
DATABASE_ENGINE=postgresql
DB_NAME=$db_name
DB_USER=$db_user
DB_PASSWORD=$DB_PASSWORD
DB_HOST=db
DB_PORT=5432

# Email (SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=$email_user
EMAIL_HOST_PASSWORD=$email_pass
DEFAULT_FROM_EMAIL=$email_user

# Cache (Redis)
REDIS_URL=redis://redis:6379/1

# HTTPS (Habilitado)
SECURE_SSL_REDIRECT=True

# Arquivos
STATIC_ROOT=/app/staticfiles
MEDIA_ROOT=/app/media

# Logs
LOG_LEVEL=WARNING
LOG_FILE=/app/logs/django.log

# Site
SITE_NAME=Havoc
SITE_URL=$site_url

# Upload
FILE_UPLOAD_MAX_MEMORY_SIZE=5242880
DATA_UPLOAD_MAX_MEMORY_SIZE=5242880

# Container
DJANGO_SETTINGS_MODULE=core.settings_prod
GUNICORN_WORKERS=4
GUNICORN_BIND=0.0.0.0:8000
GUNICORN_TIMEOUT=120
EOF
        
        echo -e "${GREEN}✅ Configuração de produção criada!${NC}"
        echo "📝 Arquivo .env criado com todas as funcionalidades"
        echo "🔐 Senha do banco: $DB_PASSWORD"
        echo "⚠️  Configure SSL/HTTPS antes de usar em produção!"
        ;;
        
    4)
        echo -e "${YELLOW}📝 Iniciando configuração personalizada...${NC}"
        ./deploy.sh auto
        exit 0
        ;;
        
    *)
        echo -e "${RED}❌ Opção inválida!${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}🎯 PRÓXIMOS PASSOS:${NC}"
echo "1. Revisar arquivo .env criado"
echo "2. Executar deploy: ./deploy.sh deploy"
echo "3. Acessar: http://localhost:8000"
echo ""
echo -e "${GREEN}✅ Configuração rápida concluída!${NC}"
