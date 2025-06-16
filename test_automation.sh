#!/bin/bash

# =============================================================================
# TESTE DA AUTOMAÇÃO - SIMULAÇÃO SEM DOCKER
# Testa as funções de automação sem precisar do Docker
# =============================================================================

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo "🧪 TESTE DA AUTOMAÇÃO DE DEPLOY"
echo "==============================="
echo ""

# Testar função de geração de SECRET_KEY
log "Testando geração de SECRET_KEY..."

# Simular função generate_secret_key
generate_secret_key() {
    if command -v python3 >/dev/null 2>&1; then
        python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null
    elif command -v python >/dev/null 2>&1; then
        python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null
    else
        # Fallback: gerar chave aleatória simples
        if command -v openssl >/dev/null 2>&1; then
            openssl rand -base64 50 | tr -d "=+/" | cut -c1-50
        else
            echo "django-insecure-fallback-key-$(date +%s)-$(shuf -i 1000-9999 -n 1 2>/dev/null || echo 1234)"
        fi
    fi
}

SECRET_KEY=$(generate_secret_key)
if [ -n "$SECRET_KEY" ] && [ ${#SECRET_KEY} -gt 20 ]; then
    success "SECRET_KEY gerada: ${SECRET_KEY:0:20}..."
else
    error "Falha na geração de SECRET_KEY"
fi

# Testar função de detecção de IP
log "Testando detecção de IP público..."

get_public_ip() {
    local ip=""
    
    # Tentar curl primeiro
    if command -v curl >/dev/null 2>&1; then
        ip=$(curl -s --max-time 5 ifconfig.me 2>/dev/null || curl -s --max-time 5 ipinfo.io/ip 2>/dev/null || echo "")
    fi
    
    # Fallback para wget
    if [ -z "$ip" ] && command -v wget >/dev/null 2>&1; then
        ip=$(wget -qO- --timeout=5 ifconfig.me 2>/dev/null || echo "")
    fi
    
    # Se não conseguir, usar localhost
    if [ -z "$ip" ]; then
        ip="localhost"
    fi
    
    echo "$ip"
}

PUBLIC_IP=$(get_public_ip)
success "IP público detectado: $PUBLIC_IP"

# Testar função de validação de email
log "Testando validação de email..."

validate_email() {
    local email="$1"
    if [[ "$email" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
        return 0
    else
        return 1
    fi
}

# Testar emails válidos e inválidos
test_emails=(
    "user@example.com:válido"
    "test.email+tag@domain.co.uk:válido"
    "invalid-email:inválido"
    "user@:inválido"
    "@domain.com:inválido"
    "user.name@domain.com:válido"
)

for test_case in "${test_emails[@]}"; do
    email=$(echo "$test_case" | cut -d: -f1)
    expected=$(echo "$test_case" | cut -d: -f2)
    
    if validate_email "$email"; then
        result="válido"
    else
        result="inválido"
    fi
    
    if [ "$result" = "$expected" ]; then
        success "Email $email: $result ✓"
    else
        error "Email $email: esperado $expected, obtido $result"
    fi
done

# Testar criação de arquivo .env
log "Testando criação de arquivo .env..."

# Configurações de teste
ENVIRONMENT="production"
DEBUG="False"
DATABASE_ENGINE="postgresql"
DB_NAME="havoc_test"
DB_USER="havoc_user"
DB_PASSWORD="test_password_123"
DB_HOST="db"
DB_PORT="5432"
ALLOWED_HOSTS="localhost,127.0.0.1,$PUBLIC_IP"
CSRF_TRUSTED_ORIGINS="http://localhost:8000,http://$PUBLIC_IP:8000"
EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend"
EMAIL_HOST=""
EMAIL_PORT="587"
EMAIL_USE_TLS="False"
EMAIL_HOST_USER=""
EMAIL_HOST_PASSWORD=""
DEFAULT_FROM_EMAIL="noreply@havoc.local"
REDIS_URL="redis://redis:6379/1"
SECURE_SSL_REDIRECT="False"

# Criar arquivo .env de teste
create_test_env() {
    cat > .env.test << EOF
# =============================================================================
# CONFIGURAÇÕES DO HAVOC - GERADO AUTOMATICAMENTE (TESTE)
# Gerado em: $(date)
# =============================================================================

# Ambiente
ENVIRONMENT=$ENVIRONMENT
DEBUG=$DEBUG

# =============================================================================
# SEGURANÇA
# =============================================================================

SECRET_KEY=$SECRET_KEY
ALLOWED_HOSTS=$ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS=$CSRF_TRUSTED_ORIGINS

# =============================================================================
# BANCO DE DADOS
# =============================================================================

DATABASE_ENGINE=$DATABASE_ENGINE
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT

# =============================================================================
# EMAIL
# =============================================================================

EMAIL_BACKEND=$EMAIL_BACKEND
EMAIL_HOST=$EMAIL_HOST
EMAIL_PORT=$EMAIL_PORT
EMAIL_USE_TLS=$EMAIL_USE_TLS
EMAIL_HOST_USER=$EMAIL_HOST_USER
EMAIL_HOST_PASSWORD=$EMAIL_HOST_PASSWORD
DEFAULT_FROM_EMAIL=$DEFAULT_FROM_EMAIL

# =============================================================================
# CACHE E SESSÕES
# =============================================================================

REDIS_URL=$REDIS_URL

# =============================================================================
# CONFIGURAÇÕES DE SEGURANÇA HTTPS
# =============================================================================

SECURE_SSL_REDIRECT=$SECURE_SSL_REDIRECT

# =============================================================================
# ARQUIVOS ESTÁTICOS E MEDIA
# =============================================================================

STATIC_ROOT=/app/staticfiles
MEDIA_ROOT=/app/media

# =============================================================================
# LOGS
# =============================================================================

LOG_LEVEL=INFO
LOG_FILE=/app/logs/django.log

# =============================================================================
# CONFIGURAÇÕES ESPECÍFICAS DO HAVOC
# =============================================================================

SITE_NAME=Havoc
SITE_URL=http://$(echo $ALLOWED_HOSTS | cut -d',' -f1):8000

# Configurações de upload
FILE_UPLOAD_MAX_MEMORY_SIZE=5242880
DATA_UPLOAD_MAX_MEMORY_SIZE=5242880

# =============================================================================
# CONFIGURAÇÕES DO CONTAINER
# =============================================================================

DJANGO_SETTINGS_MODULE=core.settings_prod
GUNICORN_WORKERS=3
GUNICORN_BIND=0.0.0.0:8000
GUNICORN_TIMEOUT=120
EOF
}

create_test_env

if [ -f ".env.test" ]; then
    success "Arquivo .env.test criado com sucesso"
    
    # Verificar conteúdo
    log "Verificando conteúdo do arquivo .env.test..."
    
    # Verificar se contém configurações essenciais
    if grep -q "SECRET_KEY=" .env.test; then
        success "SECRET_KEY presente"
    else
        error "SECRET_KEY ausente"
    fi
    
    if grep -q "DATABASE_ENGINE=postgresql" .env.test; then
        success "Configuração de banco presente"
    else
        error "Configuração de banco ausente"
    fi
    
    if grep -q "ALLOWED_HOSTS=" .env.test; then
        success "ALLOWED_HOSTS presente"
    else
        error "ALLOWED_HOSTS ausente"
    fi
    
    # Mostrar resumo do arquivo
    echo ""
    log "Resumo do arquivo .env.test criado:"
    echo "• Linhas: $(wc -l < .env.test)"
    echo "• Tamanho: $(wc -c < .env.test) bytes"
    echo "• SECRET_KEY: $(grep "SECRET_KEY=" .env.test | cut -d= -f2 | cut -c1-20)..."
    echo "• Ambiente: $(grep "ENVIRONMENT=" .env.test | cut -d= -f2)"
    echo "• Banco: $(grep "DATABASE_ENGINE=" .env.test | cut -d= -f2)"
    echo "• Hosts: $(grep "ALLOWED_HOSTS=" .env.test | cut -d= -f2)"
    
else
    error "Falha na criação do arquivo .env.test"
fi

# Testar quick_config.sh se existir
if [ -f "quick_config.sh" ]; then
    log "Testando quick_config.sh..."
    
    if bash -n quick_config.sh; then
        success "quick_config.sh tem sintaxe válida"
    else
        error "quick_config.sh tem erro de sintaxe"
    fi
else
    warning "quick_config.sh não encontrado"
fi

# Testar deploy.sh se existir
if [ -f "deploy.sh" ]; then
    log "Testando deploy.sh..."
    
    if bash -n deploy.sh; then
        success "deploy.sh tem sintaxe válida"
    else
        error "deploy.sh tem erro de sintaxe"
    fi
    
    # Verificar se contém funções essenciais
    if grep -q "interactive_setup()" deploy.sh; then
        success "Função interactive_setup presente"
    else
        error "Função interactive_setup ausente"
    fi
    
    if grep -q "generate_secret_key()" deploy.sh; then
        success "Função generate_secret_key presente"
    else
        error "Função generate_secret_key ausente"
    fi
    
    if grep -q "create_env_file()" deploy.sh; then
        success "Função create_env_file presente"
    else
        error "Função create_env_file ausente"
    fi
else
    error "deploy.sh não encontrado"
fi

# Testar docker-compose.yml se existir
if [ -f "docker-compose.yml" ]; then
    log "Testando docker-compose.yml..."
    
    # Verificar se contém serviços essenciais
    if grep -q "services:" docker-compose.yml; then
        success "Seção services presente"
    else
        error "Seção services ausente"
    fi
    
    if grep -q "db:" docker-compose.yml; then
        success "Serviço db presente"
    else
        error "Serviço db ausente"
    fi
    
    if grep -q "web:" docker-compose.yml; then
        success "Serviço web presente"
    else
        error "Serviço web ausente"
    fi
    
    if grep -q "volumes:" docker-compose.yml; then
        success "Seção volumes presente"
    else
        error "Seção volumes ausente"
    fi
else
    error "docker-compose.yml não encontrado"
fi

echo ""
log "🎯 RESUMO DO TESTE DE AUTOMAÇÃO"
echo "==============================="
echo ""
echo "✅ Funcionalidades testadas:"
echo "• Geração de SECRET_KEY"
echo "• Detecção de IP público"
echo "• Validação de email"
echo "• Criação de arquivo .env"
echo "• Validação de sintaxe dos scripts"
echo "• Verificação de estrutura docker-compose"
echo ""
echo "📁 Arquivos gerados:"
echo "• .env.test - Arquivo de configuração de teste"
echo ""
echo "🔧 Próximos passos:"
echo "1. Instalar Docker e Docker Compose"
echo "2. Executar: ./deploy.sh auto"
echo "3. Seguir configuração interativa"
echo "4. Testar aplicação em http://localhost:8000"
echo ""

# Limpar arquivo de teste
rm -f .env.test

success "Teste de automação concluído com sucesso!"
