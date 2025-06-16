#!/bin/bash

# =============================================================================
# SCRIPT DE DEPLOY PARA CONTAINER DOCKER - PROJETO HAVOC
# =============================================================================

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Função para verificar se comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
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

# Configurar ambiente
setup_environment() {
    log "Configurando ambiente..."
    
    # Copiar arquivo de ambiente se não existir
    if [ ! -f ".env" ]; then
        log "Copiando .env.docker para .env..."
        cp .env.docker .env
        warning "IMPORTANTE: Edite o arquivo .env com suas configurações específicas!"
        warning "Especialmente: SECRET_KEY, DB_PASSWORD, ALLOWED_HOSTS"
    fi
    
    # Criar diretórios necessários
    mkdir -p logs
    mkdir -p media
    mkdir -p staticfiles
    mkdir -p backups
    
    success "Ambiente configurado"
}

# Gerar chave secreta
generate_secret_key() {
    log "Gerando chave secreta..."
    
    if command_exists python3; then
        SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
        echo "Nova SECRET_KEY gerada:"
        echo "SECRET_KEY=$SECRET_KEY"
        echo ""
        warning "IMPORTANTE: Substitua a SECRET_KEY no arquivo .env pela chave acima!"
    else
        warning "Python3 não encontrado. Gere uma SECRET_KEY manualmente."
    fi
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
    
    # Iniciar serviços
    log "Iniciando serviços..."
    docker-compose up -d
    
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
    echo "🐳 DEPLOY HAVOC EM CONTAINER DOCKER"
    echo "===================================="
    echo ""
    
    case "${1:-}" in
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
            check_dependencies
            check_files
            setup_environment
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
            generate_secret_key
            ;;
        *)
            echo "Uso: $0 {build|test|deploy|quick|logs|stop|clean|secret}"
            echo ""
            echo "Comandos:"
            echo "  build   - Apenas construir a imagem"
            echo "  test    - Executar testes"
            echo "  deploy  - Deploy completo (recomendado para primeira vez)"
            echo "  quick   - Deploy rápido sem rebuild"
            echo "  logs    - Ver logs em tempo real"
            echo "  stop    - Parar todos os containers"
            echo "  clean   - Limpar containers e volumes"
            echo "  secret  - Gerar nova SECRET_KEY"
            echo ""
            echo "Exemplo: $0 deploy"
            exit 1
            ;;
    esac
}

# Executar função principal
main "$@"
