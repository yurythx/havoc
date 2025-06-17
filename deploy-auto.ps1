# =============================================================================
# SCRIPT DE DEPLOY AUTOMATIZADO WINDOWS - PROJETO HAVOC
# Deploy inteligente que detecta o ambiente e executa a melhor estratégia
# =============================================================================

param(
    [string]$Command = "auto",
    [string]$ForceEnv = "",
    [switch]$EnvOnly = $false,
    [switch]$Check = $false,
    [switch]$Help = $false
)

# Configurações
$ErrorActionPreference = "Stop"

# Função para logging com cores
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

# Banner
function Show-Banner {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║                    🚀 HAVOC AUTO DEPLOY 🚀                   ║" -ForegroundColor Magenta
    Write-Host "║                                                              ║" -ForegroundColor Magenta
    Write-Host "║  Deploy Automatizado Inteligente para Windows               ║" -ForegroundColor Magenta
    Write-Host "║  Detecta ambiente e executa a melhor estratégia             ║" -ForegroundColor Magenta
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
}

# Função para detectar ambiente
function Detect-Environment {
    Write-Log "Detectando ambiente de execução..."
    
    # Verificar se Docker está disponível
    try {
        $dockerVersion = docker --version 2>$null
        $composeVersion = docker-compose --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $script:Environment = "docker"
            Write-Info "Ambiente: Docker disponível"
            return
        }
    } catch {
        # Docker não disponível
    }
    
    # Verificar se Python está disponível
    try {
        $pythonVersion = python --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $script:Environment = "python"
            Write-Info "Ambiente: Python disponível"
            return
        }
    } catch {
        # Python não disponível
    }
    
    # Fallback para Windows
    $script:Environment = "windows"
    Write-Info "Ambiente: Windows PowerShell"
}

# Função para verificar pré-requisitos
function Test-Prerequisites {
    Write-Log "Verificando pré-requisitos..."
    
    switch ($script:Environment) {
        "docker" {
            try {
                docker --version | Out-Null
                docker-compose --version | Out-Null
                Write-Success "Docker e Docker Compose disponíveis"
            } catch {
                Write-Error "Docker não está funcionando corretamente"
                exit 1
            }
        }
        "python" {
            try {
                python --version | Out-Null
                Write-Success "Python disponível"
            } catch {
                Write-Error "Python não está funcionando corretamente"
                exit 1
            }
        }
        "windows" {
            if (!(Test-Path "scripts\deploy_simples.ps1")) {
                Write-Error "Script deploy_simples.ps1 não encontrado"
                exit 1
            }
            Write-Success "Scripts PowerShell disponíveis"
        }
    }
}

# Função para configurar arquivo .env
function Setup-EnvFile {
    Write-Log "Configurando arquivo de ambiente..."
    
    if (!(Test-Path ".env")) {
        if (Test-Path ".env.example") {
            Copy-Item ".env.example" ".env"
            Write-Success "Arquivo .env criado a partir do .env.example"
        } else {
            # Criar .env básico
            $envContent = @"
# Configuração básica gerada automaticamente
ENVIRONMENT=development
DEBUG=True
DJANGO_SECRET_KEY=django-insecure-auto-generated-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_ENGINE=sqlite
DATABASE_NAME=db.sqlite3
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
"@
            $envContent | Out-File -FilePath ".env" -Encoding UTF8
            Write-Success "Arquivo .env básico criado"
        }
        
        Write-Warning "IMPORTANTE: Edite o arquivo .env com suas configurações antes do deploy em produção"
    } else {
        Write-Info "Arquivo .env já existe"
    }
}

# Deploy via Docker
function Deploy-Docker {
    Write-Log "Executando deploy via Docker..."
    
    if (!(Test-Path "docker-compose.yml")) {
        Write-Error "Arquivo docker-compose.yml não encontrado"
        exit 1
    }
    
    Write-Log "Construindo imagens..."
    docker-compose build
    
    Write-Log "Iniciando serviços..."
    docker-compose up -d
    
    Write-Log "Aguardando serviços ficarem prontos..."
    Start-Sleep -Seconds 30
    
    # Verificar health check
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health/" -TimeoutSec 10 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Success "Aplicação está funcionando!"
        }
    } catch {
        Write-Warning "Health check falhou, mas serviços podem estar iniciando"
    }
    
    # Mostrar status
    docker-compose ps
}

# Deploy via Python
function Deploy-Python {
    Write-Log "Executando deploy via Python..."
    
    if (Test-Path "scripts\deploy_simples.ps1") {
        Set-Location "scripts"
        .\deploy_simples.ps1 dev
        Set-Location ".."
    } else {
        Write-Error "Script deploy_simples.ps1 não encontrado"
        exit 1
    }
}

# Deploy via Windows
function Deploy-Windows {
    Write-Log "Executando deploy via Windows PowerShell..."
    
    if (Test-Path "scripts\deploy_simples.ps1") {
        Set-Location "scripts"
        .\deploy_simples.ps1 dev
        Set-Location ".."
    } else {
        Write-Error "Script deploy_simples.ps1 não encontrado"
        exit 1
    }
}

# Função principal de deploy
function Invoke-Deploy {
    switch ($script:Environment) {
        "docker" {
            Deploy-Docker
        }
        "python" {
            Deploy-Python
        }
        "windows" {
            Deploy-Windows
        }
        default {
            Write-Error "Ambiente não suportado: $($script:Environment)"
            exit 1
        }
    }
}

# Função para mostrar informações pós-deploy
function Show-PostDeployInfo {
    Write-Host ""
    Write-Success "🎉 Deploy automatizado concluído!"
    Write-Host ""
    Write-Info "📋 Informações de acesso:"
    Write-Host "• URL Principal: http://localhost:8000"
    Write-Host "• Admin Django: http://localhost:8000/admin/"
    Write-Host "• Health Check: http://localhost:8000/health/"
    Write-Host ""
    Write-Info "🔑 Credenciais padrão:"
    Write-Host "• Usuário: admin@havoc.com"
    Write-Host "• Senha: admin123"
    Write-Host ""
    
    switch ($script:Environment) {
        "docker" {
            Write-Info "🐳 Comandos Docker úteis:"
            Write-Host "• Ver logs: docker-compose logs -f"
            Write-Host "• Parar: docker-compose down"
            Write-Host "• Status: docker-compose ps"
        }
        default {
            Write-Info "💻 Comandos úteis:"
            Write-Host "• Verificar: .\scripts\deploy_simples.ps1 check"
            Write-Host "• Limpar: .\scripts\deploy_simples.ps1 clean"
            Write-Host "• Reativar env: .\env\Scripts\Activate.ps1"
        }
    }
    
    Write-Host ""
    Write-Warning "⚠️  Para produção, lembre-se de:"
    Write-Host "• Configurar SECRET_KEY segura no .env"
    Write-Host "• Configurar banco PostgreSQL"
    Write-Host "• Configurar HTTPS"
    Write-Host "• Configurar backup automático"
}

# Função de ajuda
function Show-Help {
    Write-Host "🚀 HAVOC AUTO DEPLOY - WINDOWS"
    Write-Host "=============================="
    Write-Host ""
    Write-Host "Deploy automatizado inteligente que detecta o ambiente e executa a melhor estratégia."
    Write-Host ""
    Write-Host "Uso: .\deploy-auto.ps1 [opções]"
    Write-Host ""
    Write-Host "Opções:"
    Write-Host "  -Help              Mostra esta ajuda"
    Write-Host "  -EnvOnly           Apenas configura arquivo .env"
    Write-Host "  -Check             Apenas verifica pré-requisitos"
    Write-Host "  -ForceEnv <env>    Força detecção de ambiente específico"
    Write-Host "                     Valores: docker, python, windows"
    Write-Host ""
    Write-Host "Exemplos:"
    Write-Host "  .\deploy-auto.ps1                    # Deploy automático"
    Write-Host "  .\deploy-auto.ps1 -Check             # Apenas verificar sistema"
    Write-Host "  .\deploy-auto.ps1 -ForceEnv docker   # Forçar deploy via Docker"
    Write-Host ""
}

# Função principal
function Main {
    # Processar argumentos
    if ($Help) {
        Show-Help
        return
    }
    
    if ($EnvOnly) {
        Setup-EnvFile
        return
    }
    
    if ($Check) {
        Show-Banner
        if ($ForceEnv) {
            $script:Environment = $ForceEnv
            Write-Info "Ambiente forçado: $($script:Environment)"
        } else {
            Detect-Environment
        }
        Test-Prerequisites
        Write-Success "Sistema verificado com sucesso!"
        return
    }
    
    # Executar deploy
    Show-Banner
    
    # Detectar ambiente se não foi forçado
    if ($ForceEnv) {
        $script:Environment = $ForceEnv
        Write-Info "Ambiente forçado: $($script:Environment)"
    } else {
        Detect-Environment
    }
    
    Test-Prerequisites
    Setup-EnvFile
    Invoke-Deploy
    Show-PostDeployInfo
}

# Executar função principal
Main
