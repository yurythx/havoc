#!/bin/bash

# =============================================================================
# SCRIPT DE DEPLOY AUTOMATIZADO - PROJETO HAVOC
# Deploy inteligente que detecta o ambiente e executa a melhor estratégia
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

# Banner
show_banner() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🚀 HAVOC AUTO DEPLOY 🚀                   ║"
    echo "║                                                              ║"
    echo "║  Deploy Automatizado Inteligente para Container Ubuntu       ║"
    echo "║  Detecta ambiente e executa a melhor estratégia             ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
}

# Função para detectar ambiente
detect_environment() {
    log "Detectando ambiente de execução..."
    
    # Verificar se é container
    if [ -f /.dockerenv ]; then
        ENVIRONMENT="container"
        info "Ambiente: Container Docker"
        return
    fi
    
    # Verificar se Docker está disponível
    if command -v docker >/dev/null 2>&1 && command -v docker-compose >/dev/null 2>&1; then
        ENVIRONMENT="docker"
        info "Ambiente: Docker disponível"
        return
    fi
    
    # Verificar se é Ubuntu
    if [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        if [[ "$DISTRIB_ID" == "Ubuntu" ]]; then
            ENVIRONMENT="ubuntu"
            info "Ambiente: Ubuntu $DISTRIB_RELEASE"
            return
        fi
    fi
    
    # Verificar se é Linux genérico
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        ENVIRONMENT="linux"
        info "Ambiente: Linux genérico"
        return
    fi
    
    # Verificar se é Windows (WSL ou Git Bash)
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || grep -q Microsoft /proc/version 2>/dev/null; then
        ENVIRONMENT="windows"
        info "Ambiente: Windows/WSL"
        return
    fi
    
    # Fallback
    ENVIRONMENT="unknown"
    warning "Ambiente não detectado, usando configuração genérica"
}

# Função para verificar pré-requisitos
check_prerequisites() {
    log "Verificando pré-requisitos..."
    
    case $ENVIRONMENT in
        "docker")
            if ! docker --version >/dev/null 2>&1; then
                error "Docker não está funcionando"
                exit 1
            fi
            if ! docker-compose --version >/dev/null 2>&1; then
                error "Docker Compose não está funcionando"
                exit 1
            fi
            success "Docker e Docker Compose disponíveis"
            ;;
        "ubuntu"|"linux")
            if ! command -v python3 >/dev/null 2>&1; then
                warning "Python3 não encontrado, será instalado"
            fi
            ;;
        "windows")
            if ! command -v python >/dev/null 2>&1 && ! command -v python3 >/dev/null 2>&1; then
                error "Python não encontrado no Windows"
                exit 1
            fi
            ;;
    esac
}

# Função para configurar arquivo .env
setup_env_file() {
    log "Configurando arquivo de ambiente..."
    
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            success "Arquivo .env criado a partir do .env.example"
        else
            # Criar .env básico
            cat > .env << 'EOF'
# Configuração básica gerada automaticamente
ENVIRONMENT=development
DEBUG=True
DJANGO_SECRET_KEY=django-insecure-auto-generated-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_ENGINE=sqlite
DATABASE_NAME=db.sqlite3
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EOF
            success "Arquivo .env básico criado"
        fi
        
        warning "IMPORTANTE: Edite o arquivo .env com suas configurações antes do deploy em produção"
    else
        info "Arquivo .env já existe"
    fi
}

# Deploy via Docker
deploy_docker() {
    log "Executando deploy via Docker..."
    
    # Verificar se docker-compose.yml existe
    if [ ! -f docker-compose.yml ]; then
        error "Arquivo docker-compose.yml não encontrado"
        exit 1
    fi
    
    # Build e deploy
    log "Construindo imagens..."
    docker-compose build
    
    log "Iniciando serviços..."
    docker-compose up -d
    
    log "Aguardando serviços ficarem prontos..."
    sleep 30
    
    # Verificar health check
    if curl -f http://localhost:8000/health/ >/dev/null 2>&1; then
        success "Aplicação está funcionando!"
    else
        warning "Health check falhou, mas serviços podem estar iniciando"
    fi
    
    # Mostrar status
    docker-compose ps
}

# Deploy via Ubuntu
deploy_ubuntu() {
    log "Executando deploy via Ubuntu..."
    
    if [ -f scripts/deploy_ubuntu.sh ]; then
        chmod +x scripts/deploy_ubuntu.sh
        cd scripts
        ./deploy_ubuntu.sh dev
        cd ..
    else
        error "Script deploy_ubuntu.sh não encontrado"
        exit 1
    fi
}

# Deploy via Linux genérico
deploy_linux() {
    log "Executando deploy via Linux..."
    
    if [ -f scripts/deploy_melhorado.sh ]; then
        chmod +x scripts/deploy_melhorado.sh
        cd scripts
        ./deploy_melhorado.sh dev
        cd ..
    else
        error "Script deploy_melhorado.sh não encontrado"
        exit 1
    fi
}

# Deploy via Windows
deploy_windows() {
    log "Executando deploy via Windows..."
    
    if [ -f scripts/deploy_simples.ps1 ]; then
        info "Execute o seguinte comando no PowerShell:"
        echo "cd scripts"
        echo ".\\deploy_simples.ps1 dev"
    else
        error "Script deploy_simples.ps1 não encontrado"
        exit 1
    fi
}

# Função principal de deploy
execute_deploy() {
    case $ENVIRONMENT in
        "docker")
            deploy_docker
            ;;
        "ubuntu")
            deploy_ubuntu
            ;;
        "linux")
            deploy_linux
            ;;
        "windows")
            deploy_windows
            ;;
        "container")
            info "Executando dentro de container, nada a fazer"
            ;;
        *)
            error "Ambiente não suportado: $ENVIRONMENT"
            exit 1
            ;;
    esac
}

# Função para mostrar informações pós-deploy
show_post_deploy_info() {
    echo ""
    success "🎉 Deploy automatizado concluído!"
    echo ""
    info "📋 Informações de acesso:"
    echo "• URL Principal: http://localhost:8000"
    echo "• Admin Django: http://localhost:8000/admin/"
    echo "• Health Check: http://localhost:8000/health/"
    echo ""
    info "🔑 Credenciais padrão:"
    echo "• Usuário: admin@havoc.com"
    echo "• Senha: admin123"
    echo ""
    
    case $ENVIRONMENT in
        "docker")
            info "🐳 Comandos Docker úteis:"
            echo "• Ver logs: docker-compose logs -f"
            echo "• Parar: docker-compose down"
            echo "• Status: docker-compose ps"
            ;;
        "ubuntu"|"linux")
            info "🐧 Comandos úteis:"
            echo "• Ver logs: tail -f logs/django.log"
            echo "• Parar: Ctrl+C no terminal do servidor"
            echo "• Reativar env: source env/bin/activate"
            ;;
    esac
    
    echo ""
    warning "⚠️  Para produção, lembre-se de:"
    echo "• Configurar SECRET_KEY segura no .env"
    echo "• Configurar banco PostgreSQL"
    echo "• Configurar HTTPS"
    echo "• Configurar backup automático"
}

# Função de ajuda
show_help() {
    echo "🚀 HAVOC AUTO DEPLOY"
    echo "===================="
    echo ""
    echo "Deploy automatizado inteligente que detecta o ambiente e executa a melhor estratégia."
    echo ""
    echo "Uso: $0 [opções]"
    echo ""
    echo "Opções:"
    echo "  --help, -h     Mostra esta ajuda"
    echo "  --env-only     Apenas configura arquivo .env"
    echo "  --check        Apenas verifica pré-requisitos"
    echo "  --force-env    Força detecção de ambiente específico"
    echo "                 Valores: docker, ubuntu, linux, windows"
    echo ""
    echo "Exemplos:"
    echo "  $0                    # Deploy automático"
    echo "  $0 --check           # Apenas verificar sistema"
    echo "  $0 --force-env docker # Forçar deploy via Docker"
    echo ""
}

# Função principal
main() {
    # Processar argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_help
                exit 0
                ;;
            --env-only)
                setup_env_file
                exit 0
                ;;
            --check)
                show_banner
                detect_environment
                check_prerequisites
                success "Sistema verificado com sucesso!"
                exit 0
                ;;
            --force-env)
                ENVIRONMENT="$2"
                shift 2
                ;;
            *)
                error "Opção desconhecida: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Executar deploy
    show_banner
    
    # Detectar ambiente se não foi forçado
    if [ -z "$ENVIRONMENT" ]; then
        detect_environment
    else
        info "Ambiente forçado: $ENVIRONMENT"
    fi
    
    check_prerequisites
    setup_env_file
    execute_deploy
    show_post_deploy_info
}

# Executar função principal
main "$@"
