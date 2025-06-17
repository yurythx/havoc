#!/bin/bash

# =============================================================================
# SCRIPT DE DEPLOY MELHORADO - PROJETO HAVOC
# Versão corrigida com base nos problemas identificados
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

# Função para limpar variáveis de ambiente conflitantes
clean_environment() {
    log "Limpando variáveis de ambiente conflitantes..."
    
    # Limpar variáveis de banco
    unset DATABASE_ENGINE DB_NAME DB_USER DB_PASSWORD DB_HOST DB_PORT
    unset DATABASE_URL
    
    # Limpar variáveis de log
    unset LOG_FILE
    
    # Limpar configurações de produção
    unset DJANGO_SETTINGS_MODULE
    
    # Definir configuração padrão para desenvolvimento
    export DJANGO_SETTINGS_MODULE=core.settings
    
    success "Variáveis de ambiente limpas"
}

# Função para detectar ambiente
detect_environment() {
    # Verificar se está em container
    if [ -f /.dockerenv ]; then
        echo "container"
        return
    fi
    
    # Verificar variáveis de ambiente
    if [ "$ENVIRONMENT" = "production" ] || [ "$ENVIRONMENT" = "prod" ]; then
        echo "production"
    elif [ "$ENVIRONMENT" = "development" ] || [ "$ENVIRONMENT" = "dev" ]; then
        echo "development"
    else
        echo "development"  # Padrão seguro
    fi
}

# Função para gerar SECRET_KEY
generate_secret_key() {
    # Tentar usar openssl primeiro (mais confiável)
    if command -v openssl >/dev/null 2>&1; then
        openssl rand -base64 50 | tr -d "=+/" | cut -c1-50
    # Fallback para Python se Django estiver disponível
    elif command -v python3 >/dev/null 2>&1; then
        python3 -c "
import secrets
import string
chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
print(''.join(secrets.choice(chars) for _ in range(50)))
" 2>/dev/null || echo "django-insecure-$(date +%s)-$(whoami)-fallback-key-change-in-production"
    elif command -v python >/dev/null 2>&1; then
        python -c "
import random
import string
chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
print(''.join(random.choice(chars) for _ in range(50)))
" 2>/dev/null || echo "django-insecure-$(date +%s)-$(whoami)-fallback-key-change-in-production"
    else
        # Último fallback usando apenas ferramentas do sistema
        echo "django-insecure-$(date +%s)-$(whoami)-fallback-key-change-in-production"
    fi
}

# Função para gerar senha segura
generate_password() {
    openssl rand -base64 12 | tr -d "=+/"
}

# Função para verificar dependências
check_dependencies() {
    log "Verificando dependências..."
    
    local missing_deps=()
    
    if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
        missing_deps+=("python")
    fi
    
    if ! command -v pip >/dev/null 2>&1 && ! command -v pip3 >/dev/null 2>&1; then
        missing_deps+=("pip")
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        error "Dependências faltando: ${missing_deps[*]}"
        exit 1
    fi
    
    success "Dependências verificadas"
}

# Função para verificar arquivos necessários
check_files() {
    log "Verificando arquivos necessários..."
    
    local required_files=(
        "manage.py"
        "requirements.txt"
        "core/settings.py"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            error "Arquivo obrigatório não encontrado: $file"
            exit 1
        fi
    done
    
    success "Arquivos verificados"
}

# Função para configurar ambiente de desenvolvimento
setup_development() {
    log "Configurando ambiente de desenvolvimento..."
    
    # Criar arquivo .env para desenvolvimento
    cat > .env << EOF
# =============================================================================
# CONFIGURAÇÕES DE DESENVOLVIMENTO - HAVOC
# Gerado automaticamente em: $(date)
# =============================================================================

# Ambiente
ENVIRONMENT=development
DEBUG=True

# Segurança (desenvolvimento)
DJANGO_SECRET_KEY=$(generate_secret_key)
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# Banco de dados (SQLite para desenvolvimento)
DATABASE_ENGINE=sqlite
DATABASE_NAME=db.sqlite3

# Email (console para desenvolvimento)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@havoc.local

# Logs (console apenas)
LOG_LEVEL=DEBUG

# Site
SITE_NAME=Havoc
SITE_URL=http://localhost:8000

# Uploads
FILE_UPLOAD_MAX_MEMORY_SIZE=5242880
DATA_UPLOAD_MAX_MEMORY_SIZE=5242880

# Segurança (desenvolvimento)
SECURE_SSL_REDIRECT=False
EOF
    
    success "Arquivo .env criado para desenvolvimento"
}

# Função para instalar dependências
install_dependencies() {
    log "Instalando dependências Python..."
    
    # Verificar se há ambiente virtual
    if [ ! -d "env" ] && [ ! -d "venv" ] && [ -z "$VIRTUAL_ENV" ]; then
        warning "Nenhum ambiente virtual detectado"
        if command -v python3 >/dev/null 2>&1; then
            log "Criando ambiente virtual..."
            python3 -m venv env
            source env/bin/activate || source env/Scripts/activate
        else
            warning "Instalando no sistema (não recomendado)"
        fi
    fi
    
    # Ativar ambiente virtual se existir
    if [ -d "env" ] && [ -z "$VIRTUAL_ENV" ]; then
        source env/bin/activate 2>/dev/null || source env/Scripts/activate 2>/dev/null || true
    elif [ -d "venv" ] && [ -z "$VIRTUAL_ENV" ]; then
        source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null || true
    fi
    
    # Instalar dependências
    if command -v pip3 >/dev/null 2>&1; then
        pip3 install -r requirements.txt
    else
        pip install -r requirements.txt
    fi
    
    success "Dependências instaladas"
}

# Função para executar migrações
run_migrations() {
    log "Executando migrações do banco de dados..."
    
    # Ativar ambiente virtual se necessário
    if [ -d "env" ] && [ -z "$VIRTUAL_ENV" ]; then
        source env/bin/activate 2>/dev/null || source env/Scripts/activate 2>/dev/null || true
    fi
    
    # Executar migrações
    if command -v python3 >/dev/null 2>&1; then
        python3 manage.py migrate
    else
        python manage.py migrate
    fi
    
    success "Migrações executadas"
}

# Função para criar superusuário
create_superuser() {
    log "Verificando superusuário..."
    
    # Ativar ambiente virtual se necessário
    if [ -d "env" ] && [ -z "$VIRTUAL_ENV" ]; then
        source env/bin/activate 2>/dev/null || source env/Scripts/activate 2>/dev/null || true
    fi
    
    # Verificar se já existe superusuário
    local has_superuser
    if command -v python3 >/dev/null 2>&1; then
        has_superuser=$(python3 manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(is_superuser=True).exists())" 2>/dev/null || echo "False")
    else
        has_superuser=$(python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(is_superuser=True).exists())" 2>/dev/null || echo "False")
    fi
    
    if [ "$has_superuser" = "False" ]; then
        log "Criando superusuário padrão..."
        if command -v python3 >/dev/null 2>&1; then
            python3 manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@havoc.com').exists():
    User.objects.create_superuser('admin@havoc.com', 'admin123', email='admin@havoc.com', first_name='Admin', last_name='Havoc')
    print('Superusuário criado: admin@havoc.com / admin123')
else:
    print('Superusuário já existe')
"
        else
            python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@havoc.com').exists():
    User.objects.create_superuser('admin@havoc.com', 'admin123', email='admin@havoc.com', first_name='Admin', last_name='Havoc')
    print('Superusuário criado: admin@havoc.com / admin123')
else:
    print('Superusuário já existe')
"
        fi
        success "Superusuário configurado"
    else
        info "Superusuário já existe"
    fi
}

# Função para coletar arquivos estáticos
collect_static() {
    log "Coletando arquivos estáticos..."
    
    # Ativar ambiente virtual se necessário
    if [ -d "env" ] && [ -z "$VIRTUAL_ENV" ]; then
        source env/bin/activate 2>/dev/null || source env/Scripts/activate 2>/dev/null || true
    fi
    
    # Coletar arquivos estáticos
    if command -v python3 >/dev/null 2>&1; then
        python3 manage.py collectstatic --noinput
    else
        python manage.py collectstatic --noinput
    fi
    
    success "Arquivos estáticos coletados"
}

# Função para executar testes
run_tests() {
    log "Executando verificações do sistema..."
    
    # Ativar ambiente virtual se necessário
    if [ -d "env" ] && [ -z "$VIRTUAL_ENV" ]; then
        source env/bin/activate 2>/dev/null || source env/Scripts/activate 2>/dev/null || true
    fi
    
    # Executar check do Django
    if command -v python3 >/dev/null 2>&1; then
        python3 manage.py check
    else
        python manage.py check
    fi
    
    success "Verificações do sistema passaram"
}

# Função para iniciar servidor
start_server() {
    log "Iniciando servidor de desenvolvimento..."
    
    # Ativar ambiente virtual se necessário
    if [ -d "env" ] && [ -z "$VIRTUAL_ENV" ]; then
        source env/bin/activate 2>/dev/null || source env/Scripts/activate 2>/dev/null || true
    fi
    
    info "Servidor será iniciado em http://localhost:8000"
    info "Para parar o servidor, pressione Ctrl+C"
    echo ""
    
    # Iniciar servidor
    if command -v python3 >/dev/null 2>&1; then
        python3 manage.py runserver
    else
        python manage.py runserver
    fi
}

# Função principal para deploy de desenvolvimento
deploy_development() {
    echo "🚀 DEPLOY DE DESENVOLVIMENTO - HAVOC"
    echo "===================================="
    echo ""
    
    clean_environment
    check_dependencies
    check_files
    setup_development
    install_dependencies
    run_migrations
    create_superuser
    collect_static
    run_tests
    
    echo ""
    success "🎉 Deploy de desenvolvimento concluído!"
    echo ""
    info "📋 Informações importantes:"
    echo "• URL: http://localhost:8000"
    echo "• Admin: http://localhost:8000/admin/"
    echo "• Usuário: admin@havoc.com"
    echo "• Senha: admin123"
    echo ""
    
    if [ "${1:-}" != "--no-server" ]; then
        if [ -t 0 ]; then  # Verificar se é terminal interativo
            echo -n "Deseja iniciar o servidor agora? [Y/n]: "
            read -r response
            case "$response" in
                [nN][oO]|[nN]) 
                    info "Para iniciar o servidor manualmente: python manage.py runserver"
                    ;;
                *) 
                    start_server
                    ;;
            esac
        else
            info "Para iniciar o servidor: python manage.py runserver"
        fi
    fi
}

# Menu principal
main() {
    case "${1:-dev}" in
        "dev"|"development")
            deploy_development "${@:2}"
            ;;
        "check")
            clean_environment
            check_dependencies
            check_files
            run_tests
            success "Verificações concluídas"
            ;;
        "clean")
            clean_environment
            success "Ambiente limpo"
            ;;
        "secret")
            echo "Nova SECRET_KEY:"
            generate_secret_key
            ;;
        "help"|"-h"|"--help")
            echo "🚀 DEPLOY MELHORADO - HAVOC"
            echo "=========================="
            echo ""
            echo "Uso: $0 [comando]"
            echo ""
            echo "Comandos:"
            echo "  dev        - Deploy de desenvolvimento (padrão)"
            echo "  check      - Verificar sistema"
            echo "  clean      - Limpar ambiente"
            echo "  secret     - Gerar SECRET_KEY"
            echo "  help       - Mostrar ajuda"
            echo ""
            ;;
        *)
            echo "Comando inválido. Use '$0 help' para ver opções disponíveis."
            exit 1
            ;;
    esac
}

# Executar função principal
main "$@"
