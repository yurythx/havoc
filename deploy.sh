#!/bin/bash

# =============================================================================
# SCRIPT DE DEPLOY AUTOMATIZADO PARA CONTAINER DOCKER - PROJETO HAVOC
# Deploy totalmente automatizado com configuração interativa
# =============================================================================

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Função para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

prompt() {
    echo -e "${PURPLE}🔧 $1${NC}"
}

# Função para verificar se comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Função para input do usuário com valor padrão
read_input() {
    local prompt="$1"
    local default="$2"
    local var_name="$3"
    local is_password="${4:-false}"

    if [ "$is_password" = "true" ]; then
        echo -n -e "${PURPLE}🔐 $prompt${NC}"
        if [ -n "$default" ]; then
            echo -n " [padrão: ****]: "
        else
            echo -n ": "
        fi
        read -s input
        echo
    else
        echo -n -e "${PURPLE}🔧 $prompt${NC}"
        if [ -n "$default" ]; then
            echo -n " [padrão: $default]: "
        else
            echo -n ": "
        fi
        read input
    fi

    if [ -z "$input" ]; then
        input="$default"
    fi

    eval "$var_name='$input'"
}

# Função para confirmar ação
confirm() {
    local prompt="$1"
    local default="${2:-n}"

    echo -n -e "${YELLOW}❓ $prompt${NC}"
    if [ "$default" = "y" ]; then
        echo -n " [Y/n]: "
    else
        echo -n " [y/N]: "
    fi

    read -r response

    if [ -z "$response" ]; then
        response="$default"
    fi

    case "$response" in
        [yY][eE][sS]|[yY]) return 0 ;;
        *) return 1 ;;
    esac
}

# Função para gerar SECRET_KEY
generate_secret_key() {
    if command_exists python3; then
        python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
    elif command_exists python; then
        python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
    else
        # Fallback: gerar chave aleatória simples
        openssl rand -base64 50 | tr -d "=+/" | cut -c1-50
    fi
}

# Função para detectar IP público
get_public_ip() {
    # Tentar diferentes serviços para obter IP público
    local ip=""

    # Tentar curl primeiro
    if command_exists curl; then
        ip=$(curl -s --max-time 5 ifconfig.me 2>/dev/null || curl -s --max-time 5 ipinfo.io/ip 2>/dev/null || curl -s --max-time 5 icanhazip.com 2>/dev/null)
    fi

    # Fallback para wget
    if [ -z "$ip" ] && command_exists wget; then
        ip=$(wget -qO- --timeout=5 ifconfig.me 2>/dev/null || wget -qO- --timeout=5 ipinfo.io/ip 2>/dev/null)
    fi

    # Se não conseguir, usar localhost
    if [ -z "$ip" ]; then
        ip="localhost"
    fi

    echo "$ip"
}

# Função para validar email
validate_email() {
    local email="$1"
    if [[ "$email" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
        return 0
    else
        return 1
    fi
}

# Verificar dependências
check_dependencies() {
    log "Verificando dependências..."
    
    if ! command_exists docker; then
        error "Docker não está instalado!"
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        error "Docker Compose não está instalado!"
        exit 1
    fi
    
    success "Dependências verificadas"
}

# Verificar arquivos necessários
check_files() {
    log "Verificando arquivos necessários..."
    
    required_files=(
        "Dockerfile"
        "docker-compose.yml"
        "requirements.txt"
        "manage.py"
        ".env.docker"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            error "Arquivo obrigatório não encontrado: $file"
            exit 1
        fi
    done
    
    success "Arquivos verificados"
}

# Configuração interativa do ambiente
interactive_setup() {
    log "🚀 CONFIGURAÇÃO INTERATIVA DO AMBIENTE"
    echo ""

    # Detectar IP público
    local public_ip=$(get_public_ip)

    info "Vamos configurar seu ambiente de deploy passo a passo..."
    echo ""

    # === CONFIGURAÇÕES BÁSICAS ===
    prompt "=== CONFIGURAÇÕES BÁSICAS ==="

    # Ambiente
    echo ""
    info "Tipo de ambiente:"
    echo "1) Desenvolvimento (debug ativo, configurações relaxadas)"
    echo "2) Produção (debug desativo, configurações seguras)"
    echo ""
    read_input "Escolha o tipo de ambiente (1 ou 2)" "2" "env_type"

    if [ "$env_type" = "1" ]; then
        ENVIRONMENT="development"
        DEBUG="True"
        warning "Modo desenvolvimento selecionado"
    else
        ENVIRONMENT="production"
        DEBUG="False"
        success "Modo produção selecionado"
    fi

    # SECRET_KEY
    echo ""
    if confirm "Gerar nova SECRET_KEY automaticamente?" "y"; then
        SECRET_KEY=$(generate_secret_key)
        success "SECRET_KEY gerada automaticamente"
    else
        read_input "Digite sua SECRET_KEY personalizada" "" "SECRET_KEY" "true"
    fi

    # === CONFIGURAÇÕES DE REDE ===
    echo ""
    prompt "=== CONFIGURAÇÕES DE REDE ==="

    # ALLOWED_HOSTS
    echo ""
    info "Hosts permitidos para acessar a aplicação"
    info "IP público detectado: $public_ip"
    local default_hosts="localhost,127.0.0.1,$public_ip"
    read_input "Hosts permitidos (separados por vírgula)" "$default_hosts" "ALLOWED_HOSTS"

    # CSRF_TRUSTED_ORIGINS
    echo ""
    info "Origens confiáveis para CSRF"
    local default_origins="http://localhost:8000,http://$public_ip:8000"
    read_input "Origens CSRF (separadas por vírgula)" "$default_origins" "CSRF_TRUSTED_ORIGINS"

    # === CONFIGURAÇÕES DE BANCO ===
    echo ""
    prompt "=== CONFIGURAÇÕES DE BANCO DE DADOS ==="

    # Tipo de banco
    echo ""
    info "Tipos de banco disponíveis:"
    echo "1) PostgreSQL (recomendado para produção)"
    echo "2) MySQL/MariaDB"
    echo "3) SQLite (apenas para desenvolvimento)"
    echo ""
    read_input "Escolha o tipo de banco (1, 2 ou 3)" "1" "db_type"

    case "$db_type" in
        "1")
            DATABASE_ENGINE="postgresql"
            DB_NAME_DEFAULT="havoc_prod"
            DB_USER_DEFAULT="havoc_user"
            DB_PORT_DEFAULT="5432"
            ;;
        "2")
            DATABASE_ENGINE="mysql"
            DB_NAME_DEFAULT="havoc_prod"
            DB_USER_DEFAULT="havoc_user"
            DB_PORT_DEFAULT="3306"
            ;;
        "3")
            DATABASE_ENGINE="sqlite"
            DB_NAME_DEFAULT="db.sqlite3"
            DB_USER_DEFAULT=""
            DB_PORT_DEFAULT=""
            warning "SQLite selecionado - adequado apenas para desenvolvimento"
            ;;
        *)
            DATABASE_ENGINE="postgresql"
            DB_NAME_DEFAULT="havoc_prod"
            DB_USER_DEFAULT="havoc_user"
            DB_PORT_DEFAULT="5432"
            warning "Opção inválida, usando PostgreSQL como padrão"
            ;;
    esac

    if [ "$DATABASE_ENGINE" != "sqlite" ]; then
        echo ""
        read_input "Nome do banco de dados" "$DB_NAME_DEFAULT" "DB_NAME"
        read_input "Usuário do banco" "$DB_USER_DEFAULT" "DB_USER"
        read_input "Senha do banco" "$(openssl rand -base64 12)" "DB_PASSWORD" "true"
        read_input "Host do banco" "db" "DB_HOST"
        read_input "Porta do banco" "$DB_PORT_DEFAULT" "DB_PORT"
    else
        DB_NAME="$DB_NAME_DEFAULT"
        DB_USER=""
        DB_PASSWORD=""
        DB_HOST=""
        DB_PORT=""
    fi

    # === CONFIGURAÇÕES DE EMAIL ===
    echo ""
    prompt "=== CONFIGURAÇÕES DE EMAIL ==="

    if confirm "Configurar email SMTP?" "n"; then
        echo ""
        info "Configuração de email SMTP:"
        read_input "Host SMTP (ex: smtp.gmail.com)" "smtp.gmail.com" "EMAIL_HOST"
        read_input "Porta SMTP" "587" "EMAIL_PORT"
        read_input "Usuário/Email" "" "EMAIL_HOST_USER"
        read_input "Senha do email" "" "EMAIL_HOST_PASSWORD" "true"

        if validate_email "$EMAIL_HOST_USER"; then
            success "Email configurado: $EMAIL_HOST_USER"
            EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
            EMAIL_USE_TLS="True"
            DEFAULT_FROM_EMAIL="$EMAIL_HOST_USER"
        else
            warning "Email inválido, usando configuração console"
            EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend"
        fi
    else
        EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend"
        EMAIL_HOST=""
        EMAIL_PORT="587"
        EMAIL_HOST_USER=""
        EMAIL_HOST_PASSWORD=""
        EMAIL_USE_TLS="False"
        DEFAULT_FROM_EMAIL="noreply@havoc.local"
        info "Email configurado para modo console (desenvolvimento)"
    fi

    # === CONFIGURAÇÕES OPCIONAIS ===
    echo ""
    prompt "=== CONFIGURAÇÕES OPCIONAIS ==="

    # Redis
    if confirm "Habilitar Redis para cache?" "y"; then
        REDIS_URL="redis://redis:6379/1"
        success "Redis habilitado"
    else
        REDIS_URL=""
        info "Redis desabilitado"
    fi

    # HTTPS
    if [ "$ENVIRONMENT" = "production" ]; then
        echo ""
        if confirm "Habilitar redirecionamento HTTPS?" "n"; then
            SECURE_SSL_REDIRECT="True"
            warning "HTTPS habilitado - certifique-se de ter certificado SSL configurado"
        else
            SECURE_SSL_REDIRECT="False"
            info "HTTPS desabilitado"
        fi
    else
        SECURE_SSL_REDIRECT="False"
    fi

    # === RESUMO ===
    echo ""
    prompt "=== RESUMO DA CONFIGURAÇÃO ==="
    echo ""
    info "Ambiente: $ENVIRONMENT"
    info "Debug: $DEBUG"
    info "Banco: $DATABASE_ENGINE"
    if [ "$DATABASE_ENGINE" != "sqlite" ]; then
        info "Nome do banco: $DB_NAME"
        info "Usuário: $DB_USER"
        info "Host: $DB_HOST:$DB_PORT"
    fi
    info "Hosts permitidos: $ALLOWED_HOSTS"
    info "Email backend: $EMAIL_BACKEND"
    if [ -n "$REDIS_URL" ]; then
        info "Redis: Habilitado"
    else
        info "Redis: Desabilitado"
    fi
    info "HTTPS: $SECURE_SSL_REDIRECT"
    echo ""

    if confirm "Confirma a configuração acima?" "y"; then
        create_env_file
        success "Configuração salva em .env"
    else
        error "Configuração cancelada pelo usuário"
        exit 1
    fi
}

# Criar arquivo .env com as configurações
create_env_file() {
    log "Criando arquivo .env..."

    # Backup do .env existente
    if [ -f ".env" ]; then
        cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
        warning "Backup do .env anterior criado"
    fi

    # Criar novo arquivo .env
    cat > .env << EOF
# =============================================================================
# CONFIGURAÇÕES DO HAVOC - GERADO AUTOMATICAMENTE
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

    success "Arquivo .env criado com sucesso"
}

# Configurar ambiente (versão simplificada para compatibilidade)
setup_environment() {
    log "Configurando ambiente..."

    # Criar diretórios necessários
    mkdir -p logs
    mkdir -p media
    mkdir -p staticfiles
    mkdir -p backups

    success "Ambiente configurado"
}

# Build da imagem
build_image() {
    log "Construindo imagem Docker..."
    
    docker-compose build --no-cache
    
    success "Imagem construída com sucesso"
}

# Executar testes
run_tests() {
    log "Executando testes..."
    
    # Criar container temporário para testes
    docker-compose run --rm web python manage.py check
    
    success "Testes executados com sucesso"
}

# Deploy
deploy() {
    log "Iniciando deploy..."
    
    # Parar containers existentes
    log "Parando containers existentes..."
    docker-compose down
    
    # Verificar se Redis deve ser iniciado
    if [ -f ".env" ] && grep -q "REDIS_URL=redis://" .env; then
        log "Iniciando serviços com Redis..."
        docker-compose --profile redis up -d
    else
        log "Iniciando serviços básicos..."
        docker-compose up -d db web
    fi
    
    # Aguardar serviços ficarem prontos
    log "Aguardando serviços ficarem prontos..."
    sleep 30
    
    # Verificar status
    log "Verificando status dos serviços..."
    docker-compose ps
    
    success "Deploy concluído!"
}

# Verificar saúde dos serviços
check_health() {
    log "Verificando saúde dos serviços..."
    
    # Verificar se containers estão rodando
    if ! docker-compose ps | grep -q "Up"; then
        error "Alguns serviços não estão rodando!"
        docker-compose logs
        exit 1
    fi
    
    # Testar endpoint de saúde (se existir)
    log "Testando conectividade..."
    sleep 10
    
    if curl -f http://localhost:8000/ >/dev/null 2>&1; then
        success "Aplicação está respondendo!"
    else
        warning "Aplicação pode não estar totalmente pronta ainda"
        log "Verifique os logs: docker-compose logs web"
    fi
}

# Mostrar informações pós-deploy
show_info() {
    echo ""
    echo "🎉 DEPLOY CONCLUÍDO!"
    echo "===================="
    echo ""
    echo "📋 Informações do Deploy:"
    echo "• URL da aplicação: http://localhost:8000"
    echo "• Admin Django: http://localhost:8000/admin/"
    echo "• Usuário admin padrão: admin / admin123"
    echo ""
    echo "🔧 Comandos úteis:"
    echo "• Ver logs: docker-compose logs -f"
    echo "• Parar: docker-compose down"
    echo "• Reiniciar: docker-compose restart"
    echo "• Shell Django: docker-compose exec web python manage.py shell"
    echo "• Backup DB: docker-compose exec db pg_dump -U havoc_user havoc_prod > backup.sql"
    echo ""
    echo "⚠️  IMPORTANTE:"
    echo "• Altere a SECRET_KEY no arquivo .env"
    echo "• Configure ALLOWED_HOSTS para seu domínio"
    echo "• Configure email SMTP se necessário"
    echo "• Configure HTTPS para produção"
    echo ""
}

# Menu principal
main() {
    echo "🚀 DEPLOY AUTOMATIZADO HAVOC EM CONTAINER"
    echo "=========================================="
    echo ""

    case "${1:-}" in
        "auto"|"")
            # Deploy automatizado completo com configuração interativa
            log "🤖 DEPLOY TOTALMENTE AUTOMATIZADO"
            echo ""
            check_dependencies
            check_files
            interactive_setup
            setup_environment
            build_image
            deploy
            check_health
            show_info
            ;;
        "config")
            # Apenas configuração interativa
            log "⚙️ CONFIGURAÇÃO INTERATIVA"
            echo ""
            interactive_setup
            success "Configuração concluída! Execute './deploy.sh deploy' para fazer o deploy"
            ;;
        "build")
            check_dependencies
            check_files
            build_image
            ;;
        "test")
            check_dependencies
            check_files
            run_tests
            ;;
        "deploy")
            # Deploy tradicional (assume .env já configurado)
            check_dependencies
            check_files
            if [ ! -f ".env" ]; then
                warning "Arquivo .env não encontrado!"
                if confirm "Executar configuração interativa?" "y"; then
                    interactive_setup
                else
                    setup_environment
                fi
            fi
            build_image
            deploy
            check_health
            show_info
            ;;
        "quick")
            # Deploy rápido sem rebuild
            log "Deploy rápido (sem rebuild)..."
            docker-compose down
            docker-compose up -d
            check_health
            show_info
            ;;
        "logs")
            docker-compose logs -f
            ;;
        "stop")
            docker-compose down
            success "Containers parados"
            ;;
        "clean")
            log "Limpando containers e volumes..."
            docker-compose down -v
            docker system prune -f
            success "Limpeza concluída"
            ;;
        "secret")
            SECRET_KEY=$(generate_secret_key)
            echo "Nova SECRET_KEY gerada:"
            echo "$SECRET_KEY"
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            show_help
            exit 1
            ;;
    esac
}

# Mostrar ajuda
show_help() {
    echo "🚀 DEPLOY AUTOMATIZADO HAVOC EM CONTAINER"
    echo "=========================================="
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos disponíveis:"
    echo ""
    echo "  🤖 AUTOMATIZADO:"
    echo "    auto      - Deploy totalmente automatizado com configuração interativa (PADRÃO)"
    echo "    config    - Apenas configuração interativa (gera .env)"
    echo ""
    echo "  🔧 MANUAL:"
    echo "    deploy    - Deploy completo (verifica .env, configura se necessário)"
    echo "    build     - Apenas construir a imagem Docker"
    echo "    test      - Executar testes de validação"
    echo "    quick     - Deploy rápido sem rebuild"
    echo ""
    echo "  📊 GERENCIAMENTO:"
    echo "    logs      - Ver logs em tempo real"
    echo "    stop      - Parar todos os containers"
    echo "    clean     - Limpar containers e volumes"
    echo "    secret    - Gerar nova SECRET_KEY"
    echo ""
    echo "  ❓ AJUDA:"
    echo "    help      - Mostrar esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0              # Deploy automatizado (recomendado)"
    echo "  $0 auto         # Deploy automatizado"
    echo "  $0 config       # Apenas configurar .env"
    echo "  $0 deploy       # Deploy tradicional"
    echo "  $0 quick        # Deploy rápido"
    echo ""
    echo "🎯 Para primeira vez, use: $0 auto"
}

# Executar função principal
main "$@"
