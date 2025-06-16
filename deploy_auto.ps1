# =============================================================================
# SCRIPT DE DEPLOY AUTOMATIZADO PARA WINDOWS - PROJETO HAVOC
# Deploy totalmente automatizado com configuração interativa
# =============================================================================

param(
    [string]$Command = "auto"
)

# Configurações
$ErrorActionPreference = "Stop"

# Cores para output
function Write-Log {
    param($Message, $Color = "Cyan")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor $Color
}

function Write-Success {
    param($Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param($Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Warning {
    param($Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Info {
    param($Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

function Write-Prompt {
    param($Message)
    Write-Host "🔧 $Message" -ForegroundColor Magenta
}

# Função para input do usuário
function Read-UserInput {
    param(
        [string]$Prompt,
        [string]$Default = "",
        [switch]$IsPassword = $false
    )
    
    if ($IsPassword) {
        Write-Host "🔐 $Prompt" -ForegroundColor Magenta -NoNewline
        if ($Default) {
            Write-Host " [padrão: ****]: " -NoNewline
        } else {
            Write-Host ": " -NoNewline
        }
        $input = Read-Host -AsSecureString
        $input = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($input))
    } else {
        Write-Host "🔧 $Prompt" -ForegroundColor Magenta -NoNewline
        if ($Default) {
            Write-Host " [padrão: $Default]: " -NoNewline
        } else {
            Write-Host ": " -NoNewline
        }
        $input = Read-Host
    }
    
    if ([string]::IsNullOrWhiteSpace($input)) {
        return $Default
    }
    return $input
}

# Função para confirmação
function Confirm-Action {
    param(
        [string]$Prompt,
        [string]$Default = "n"
    )
    
    Write-Host "❓ $Prompt" -ForegroundColor Yellow -NoNewline
    if ($Default -eq "y") {
        Write-Host " [Y/n]: " -NoNewline
    } else {
        Write-Host " [y/N]: " -NoNewline
    }
    
    $response = Read-Host
    
    if ([string]::IsNullOrWhiteSpace($response)) {
        $response = $Default
    }
    
    return $response -match "^[yY]"
}

# Função para gerar SECRET_KEY
function New-SecretKey {
    try {
        # Tentar usar Python
        $secretKey = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>$null
        if ($LASTEXITCODE -eq 0 -and $secretKey) {
            return $secretKey
        }
    } catch {}
    
    # Fallback: gerar chave aleatória
    $chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    $key = ""
    for ($i = 0; $i -lt 50; $i++) {
        $key += $chars[(Get-Random -Maximum $chars.Length)]
    }
    return $key
}

# Função para obter IP público
function Get-PublicIP {
    try {
        $ip = Invoke-RestMethod -Uri "https://ifconfig.me/ip" -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($ip) { return $ip.Trim() }
    } catch {}
    
    try {
        $ip = Invoke-RestMethod -Uri "https://ipinfo.io/ip" -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($ip) { return $ip.Trim() }
    } catch {}
    
    return "localhost"
}

# Função para validar email
function Test-Email {
    param([string]$Email)
    return $Email -match "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
}

# Verificar dependências
function Test-Dependencies {
    Write-Log "Verificando dependências..."
    
    # Verificar Docker
    try {
        $dockerVersion = docker --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Docker encontrado: $dockerVersion"
        } else {
            throw "Docker não encontrado"
        }
    } catch {
        Write-Error "Docker não está disponível"
        Write-Warning "Instale Docker Desktop para Windows"
        exit 1
    }
    
    # Verificar Docker Compose
    try {
        $composeVersion = docker-compose --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Docker Compose encontrado: $composeVersion"
        } else {
            throw "Docker Compose não encontrado"
        }
    } catch {
        Write-Error "Docker Compose não está disponível"
        exit 1
    }
}

# Verificar arquivos necessários
function Test-RequiredFiles {
    Write-Log "Verificando arquivos necessários..."
    
    $requiredFiles = @(
        "Dockerfile",
        "docker-compose.yml",
        "requirements.txt",
        "requirements-prod.txt",
        "manage.py"
    )
    
    $missingFiles = @()
    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            Write-Success "Arquivo encontrado: $file"
        } else {
            Write-Error "Arquivo não encontrado: $file"
            $missingFiles += $file
        }
    }
    
    if ($missingFiles.Count -gt 0) {
        Write-Error "Arquivos obrigatórios não encontrados. Abortando."
        exit 1
    }
}

# Configuração interativa
function Start-InteractiveSetup {
    Write-Log "🚀 CONFIGURAÇÃO INTERATIVA DO AMBIENTE" -Color "Blue"
    Write-Host ""
    
    # Detectar IP público
    $publicIP = Get-PublicIP
    
    Write-Info "Vamos configurar seu ambiente de deploy passo a passo..."
    Write-Host ""
    
    # === CONFIGURAÇÕES BÁSICAS ===
    Write-Prompt "=== CONFIGURAÇÕES BÁSICAS ==="
    Write-Host ""
    
    # Ambiente
    Write-Info "Tipo de ambiente:"
    Write-Host "1) Desenvolvimento (debug ativo, configurações relaxadas)"
    Write-Host "2) Produção (debug desativo, configurações seguras)"
    Write-Host ""
    $envType = Read-UserInput "Escolha o tipo de ambiente (1 ou 2)" "2"
    
    if ($envType -eq "1") {
        $script:ENVIRONMENT = "development"
        $script:DEBUG = "True"
        Write-Warning "Modo desenvolvimento selecionado"
    } else {
        $script:ENVIRONMENT = "production"
        $script:DEBUG = "False"
        Write-Success "Modo produção selecionado"
    }
    
    # SECRET_KEY
    Write-Host ""
    if (Confirm-Action "Gerar nova SECRET_KEY automaticamente?" "y") {
        $script:SECRET_KEY = New-SecretKey
        Write-Success "SECRET_KEY gerada automaticamente"
    } else {
        $script:SECRET_KEY = Read-UserInput "Digite sua SECRET_KEY personalizada" "" -IsPassword
    }
    
    # === CONFIGURAÇÕES DE REDE ===
    Write-Host ""
    Write-Prompt "=== CONFIGURAÇÕES DE REDE ==="
    Write-Host ""
    
    # ALLOWED_HOSTS
    Write-Info "Hosts permitidos para acessar a aplicação"
    Write-Info "IP público detectado: $publicIP"
    $defaultHosts = "localhost,127.0.0.1,$publicIP"
    $script:ALLOWED_HOSTS = Read-UserInput "Hosts permitidos (separados por vírgula)" $defaultHosts
    
    # CSRF_TRUSTED_ORIGINS
    Write-Host ""
    Write-Info "Origens confiáveis para CSRF"
    $defaultOrigins = "http://localhost:8000,http://$publicIP:8000"
    $script:CSRF_TRUSTED_ORIGINS = Read-UserInput "Origens CSRF (separadas por vírgula)" $defaultOrigins
    
    # === CONFIGURAÇÕES DE BANCO ===
    Write-Host ""
    Write-Prompt "=== CONFIGURAÇÕES DE BANCO DE DADOS ==="
    Write-Host ""
    
    # Tipo de banco
    Write-Info "Tipos de banco disponíveis:"
    Write-Host "1) PostgreSQL (recomendado para produção)"
    Write-Host "2) MySQL/MariaDB"
    Write-Host "3) SQLite (apenas para desenvolvimento)"
    Write-Host ""
    $dbType = Read-UserInput "Escolha o tipo de banco (1, 2 ou 3)" "1"
    
    switch ($dbType) {
        "1" {
            $script:DATABASE_ENGINE = "postgresql"
            $dbNameDefault = "havoc_prod"
            $dbUserDefault = "havoc_user"
            $dbPortDefault = "5432"
        }
        "2" {
            $script:DATABASE_ENGINE = "mysql"
            $dbNameDefault = "havoc_prod"
            $dbUserDefault = "havoc_user"
            $dbPortDefault = "3306"
        }
        "3" {
            $script:DATABASE_ENGINE = "sqlite"
            $dbNameDefault = "db.sqlite3"
            $dbUserDefault = ""
            $dbPortDefault = ""
            Write-Warning "SQLite selecionado - adequado apenas para desenvolvimento"
        }
        default {
            $script:DATABASE_ENGINE = "postgresql"
            $dbNameDefault = "havoc_prod"
            $dbUserDefault = "havoc_user"
            $dbPortDefault = "5432"
            Write-Warning "Opção inválida, usando PostgreSQL como padrão"
        }
    }
    
    if ($script:DATABASE_ENGINE -ne "sqlite") {
        Write-Host ""
        $script:DB_NAME = Read-UserInput "Nome do banco de dados" $dbNameDefault
        $script:DB_USER = Read-UserInput "Usuário do banco" $dbUserDefault
        $script:DB_PASSWORD = Read-UserInput "Senha do banco" ([System.Web.Security.Membership]::GeneratePassword(12, 3)) -IsPassword
        $script:DB_HOST = Read-UserInput "Host do banco" "db"
        $script:DB_PORT = Read-UserInput "Porta do banco" $dbPortDefault
    } else {
        $script:DB_NAME = $dbNameDefault
        $script:DB_USER = ""
        $script:DB_PASSWORD = ""
        $script:DB_HOST = ""
        $script:DB_PORT = ""
    }
    
    # === CONFIGURAÇÕES DE EMAIL ===
    Write-Host ""
    Write-Prompt "=== CONFIGURAÇÕES DE EMAIL ==="
    Write-Host ""
    
    if (Confirm-Action "Configurar email SMTP?" "n") {
        Write-Host ""
        Write-Info "Configuração de email SMTP:"
        $script:EMAIL_HOST = Read-UserInput "Host SMTP (ex: smtp.gmail.com)" "smtp.gmail.com"
        $script:EMAIL_PORT = Read-UserInput "Porta SMTP" "587"
        $script:EMAIL_HOST_USER = Read-UserInput "Usuário/Email" ""
        $script:EMAIL_HOST_PASSWORD = Read-UserInput "Senha do email" "" -IsPassword
        
        if (Test-Email $script:EMAIL_HOST_USER) {
            Write-Success "Email configurado: $($script:EMAIL_HOST_USER)"
            $script:EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
            $script:EMAIL_USE_TLS = "True"
            $script:DEFAULT_FROM_EMAIL = $script:EMAIL_HOST_USER
        } else {
            Write-Warning "Email inválido, usando configuração console"
            $script:EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
        }
    } else {
        $script:EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
        $script:EMAIL_HOST = ""
        $script:EMAIL_PORT = "587"
        $script:EMAIL_HOST_USER = ""
        $script:EMAIL_HOST_PASSWORD = ""
        $script:EMAIL_USE_TLS = "False"
        $script:DEFAULT_FROM_EMAIL = "noreply@havoc.local"
        Write-Info "Email configurado para modo console (desenvolvimento)"
    }
    
    # === CONFIGURAÇÕES OPCIONAIS ===
    Write-Host ""
    Write-Prompt "=== CONFIGURAÇÕES OPCIONAIS ==="
    Write-Host ""
    
    # Redis
    if (Confirm-Action "Habilitar Redis para cache?" "y") {
        $script:REDIS_URL = "redis://redis:6379/1"
        Write-Success "Redis habilitado"
    } else {
        $script:REDIS_URL = ""
        Write-Info "Redis desabilitado"
    }
    
    # HTTPS
    if ($script:ENVIRONMENT -eq "production") {
        Write-Host ""
        if (Confirm-Action "Habilitar redirecionamento HTTPS?" "n") {
            $script:SECURE_SSL_REDIRECT = "True"
            Write-Warning "HTTPS habilitado - certifique-se de ter certificado SSL configurado"
        } else {
            $script:SECURE_SSL_REDIRECT = "False"
            Write-Info "HTTPS desabilitado"
        }
    } else {
        $script:SECURE_SSL_REDIRECT = "False"
    }
    
    # === RESUMO ===
    Write-Host ""
    Write-Prompt "=== RESUMO DA CONFIGURAÇÃO ==="
    Write-Host ""
    Write-Info "Ambiente: $($script:ENVIRONMENT)"
    Write-Info "Debug: $($script:DEBUG)"
    Write-Info "Banco: $($script:DATABASE_ENGINE)"
    if ($script:DATABASE_ENGINE -ne "sqlite") {
        Write-Info "Nome do banco: $($script:DB_NAME)"
        Write-Info "Usuário: $($script:DB_USER)"
        Write-Info "Host: $($script:DB_HOST):$($script:DB_PORT)"
    }
    Write-Info "Hosts permitidos: $($script:ALLOWED_HOSTS)"
    Write-Info "Email backend: $($script:EMAIL_BACKEND)"
    if ($script:REDIS_URL) {
        Write-Info "Redis: Habilitado"
    } else {
        Write-Info "Redis: Desabilitado"
    }
    Write-Info "HTTPS: $($script:SECURE_SSL_REDIRECT)"
    Write-Host ""
    
    if (Confirm-Action "Confirma a configuração acima?" "y") {
        New-EnvFile
        Write-Success "Configuração salva em .env"
    } else {
        Write-Error "Configuração cancelada pelo usuário"
        exit 1
    }
}

# Criar arquivo .env
function New-EnvFile {
    Write-Log "Criando arquivo .env..."

    # Backup do .env existente
    if (Test-Path ".env") {
        $backupName = ".env.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Copy-Item ".env" $backupName
        Write-Warning "Backup do .env anterior criado: $backupName"
    }

    # Criar novo arquivo .env
    $envContent = @"
# =============================================================================
# CONFIGURAÇÕES DO HAVOC - GERADO AUTOMATICAMENTE
# Gerado em: $(Get-Date)
# =============================================================================

# Ambiente
ENVIRONMENT=$($script:ENVIRONMENT)
DEBUG=$($script:DEBUG)

# =============================================================================
# SEGURANÇA
# =============================================================================

SECRET_KEY=$($script:SECRET_KEY)
ALLOWED_HOSTS=$($script:ALLOWED_HOSTS)
CSRF_TRUSTED_ORIGINS=$($script:CSRF_TRUSTED_ORIGINS)

# =============================================================================
# BANCO DE DADOS
# =============================================================================

DATABASE_ENGINE=$($script:DATABASE_ENGINE)
DB_NAME=$($script:DB_NAME)
DB_USER=$($script:DB_USER)
DB_PASSWORD=$($script:DB_PASSWORD)
DB_HOST=$($script:DB_HOST)
DB_PORT=$($script:DB_PORT)

# =============================================================================
# EMAIL
# =============================================================================

EMAIL_BACKEND=$($script:EMAIL_BACKEND)
EMAIL_HOST=$($script:EMAIL_HOST)
EMAIL_PORT=$($script:EMAIL_PORT)
EMAIL_USE_TLS=$($script:EMAIL_USE_TLS)
EMAIL_HOST_USER=$($script:EMAIL_HOST_USER)
EMAIL_HOST_PASSWORD=$($script:EMAIL_HOST_PASSWORD)
DEFAULT_FROM_EMAIL=$($script:DEFAULT_FROM_EMAIL)

# =============================================================================
# CACHE E SESSÕES
# =============================================================================

REDIS_URL=$($script:REDIS_URL)

# =============================================================================
# CONFIGURAÇÕES DE SEGURANÇA HTTPS
# =============================================================================

SECURE_SSL_REDIRECT=$($script:SECURE_SSL_REDIRECT)

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
SITE_URL=http://$($script:ALLOWED_HOSTS.Split(',')[0]):8000

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
"@

    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Success "Arquivo .env criado com sucesso"
}

# Build da imagem
function Start-Build {
    Write-Log "Construindo imagem Docker..."

    try {
        docker-compose build --no-cache web
        Write-Success "Imagem construída com sucesso"
    } catch {
        Write-Error "Falha no build da imagem: $_"
        exit 1
    }
}

# Deploy
function Start-Deploy {
    Write-Log "Iniciando deploy..."

    try {
        # Parar containers existentes
        Write-Log "Parando containers existentes..."
        docker-compose down 2>$null

        # Iniciar serviços
        Write-Log "Iniciando serviços..."
        docker-compose up -d

        Write-Success "Deploy concluído!"
    } catch {
        Write-Error "Falha no deploy: $_"
        exit 1
    }
}

# Verificar saúde dos serviços
function Test-Health {
    Write-Log "Verificando saúde dos serviços..."

    # Aguardar serviços ficarem prontos
    Write-Log "Aguardando serviços ficarem prontos..."
    Start-Sleep 30

    # Verificar status dos containers
    $containers = docker-compose ps --format "table {{.Name}}\t{{.State}}"
    Write-Info "Status dos containers:"
    Write-Host $containers

    # Testar endpoint de saúde
    Write-Log "Testando conectividade..."
    $maxWait = 60
    $waited = 0

    do {
        Start-Sleep 3
        $waited += 3
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health/" -TimeoutSec 5 -UseBasicParsing 2>$null
            if ($response.StatusCode -eq 200) {
                Write-Success "Aplicação está respondendo!"
                return $true
            }
        } catch {
            # Continuar tentando
        }
        Write-Log "Aguardando aplicação... ($waited/$maxWait segundos)"
    } while ($waited -lt $maxWait)

    Write-Warning "Timeout aguardando aplicação"
    Write-Log "Verificando logs da aplicação..."
    docker-compose logs --tail=20 web
    return $false
}

# Mostrar informações finais
function Show-FinalInfo {
    Write-Host ""
    Write-Host "🎉 DEPLOY AUTOMATIZADO CONCLUÍDO!" -ForegroundColor Green
    Write-Host "===================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Informações do Deploy:" -ForegroundColor Cyan
    Write-Host "• URL da aplicação: http://localhost:8000" -ForegroundColor White
    Write-Host "• Admin Django: http://localhost:8000/admin/" -ForegroundColor White
    Write-Host "• Health Check: http://localhost:8000/health/" -ForegroundColor White
    Write-Host "• Usuário admin padrão: admin / admin123" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Comandos úteis:" -ForegroundColor Cyan
    Write-Host "• Ver logs: docker-compose logs -f" -ForegroundColor White
    Write-Host "• Parar: docker-compose down" -ForegroundColor White
    Write-Host "• Reiniciar: docker-compose restart" -ForegroundColor White
    Write-Host "• Status: docker-compose ps" -ForegroundColor White
    Write-Host ""
    Write-Host "⚠️  IMPORTANTE:" -ForegroundColor Yellow
    Write-Host "• Altere a senha do admin após primeiro login" -ForegroundColor White
    Write-Host "• Configure HTTPS para produção" -ForegroundColor White
    Write-Host "• Faça backup regular do banco de dados" -ForegroundColor White
    Write-Host ""
}

# Mostrar ajuda
function Show-Help {
    Write-Host "🚀 DEPLOY AUTOMATIZADO HAVOC EM CONTAINER - WINDOWS" -ForegroundColor Blue
    Write-Host "====================================================" -ForegroundColor Blue
    Write-Host ""
    Write-Host "Uso: .\deploy_auto.ps1 [comando]" -ForegroundColor White
    Write-Host ""
    Write-Host "Comandos disponíveis:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  🤖 AUTOMATIZADO:" -ForegroundColor Green
    Write-Host "    auto      - Deploy totalmente automatizado com configuração interativa (PADRÃO)" -ForegroundColor White
    Write-Host "    config    - Apenas configuração interativa (gera .env)" -ForegroundColor White
    Write-Host ""
    Write-Host "  🔧 MANUAL:" -ForegroundColor Yellow
    Write-Host "    deploy    - Deploy completo (assume .env já configurado)" -ForegroundColor White
    Write-Host "    build     - Apenas construir a imagem Docker" -ForegroundColor White
    Write-Host "    test      - Executar testes de validação" -ForegroundColor White
    Write-Host ""
    Write-Host "  📊 GERENCIAMENTO:" -ForegroundColor Magenta
    Write-Host "    logs      - Ver logs em tempo real" -ForegroundColor White
    Write-Host "    stop      - Parar todos os containers" -ForegroundColor White
    Write-Host "    clean     - Limpar containers e volumes" -ForegroundColor White
    Write-Host "    secret    - Gerar nova SECRET_KEY" -ForegroundColor White
    Write-Host ""
    Write-Host "  ❓ AJUDA:" -ForegroundColor Blue
    Write-Host "    help      - Mostrar esta ajuda" -ForegroundColor White
    Write-Host ""
    Write-Host "Exemplos:" -ForegroundColor Cyan
    Write-Host "  .\deploy_auto.ps1              # Deploy automatizado (recomendado)" -ForegroundColor White
    Write-Host "  .\deploy_auto.ps1 auto         # Deploy automatizado" -ForegroundColor White
    Write-Host "  .\deploy_auto.ps1 config       # Apenas configurar .env" -ForegroundColor White
    Write-Host "  .\deploy_auto.ps1 deploy       # Deploy tradicional" -ForegroundColor White
    Write-Host ""
    Write-Host "🎯 Para primeira vez, use: .\deploy_auto.ps1 auto" -ForegroundColor Green
}

# Função principal
function Main {
    Write-Host "🚀 DEPLOY AUTOMATIZADO HAVOC EM CONTAINER - WINDOWS" -ForegroundColor Blue
    Write-Host "====================================================" -ForegroundColor Blue
    Write-Host ""

    switch ($Command.ToLower()) {
        { $_ -in @("auto", "") } {
            # Deploy automatizado completo
            Write-Log "🤖 DEPLOY TOTALMENTE AUTOMATIZADO" -Color "Blue"
            Write-Host ""
            Test-Dependencies
            Test-RequiredFiles
            Start-InteractiveSetup
            Start-Build
            Start-Deploy
            Test-Health
            Show-FinalInfo
        }
        "config" {
            # Apenas configuração
            Write-Log "⚙️ CONFIGURAÇÃO INTERATIVA" -Color "Blue"
            Write-Host ""
            Start-InteractiveSetup
            Write-Success "Configuração concluída! Execute '.\deploy_auto.ps1 deploy' para fazer o deploy"
        }
        "deploy" {
            # Deploy tradicional
            Test-Dependencies
            Test-RequiredFiles
            if (-not (Test-Path ".env")) {
                Write-Warning "Arquivo .env não encontrado!"
                if (Confirm-Action "Executar configuração interativa?" "y") {
                    Start-InteractiveSetup
                }
            }
            Start-Build
            Start-Deploy
            Test-Health
            Show-FinalInfo
        }
        "build" {
            Test-Dependencies
            Test-RequiredFiles
            Start-Build
        }
        "test" {
            Test-Dependencies
            Test-RequiredFiles
            Write-Success "Validação concluída com sucesso!"
        }
        "logs" {
            docker-compose logs -f
        }
        "stop" {
            docker-compose down
            Write-Success "Containers parados"
        }
        "clean" {
            Write-Log "Limpando containers e volumes..."
            docker-compose down -v
            docker system prune -f
            Write-Success "Limpeza concluída"
        }
        "secret" {
            $secretKey = New-SecretKey
            Write-Host "Nova SECRET_KEY gerada:" -ForegroundColor Green
            Write-Host $secretKey -ForegroundColor Yellow
        }
        { $_ -in @("help", "-h", "--help") } {
            Show-Help
        }
        default {
            Show-Help
            exit 1
        }
    }
}

# Executar função principal
try {
    Main
} catch {
    Write-Error "Erro durante execução: $_"
    exit 1
}
