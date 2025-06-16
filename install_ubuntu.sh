#!/bin/bash

# =============================================================================
# SCRIPT DE INSTALAÇÃO AUTOMÁTICA - UBUNTU
# Instala Docker, Docker Compose e prepara ambiente para o Havoc
# =============================================================================

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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
    echo -e "${PURPLE}ℹ️  $1${NC}"
}

# Verificar se é Ubuntu
check_ubuntu() {
    if [ ! -f /etc/lsb-release ]; then
        error "Este script é específico para Ubuntu!"
        exit 1
    fi
    
    . /etc/lsb-release
    log "Detectado: $DISTRIB_DESCRIPTION"
    
    # Verificar versão mínima (20.04)
    version=$(echo $DISTRIB_RELEASE | cut -d. -f1)
    if [ "$version" -lt 20 ]; then
        error "Ubuntu 20.04 ou superior é necessário!"
        exit 1
    fi
    
    success "Sistema operacional compatível"
}

# Verificar privilégios
check_privileges() {
    if [ "$EUID" -eq 0 ]; then
        error "Não execute este script como root!"
        error "Execute como usuário normal que tenha acesso sudo"
        exit 1
    fi
    
    # Verificar se tem sudo
    if ! sudo -n true 2>/dev/null; then
        error "Este script precisa de privilégios sudo"
        error "Execute: sudo -v"
        exit 1
    fi
    
    success "Privilégios verificados"
}

# Verificar recursos do sistema
check_resources() {
    log "Verificando recursos do sistema..."
    
    # Verificar RAM (mínimo 2GB)
    ram_gb=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$ram_gb" -lt 2 ]; then
        warning "RAM disponível: ${ram_gb}GB (recomendado: 2GB+)"
    else
        success "RAM: ${ram_gb}GB"
    fi
    
    # Verificar espaço em disco (mínimo 10GB)
    disk_gb=$(df -BG / | awk 'NR==2{print $4}' | sed 's/G//')
    if [ "$disk_gb" -lt 10 ]; then
        warning "Espaço livre: ${disk_gb}GB (recomendado: 10GB+)"
    else
        success "Espaço em disco: ${disk_gb}GB"
    fi
}

# Atualizar sistema
update_system() {
    log "Atualizando sistema..."
    
    sudo apt update
    sudo apt upgrade -y
    
    success "Sistema atualizado"
}

# Instalar dependências básicas
install_dependencies() {
    log "Instalando dependências básicas..."
    
    sudo apt install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release \
        git \
        unzip \
        wget \
        htop \
        nano \
        python3 \
        python3-pip
    
    success "Dependências básicas instaladas"
}

# Remover Docker antigo
remove_old_docker() {
    log "Removendo versões antigas do Docker..."
    
    sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    success "Versões antigas removidas"
}

# Instalar Docker
install_docker() {
    log "Instalando Docker..."
    
    # Adicionar chave GPG
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Adicionar repositório
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Atualizar e instalar
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    success "Docker instalado"
}

# Instalar Docker Compose
install_docker_compose() {
    log "Instalando Docker Compose..."
    
    # Baixar versão mais recente
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    
    sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # Dar permissão
    sudo chmod +x /usr/local/bin/docker-compose
    
    # Criar link simbólico
    sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    success "Docker Compose instalado (versão: $DOCKER_COMPOSE_VERSION)"
}

# Configurar usuário Docker
configure_docker_user() {
    log "Configurando usuário para Docker..."
    
    # Adicionar usuário ao grupo docker
    sudo usermod -aG docker $USER
    
    success "Usuário adicionado ao grupo docker"
    warning "Você precisa fazer logout/login ou executar: newgrp docker"
}

# Configurar firewall
configure_firewall() {
    log "Configurando firewall básico..."
    
    # Instalar UFW se não estiver instalado
    sudo apt install -y ufw
    
    # Configurar regras básicas
    sudo ufw --force reset
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow ssh
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw allow 8000/tcp
    
    # Ativar firewall
    sudo ufw --force enable
    
    success "Firewall configurado"
}

# Verificar instalação
verify_installation() {
    log "Verificando instalação..."
    
    # Verificar Docker
    if command -v docker >/dev/null 2>&1; then
        DOCKER_VERSION=$(docker --version)
        success "Docker: $DOCKER_VERSION"
    else
        error "Docker não foi instalado corretamente"
        return 1
    fi
    
    # Verificar Docker Compose
    if command -v docker-compose >/dev/null 2>&1; then
        COMPOSE_VERSION=$(docker-compose --version)
        success "Docker Compose: $COMPOSE_VERSION"
    else
        error "Docker Compose não foi instalado corretamente"
        return 1
    fi
    
    # Testar Docker (pode falhar se usuário não fez logout/login)
    if docker run hello-world >/dev/null 2>&1; then
        success "Docker está funcionando"
    else
        warning "Docker instalado mas precisa de logout/login para funcionar"
        info "Execute: newgrp docker"
    fi
}

# Criar estrutura de diretórios
create_directories() {
    log "Criando estrutura de diretórios..."
    
    mkdir -p ~/havoc-deploy/{logs,media,staticfiles,backups}
    
    success "Diretórios criados em ~/havoc-deploy/"
}

# Mostrar informações finais
show_final_info() {
    echo ""
    echo "🎉 INSTALAÇÃO CONCLUÍDA!"
    echo "======================="
    echo ""
    echo "✅ Componentes instalados:"
    echo "• Docker Engine"
    echo "• Docker Compose"
    echo "• Dependências do sistema"
    echo "• Firewall configurado"
    echo ""
    echo "📋 Próximos passos:"
    echo "1. Fazer logout/login ou executar: newgrp docker"
    echo "2. Transferir projeto Havoc para o servidor"
    echo "3. Configurar arquivo .env"
    echo "4. Executar deploy: ./deploy.sh deploy"
    echo ""
    echo "📁 Estrutura criada:"
    echo "• ~/havoc-deploy/ - Diretório para o projeto"
    echo ""
    echo "🔧 Comandos úteis:"
    echo "• Verificar Docker: docker --version"
    echo "• Testar Docker: docker run hello-world"
    echo "• Status firewall: sudo ufw status"
    echo ""
    echo "📖 Documentação completa: DEPLOY_UBUNTU.md"
    echo ""
}

# Menu principal
main() {
    echo "🐧 INSTALAÇÃO AUTOMÁTICA - UBUNTU"
    echo "=================================="
    echo ""
    echo "Este script irá instalar:"
    echo "• Docker Engine"
    echo "• Docker Compose"
    echo "• Dependências necessárias"
    echo "• Configuração básica de firewall"
    echo ""
    
    read -p "Continuar com a instalação? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Instalação cancelada."
        exit 0
    fi
    
    echo ""
    log "Iniciando instalação..."
    
    # Executar verificações e instalação
    check_ubuntu
    check_privileges
    check_resources
    update_system
    install_dependencies
    remove_old_docker
    install_docker
    install_docker_compose
    configure_docker_user
    configure_firewall
    create_directories
    verify_installation
    show_final_info
    
    echo ""
    success "Instalação concluída com sucesso!"
    echo ""
    warning "IMPORTANTE: Execute 'newgrp docker' ou faça logout/login antes de usar o Docker"
}

# Verificar argumentos
case "${1:-}" in
    "--help"|"-h")
        echo "Uso: $0 [opções]"
        echo ""
        echo "Opções:"
        echo "  --help, -h     Mostrar esta ajuda"
        echo "  --check        Apenas verificar sistema"
        echo ""
        echo "Este script instala Docker e Docker Compose no Ubuntu"
        exit 0
        ;;
    "--check")
        check_ubuntu
        check_privileges
        check_resources
        verify_installation 2>/dev/null || true
        exit 0
        ;;
    "")
        main
        ;;
    *)
        error "Opção inválida: $1"
        echo "Use --help para ver opções disponíveis"
        exit 1
        ;;
esac
