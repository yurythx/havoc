#!/bin/bash

# =============================================================================
# SCRIPT DE DEPLOY COMPLETO PARA UBUNTU - PROJETO HAVOC
# Instala dependências e faz deploy em uma única execução
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

# Função para verificar se é Ubuntu
check_ubuntu() {
    if [ ! -f /etc/lsb-release ]; then
        error "Este script é específico para Ubuntu!"
        exit 1
    fi
    
    . /etc/lsb-release
    log "Detectado: $DISTRIB_DESCRIPTION"
    success "Sistema operacional compatível"
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

# Função para gerar SECRET_KEY melhorada
generate_secret_key() {
    # Tentar usar openssl primeiro (mais confiável)
    if command -v openssl >/dev/null 2>&1; then
        openssl rand -base64 50 | tr -d "=+/" | cut -c1-50
    # Fallback para /dev/urandom
    elif [ -r /dev/urandom ]; then
        tr -dc 'a-zA-Z0-9!@#$%^&*(-_=+)' < /dev/urandom | head -c 50
    else
        # Último fallback usando apenas ferramentas do sistema
        echo "django-insecure-$(date +%s)-$(whoami)-$(hostname)-fallback-key"
    fi
}

# Função para instalar dependências do sistema
install_system_dependencies() {
    log "Instalando dependências do sistema..."
    
    # Atualizar repositórios
    sudo apt update
    
    # Instalar dependências básicas
    sudo apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        libpq-dev \
        curl \
        git \
        openssl
    
    success "Dependências do sistema instaladas"
}

# Função para verificar dependências
check_dependencies() {
    log "Verificando dependências..."
    
    local missing_deps=()
    
    if ! command -v python3 >/dev/null 2>&1; then
        missing_deps+=("python3")
    fi
    
    if ! command -v pip3 >/dev/null 2>&1; then
        missing_deps+=("python3-pip")
    fi
    
    if ! command -v openssl >/dev/null 2>&1; then
        missing_deps+=("openssl")
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        warning "Dependências faltando: ${missing_deps[*]}"
        log "Tentando instalar dependências automaticamente..."
        install_system_dependencies
    else
        success "Dependências verificadas"
    fi
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
            error "Certifique-se de estar no diretório raiz do projeto Havoc"
            exit 1
        fi
    done
    
    success "Arquivos verificados"
}

# Função para configurar ambiente de desenvolvimento
setup_development() {
    log "Configurando ambiente de desenvolvimento..."
    
    # Gerar SECRET_KEY
    local secret_key
    secret_key=$(generate_secret_key)
    
    # Criar arquivo .env para desenvolvimento
    cat > .env << EOF
# =============================================================================
# CONFIGURAÇÕES DE DESENVOLVIMENTO - HAVOC UBUNTU
# Gerado automaticamente em: $(date)
# =============================================================================

# Ambiente
ENVIRONMENT=development
DEBUG=True

# Segurança (desenvolvimento)
DJANGO_SECRET_KEY=$secret_key
ALLOWED_HOSTS=localhost,127.0.0.1,$(hostname),$(hostname -I | awk '{print $1}')
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://$(hostname):8000

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

# Configurações específicas Ubuntu
STATIC_ROOT=staticfiles
MEDIA_ROOT=media
EOF
    
    success "Arquivo .env criado para desenvolvimento"
    info "SECRET_KEY gerada: ${secret_key:0:20}..."
}

# Função para criar e ativar ambiente virtual
setup_virtual_environment() {
    log "Configurando ambiente virtual..."
    
    # Criar ambiente virtual se não existir
    if [ ! -d "env" ]; then
        log "Criando ambiente virtual..."
        python3 -m venv env
    fi
    
    # Ativar ambiente virtual
    source env/bin/activate
    
    # Atualizar pip
    pip install --upgrade pip
    
    success "Ambiente virtual configurado e ativado"
}

# Função para instalar dependências Python
install_python_dependencies() {
    log "Instalando dependências Python..."
    
    # Garantir que o ambiente virtual está ativo
    if [ -z "$VIRTUAL_ENV" ]; then
        source env/bin/activate
    fi
    
    # Instalar dependências
    pip install -r requirements.txt
    
    success "Dependências Python instaladas"
}

# Função para executar migrações
run_migrations() {
    log "Executando migrações do banco de dados..."
    
    # Garantir que o ambiente virtual está ativo
    if [ -z "$VIRTUAL_ENV" ]; then
        source env/bin/activate
    fi
    
    # Executar migrações
    python manage.py migrate
    
    success "Migrações executadas"
}

# Função para criar superusuário
create_superuser() {
    log "Criando superusuário padrão..."
    
    # Garantir que o ambiente virtual está ativo
    if [ -z "$VIRTUAL_ENV" ]; then
        source env/bin/activate
    fi
    
    # Criar superusuário
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@havoc.com').exists():
    User.objects.create_superuser('admin@havoc.com', 'admin123', email='admin@havoc.com', first_name='Admin', last_name='Havoc')
    print('Superusuário criado: admin@havoc.com / admin123')
else:
    print('Superusuário já existe')
"
    
    success "Superusuário configurado"
}

# Função para coletar arquivos estáticos
collect_static() {
    log "Coletando arquivos estáticos..."
    
    # Garantir que o ambiente virtual está ativo
    if [ -z "$VIRTUAL_ENV" ]; then
        source env/bin/activate
    fi
    
    # Coletar arquivos estáticos
    python manage.py collectstatic --noinput
    
    success "Arquivos estáticos coletados"
}

# Função para executar testes
run_tests() {
    log "Executando verificações do sistema..."
    
    # Garantir que o ambiente virtual está ativo
    if [ -z "$VIRTUAL_ENV" ]; then
        source env/bin/activate
    fi
    
    # Executar check do Django
    python manage.py check
    
    success "Verificações do sistema passaram"
}

# Função para configurar firewall
configure_firewall() {
    log "Configurando firewall para desenvolvimento..."
    
    # Verificar se UFW está instalado
    if command -v ufw >/dev/null 2>&1; then
        # Permitir porta 8000 para desenvolvimento
        sudo ufw allow 8000/tcp >/dev/null 2>&1 || true
        success "Firewall configurado (porta 8000 liberada)"
    else
        warning "UFW não encontrado, firewall não configurado"
    fi
}

# Função para mostrar informações do sistema
show_system_info() {
    log "Coletando informações do sistema..."
    
    local ip_local
    ip_local=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "localhost")
    
    echo ""
    info "📊 Informações do Sistema:"
    echo "• Hostname: $(hostname)"
    echo "• IP Local: $ip_local"
    echo "• Usuário: $(whoami)"
    echo "• Diretório: $(pwd)"
    echo "• Python: $(python3 --version 2>/dev/null || echo 'Não encontrado')"
    echo ""
}

# Função principal para deploy de desenvolvimento
deploy_development() {
    echo "🐧 DEPLOY UBUNTU - HAVOC"
    echo "========================"
    echo ""
    
    check_ubuntu
    clean_environment
    check_dependencies
    check_files
    setup_development
    setup_virtual_environment
    install_python_dependencies
    run_migrations
    create_superuser
    collect_static
    run_tests
    configure_firewall
    show_system_info
    
    echo ""
    success "🎉 Deploy de desenvolvimento concluído!"
    echo ""
    info "📋 Informações importantes:"
    echo "• URL Local: http://localhost:8000"
    echo "• URL Rede: http://$(hostname -I | awk '{print $1}'):8000"
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
                    info "Para iniciar o servidor manualmente:"
                    echo "  source env/bin/activate"
                    echo "  python manage.py runserver 0.0.0.0:8000"
                    ;;
                *) 
                    start_server
                    ;;
            esac
        else
            info "Para iniciar o servidor:"
            echo "  source env/bin/activate"
            echo "  python manage.py runserver 0.0.0.0:8000"
        fi
    fi
}

# Função para iniciar servidor
start_server() {
    log "Iniciando servidor de desenvolvimento..."
    
    # Garantir que o ambiente virtual está ativo
    if [ -z "$VIRTUAL_ENV" ]; then
        source env/bin/activate
    fi
    
    local ip_local
    ip_local=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "localhost")
    
    info "Servidor será iniciado em:"
    echo "• Local: http://localhost:8000"
    echo "• Rede: http://$ip_local:8000"
    info "Para parar o servidor, pressione Ctrl+C"
    echo ""
    
    # Iniciar servidor permitindo acesso externo
    python manage.py runserver 0.0.0.0:8000
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
        "install")
            check_ubuntu
            install_system_dependencies
            success "Dependências do sistema instaladas"
            ;;
        "help"|"-h"|"--help")
            echo "🐧 DEPLOY UBUNTU - HAVOC"
            echo "========================"
            echo ""
            echo "Uso: $0 [comando]"
            echo ""
            echo "Comandos:"
            echo "  dev        - Deploy de desenvolvimento completo (padrão)"
            echo "  install    - Instalar apenas dependências do sistema"
            echo "  check      - Verificar sistema"
            echo "  clean      - Limpar ambiente"
            echo "  secret     - Gerar SECRET_KEY"
            echo "  help       - Mostrar ajuda"
            echo ""
            echo "Exemplos:"
            echo "  $0 dev                    # Deploy completo"
            echo "  $0 dev --no-server        # Deploy sem iniciar servidor"
            echo "  sudo $0 install           # Instalar dependências do sistema"
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
