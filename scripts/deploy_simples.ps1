# =============================================================================
# SCRIPT DE DEPLOY SIMPLES PARA WINDOWS - PROJETO HAVOC
# =============================================================================

param(
    [string]$Command = "dev"
)

# Funcao para logging
function Write-Log {
    param([string]$Message, [string]$Type = "Info")
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    switch ($Type) {
        "Success" { Write-Host "[$timestamp] SUCCESS: $Message" -ForegroundColor Green }
        "Warning" { Write-Host "[$timestamp] WARNING: $Message" -ForegroundColor Yellow }
        "Error"   { Write-Host "[$timestamp] ERROR: $Message" -ForegroundColor Red }
        "Info"    { Write-Host "[$timestamp] INFO: $Message" -ForegroundColor Cyan }
        default   { Write-Host "[$timestamp] $Message" -ForegroundColor Blue }
    }
}

# Funcao para limpar variaveis de ambiente
function Clear-Environment {
    Write-Log "Limpando variaveis de ambiente conflitantes..."
    
    # Limpar variaveis de banco
    $env:DATABASE_ENGINE = $null
    $env:DB_NAME = $null
    $env:DB_USER = $null
    $env:DB_PASSWORD = $null
    $env:DB_HOST = $null
    $env:DB_PORT = $null
    $env:DATABASE_URL = $null
    
    # Limpar variaveis de log
    $env:LOG_FILE = $null
    
    # Definir configuracao padrao
    $env:DJANGO_SETTINGS_MODULE = "core.settings"
    
    Write-Log "Variaveis de ambiente limpas" "Success"
}

# Funcao para gerar SECRET_KEY melhorada
function New-SecretKey {
    try {
        # Tentar usar Django se estiver disponivel
        $key = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>$null
        if ($key -and $key.Length -gt 20) {
            return $key
        }
    }
    catch {
        # Continuar para fallback
    }

    try {
        # Fallback: usar Python com secrets
        $key = python -c "
import secrets
import string
chars = string.ascii_letters + string.digits + '!@#`$%^&*(-_=+)'
print(''.join(secrets.choice(chars) for _ in range(50)))
" 2>$null
        if ($key -and $key.Length -gt 20) {
            return $key
        }
    }
    catch {
        # Continuar para fallback final
    }

    # Ultimo fallback: gerar chave usando PowerShell
    $chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)"
    $key = ""
    for ($i = 0; $i -lt 50; $i++) {
        $key += $chars[(Get-Random -Maximum $chars.Length)]
    }
    return $key
}

# Funcao para verificar dependencias
function Test-Dependencies {
    Write-Log "Verificando dependencias..."
    
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Log "Python nao encontrado!" "Error"
        exit 1
    }
    
    if (-not (Get-Command pip -ErrorAction SilentlyContinue)) {
        Write-Log "Pip nao encontrado!" "Error"
        exit 1
    }
    
    Write-Log "Dependencias verificadas" "Success"
}

# Funcao para verificar arquivos
function Test-Files {
    Write-Log "Verificando arquivos necessarios..."
    
    $requiredFiles = @("manage.py", "requirements.txt", "core/settings.py")
    
    foreach ($file in $requiredFiles) {
        if (-not (Test-Path $file)) {
            Write-Log "Arquivo obrigatorio nao encontrado: $file" "Error"
            exit 1
        }
    }
    
    Write-Log "Arquivos verificados" "Success"
}

# Funcao para configurar ambiente de desenvolvimento
function Set-DevelopmentEnvironment {
    Write-Log "Configurando ambiente de desenvolvimento..."
    
    $secretKey = New-SecretKey
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    $envContent = @"
# Configuracoes de desenvolvimento - Havoc
# Gerado em: $timestamp

ENVIRONMENT=development
DEBUG=True
DJANGO_SECRET_KEY=$secretKey
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
DATABASE_ENGINE=sqlite
DATABASE_NAME=db.sqlite3
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@havoc.local
LOG_LEVEL=DEBUG
SITE_NAME=Havoc
SITE_URL=http://localhost:8000
FILE_UPLOAD_MAX_MEMORY_SIZE=5242880
DATA_UPLOAD_MAX_MEMORY_SIZE=5242880
SECURE_SSL_REDIRECT=False
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Log "Arquivo .env criado para desenvolvimento" "Success"
}

# Funcao para instalar dependencias
function Install-Dependencies {
    Write-Log "Instalando dependencias Python..."
    
    # Verificar ambiente virtual
    if (-not (Test-Path "env") -and -not $env:VIRTUAL_ENV) {
        Write-Log "Criando ambiente virtual..."
        python -m venv env
        & ".\env\Scripts\Activate.ps1"
    }
    
    # Ativar ambiente virtual se existir
    if ((Test-Path "env\Scripts\Activate.ps1") -and -not $env:VIRTUAL_ENV) {
        & ".\env\Scripts\Activate.ps1"
    }
    
    # Instalar dependencias
    pip install -r requirements.txt
    
    Write-Log "Dependencias instaladas" "Success"
}

# Funcao para executar migracoes
function Invoke-Migrations {
    Write-Log "Executando migracoes do banco de dados..."
    
    if ((Test-Path "env\Scripts\Activate.ps1") -and -not $env:VIRTUAL_ENV) {
        & ".\env\Scripts\Activate.ps1"
    }
    
    python manage.py migrate
    Write-Log "Migracoes executadas" "Success"
}

# Funcao para criar superusuario
function New-Superuser {
    Write-Log "Criando superusuario padrao..."
    
    if ((Test-Path "env\Scripts\Activate.ps1") -and -not $env:VIRTUAL_ENV) {
        & ".\env\Scripts\Activate.ps1"
    }
    
    $createUserScript = @"
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@havoc.com').exists():
    User.objects.create_superuser('admin@havoc.com', 'admin123', email='admin@havoc.com', first_name='Admin', last_name='Havoc')
    print('Superusuario criado: admin@havoc.com / admin123')
else:
    print('Superusuario ja existe')
"@
    
    python manage.py shell -c $createUserScript
    Write-Log "Superusuario configurado" "Success"
}

# Funcao para coletar arquivos estaticos
function Invoke-CollectStatic {
    Write-Log "Coletando arquivos estaticos..."
    
    if ((Test-Path "env\Scripts\Activate.ps1") -and -not $env:VIRTUAL_ENV) {
        & ".\env\Scripts\Activate.ps1"
    }
    
    python manage.py collectstatic --noinput
    Write-Log "Arquivos estaticos coletados" "Success"
}

# Funcao para executar testes
function Invoke-Tests {
    Write-Log "Executando verificacoes do sistema..."
    
    if ((Test-Path "env\Scripts\Activate.ps1") -and -not $env:VIRTUAL_ENV) {
        & ".\env\Scripts\Activate.ps1"
    }
    
    python manage.py check
    Write-Log "Verificacoes do sistema passaram" "Success"
}

# Funcao principal para deploy de desenvolvimento
function Deploy-Development {
    Write-Host "DEPLOY DE DESENVOLVIMENTO - HAVOC" -ForegroundColor Magenta
    Write-Host "==================================" -ForegroundColor Magenta
    Write-Host ""
    
    Clear-Environment
    Test-Dependencies
    Test-Files
    Set-DevelopmentEnvironment
    Install-Dependencies
    Invoke-Migrations
    New-Superuser
    Invoke-CollectStatic
    Invoke-Tests
    
    Write-Host ""
    Write-Log "Deploy de desenvolvimento concluido!" "Success"
    Write-Host ""
    Write-Log "Informacoes importantes:" "Info"
    Write-Host "• URL: http://localhost:8000"
    Write-Host "• Admin: http://localhost:8000/admin/"
    Write-Host "• Usuario: admin@havoc.com"
    Write-Host "• Senha: admin123"
    Write-Host ""
    
    $response = Read-Host "Deseja iniciar o servidor agora? [Y/n]"
    if ($response -notmatch '^[nN]') {
        Write-Log "Iniciando servidor..." "Info"
        python manage.py runserver
    }
    else {
        Write-Log "Para iniciar o servidor: python manage.py runserver" "Info"
    }
}

# Menu principal
switch ($Command.ToLower()) {
    "dev" {
        Deploy-Development
    }
    "development" {
        Deploy-Development
    }
    "check" {
        Clear-Environment
        Test-Dependencies
        Test-Files
        Invoke-Tests
        Write-Log "Verificacoes concluidas" "Success"
    }
    "clean" {
        Clear-Environment
        Write-Log "Ambiente limpo" "Success"
    }
    "secret" {
        Write-Host "Nova SECRET_KEY:"
        New-SecretKey
    }
    "help" {
        Write-Host "DEPLOY MELHORADO - HAVOC" -ForegroundColor Magenta
        Write-Host "========================" -ForegroundColor Magenta
        Write-Host ""
        Write-Host "Uso: .\deploy_simples.ps1 [comando]"
        Write-Host ""
        Write-Host "Comandos:"
        Write-Host "  dev        - Deploy de desenvolvimento (padrao)"
        Write-Host "  check      - Verificar sistema"
        Write-Host "  clean      - Limpar ambiente"
        Write-Host "  secret     - Gerar SECRET_KEY"
        Write-Host "  help       - Mostrar ajuda"
        Write-Host ""
    }
    default {
        Write-Log "Comando invalido. Use '.\deploy_simples.ps1 help' para ver opcoes disponiveis." "Error"
        exit 1
    }
}
