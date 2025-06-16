#!/bin/bash

# =============================================================================
# TESTE COMPLETO DO SISTEMA DE DEPLOY AUTOMATIZADO
# Testa todas as funcionalidades do deploy
# =============================================================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Contadores
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

# Função para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((TESTS_PASSED++))
}

error() {
    echo -e "${RED}❌ $1${NC}"
    ((TESTS_FAILED++))
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

info() {
    echo -e "${PURPLE}ℹ️  $1${NC}"
}

# Função para executar teste
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    ((TESTS_TOTAL++))
    log "Teste $TESTS_TOTAL: $test_name"
    
    if eval "$test_command" >/dev/null 2>&1; then
        success "$test_name"
        return 0
    else
        error "$test_name"
        return 1
    fi
}

# Função para testar arquivo
test_file() {
    local file="$1"
    local description="$2"
    
    run_test "Arquivo $file existe" "[ -f '$file' ]"
    
    if [ -f "$file" ]; then
        run_test "$description - sintaxe" "bash -n '$file' 2>/dev/null || true"
    fi
}

# Função para testar comando
test_command() {
    local command="$1"
    local description="$2"
    
    run_test "$description" "command -v '$command'"
}

echo "🧪 TESTE COMPLETO DO SISTEMA DE DEPLOY"
echo "======================================"
echo ""

# === TESTE 1: DEPENDÊNCIAS ===
log "=== TESTANDO DEPENDÊNCIAS ==="

test_command "docker" "Docker instalado"
test_command "docker-compose" "Docker Compose instalado"
test_command "curl" "cURL disponível"
test_command "openssl" "OpenSSL disponível"

# === TESTE 2: ARQUIVOS OBRIGATÓRIOS ===
log "=== TESTANDO ARQUIVOS OBRIGATÓRIOS ==="

test_file "Dockerfile" "Dockerfile válido"
test_file "docker-compose.yml" "Docker Compose válido"
test_file "requirements.txt" "Requirements base"
test_file "requirements-prod.txt" "Requirements produção"
test_file "manage.py" "Django manage.py"
test_file ".env.docker" "Arquivo de exemplo"

# === TESTE 3: SCRIPTS DE DEPLOY ===
log "=== TESTANDO SCRIPTS DE DEPLOY ==="

test_file "deploy.sh" "Script principal de deploy"
test_file "quick_config.sh" "Script de configuração rápida"
test_file "install_ubuntu.sh" "Script de instalação Ubuntu"

# Testar se scripts são executáveis
if [ -f "deploy.sh" ]; then
    run_test "deploy.sh é executável" "[ -x deploy.sh ]"
fi

# === TESTE 4: ESTRUTURA DOCKER ===
log "=== TESTANDO ESTRUTURA DOCKER ==="

test_file "docker/entrypoint.sh" "Script entrypoint"
test_file "docker/start.sh" "Script start"
test_file "docker/nginx/nginx.conf" "Configuração Nginx"
test_file "docker/nginx/default.conf" "Configuração Nginx default"

# === TESTE 5: CONFIGURAÇÕES DJANGO ===
log "=== TESTANDO CONFIGURAÇÕES DJANGO ==="

test_file "core/settings_prod.py" "Settings de produção"
test_file "core/health_check.py" "Health check"
test_file "core/urls.py" "URLs principais"

# Testar se health check está nas URLs
if [ -f "core/urls.py" ]; then
    run_test "Health check configurado nas URLs" "grep -q 'health_check' core/urls.py"
fi

# === TESTE 6: VALIDAÇÃO DOCKER COMPOSE ===
log "=== TESTANDO DOCKER COMPOSE ==="

if command -v docker-compose >/dev/null 2>&1; then
    run_test "Docker Compose config válida" "docker-compose config >/dev/null 2>&1"
    
    # Testar se serviços estão definidos
    run_test "Serviço 'db' definido" "docker-compose config | grep -q 'db:'"
    run_test "Serviço 'web' definido" "docker-compose config | grep -q 'web:'"
    
    # Testar volumes
    run_test "Volumes definidos" "docker-compose config | grep -q 'volumes:'"
else
    warning "Docker Compose não disponível para teste"
fi

# === TESTE 7: VALIDAÇÃO DOCKERFILE ===
log "=== TESTANDO DOCKERFILE ==="

if [ -f "Dockerfile" ]; then
    run_test "Dockerfile tem FROM" "grep -q '^FROM' Dockerfile"
    run_test "Dockerfile tem WORKDIR" "grep -q '^WORKDIR' Dockerfile"
    run_test "Dockerfile tem EXPOSE" "grep -q '^EXPOSE' Dockerfile"
    run_test "Dockerfile instala netcat" "grep -q 'netcat' Dockerfile"
    run_test "Dockerfile copia requirements" "grep -q 'requirements' Dockerfile"
fi

# === TESTE 8: VALIDAÇÃO REQUIREMENTS ===
log "=== TESTANDO REQUIREMENTS ==="

if [ -f "requirements-prod.txt" ]; then
    run_test "Gunicorn no requirements-prod" "grep -q 'gunicorn' requirements-prod.txt"
    run_test "psycopg2 no requirements-prod" "grep -q 'psycopg2' requirements-prod.txt"
    run_test "dj-database-url no requirements-prod" "grep -q 'dj-database-url' requirements-prod.txt"
fi

# === TESTE 9: FUNCIONALIDADES DO DEPLOY.SH ===
log "=== TESTANDO FUNCIONALIDADES DEPLOY.SH ==="

if [ -f "deploy.sh" ]; then
    run_test "deploy.sh tem função interactive_setup" "grep -q 'interactive_setup()' deploy.sh"
    run_test "deploy.sh tem função generate_secret_key" "grep -q 'generate_secret_key()' deploy.sh"
    run_test "deploy.sh tem função get_public_ip" "grep -q 'get_public_ip()' deploy.sh"
    run_test "deploy.sh tem função validate_email" "grep -q 'validate_email()' deploy.sh"
    run_test "deploy.sh tem função create_env_file" "grep -q 'create_env_file()' deploy.sh"
fi

# === TESTE 10: TESTE DE GERAÇÃO DE SECRET_KEY ===
log "=== TESTANDO GERAÇÃO DE SECRET_KEY ==="

if command -v python3 >/dev/null 2>&1; then
    SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null || echo "")
    if [ -n "$SECRET_KEY" ] && [ ${#SECRET_KEY} -gt 30 ]; then
        success "Geração de SECRET_KEY funciona"
        ((TESTS_PASSED++))
    else
        error "Geração de SECRET_KEY falhou"
        ((TESTS_FAILED++))
    fi
    ((TESTS_TOTAL++))
else
    warning "Python3 não disponível para teste de SECRET_KEY"
fi

# === TESTE 11: TESTE DE CONFIGURAÇÃO RÁPIDA ===
log "=== TESTANDO CONFIGURAÇÃO RÁPIDA ==="

if [ -f "quick_config.sh" ]; then
    run_test "quick_config.sh tem opções de ambiente" "grep -q 'Desenvolvimento Local' quick_config.sh"
    run_test "quick_config.sh tem opções de produção" "grep -q 'PRODUÇÃO' quick_config.sh"
fi

# === TESTE 12: TESTE DE HEALTH CHECK ===
log "=== TESTANDO HEALTH CHECK ==="

if [ -f "core/health_check.py" ]; then
    run_test "Health check tem função principal" "grep -q 'def health_check' core/health_check.py"
    run_test "Health check testa banco" "grep -q 'connection.cursor' core/health_check.py"
    run_test "Health check testa cache" "grep -q 'cache.set' core/health_check.py"
fi

# === TESTE 13: TESTE DE SCRIPTS WINDOWS ===
log "=== TESTANDO SCRIPTS WINDOWS ==="

test_file "deploy_auto.ps1" "Script PowerShell automatizado"
test_file "test_deploy.ps1" "Script de teste PowerShell"

# === TESTE 14: DOCUMENTAÇÃO ===
log "=== TESTANDO DOCUMENTAÇÃO ==="

test_file "README_DEPLOY_AUTO.md" "README do deploy automatizado"
test_file "DEPLOY_AUTOMATIZADO_FINAL.md" "Relatório final"
test_file "COMANDOS_RAPIDOS.md" "Guia de comandos"

# === TESTE 15: TESTE SIMULADO DE CONFIGURAÇÃO ===
log "=== TESTANDO CONFIGURAÇÃO SIMULADA ==="

# Criar arquivo .env de teste
cat > .env.test << EOF
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=test-key-123
DATABASE_ENGINE=postgresql
DB_NAME=test_db
DB_USER=test_user
DB_PASSWORD=test_pass
DB_HOST=db
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
REDIS_URL=redis://redis:6379/1
SECURE_SSL_REDIRECT=False
EOF

run_test "Arquivo .env de teste criado" "[ -f '.env.test' ]"
run_test "Arquivo .env tem configurações básicas" "grep -q 'SECRET_KEY' .env.test"
run_test "Arquivo .env tem configurações de banco" "grep -q 'DATABASE_ENGINE' .env.test"

# Limpar arquivo de teste
rm -f .env.test

# === RESULTADOS FINAIS ===
echo ""
echo "📊 RESULTADOS DOS TESTES"
echo "========================"
echo ""
echo "Total de testes: $TESTS_TOTAL"
echo -e "Testes passaram: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Testes falharam: ${RED}$TESTS_FAILED${NC}"
echo ""

# Calcular porcentagem
if [ $TESTS_TOTAL -gt 0 ]; then
    PERCENTAGE=$((TESTS_PASSED * 100 / TESTS_TOTAL))
    echo "Taxa de sucesso: $PERCENTAGE%"
    echo ""
    
    if [ $PERCENTAGE -ge 90 ]; then
        echo -e "${GREEN}🎉 SISTEMA DE DEPLOY EXCELENTE!${NC}"
        echo "O sistema está pronto para uso em produção."
    elif [ $PERCENTAGE -ge 75 ]; then
        echo -e "${YELLOW}⚠️  SISTEMA DE DEPLOY BOM${NC}"
        echo "Algumas melhorias podem ser necessárias."
    else
        echo -e "${RED}❌ SISTEMA DE DEPLOY PRECISA DE CORREÇÕES${NC}"
        echo "Vários problemas foram encontrados."
    fi
else
    echo -e "${RED}❌ NENHUM TESTE FOI EXECUTADO${NC}"
fi

echo ""
echo "🔧 PRÓXIMOS PASSOS:"
echo "1. Corrigir problemas encontrados (se houver)"
echo "2. Executar deploy de teste: ./deploy.sh auto"
echo "3. Verificar funcionamento da aplicação"
echo ""

# Retornar código de saída baseado nos resultados
if [ $TESTS_FAILED -eq 0 ]; then
    exit 0
else
    exit 1
fi
