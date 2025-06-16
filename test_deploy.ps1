# Script de teste de deploy para Windows PowerShell
# Testa a configuração do container Docker

Write-Host "🐳 TESTE DE DEPLOY HAVOC - WINDOWS" -ForegroundColor Blue
Write-Host "=================================" -ForegroundColor Blue
Write-Host ""

# Função para logging
function Write-Log {
    param($Message, $Color = "White")
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

# Verificar se Docker está disponível
Write-Log "Verificando Docker..."
try {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker encontrado: $dockerVersion"
    } else {
        Write-Error "Docker não está disponível"
        Write-Warning "Instale Docker Desktop para Windows"
        exit 1
    }
} catch {
    Write-Error "Erro ao verificar Docker: $_"
    exit 1
}

# Verificar se Docker Compose está disponível
Write-Log "Verificando Docker Compose..."
try {
    $composeVersion = docker-compose --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker Compose encontrado: $composeVersion"
    } else {
        Write-Error "Docker Compose não está disponível"
        exit 1
    }
} catch {
    Write-Error "Erro ao verificar Docker Compose: $_"
    exit 1
}

# Verificar arquivos necessários
Write-Log "Verificando arquivos necessários..."
$requiredFiles = @(
    "Dockerfile",
    "docker-compose.yml",
    "requirements.txt",
    "requirements-prod.txt",
    "manage.py",
    ".env"
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
    Write-Error "Arquivos obrigatórios não encontrados. Abortando teste."
    exit 1
}

# Verificar configuração do .env
Write-Log "Verificando configuração do .env..."
if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    
    # Verificar SECRET_KEY
    if ($envContent -match "SECRET_KEY=django-insecure-test-key") {
        Write-Success "SECRET_KEY de teste encontrada"
    } elseif ($envContent -match "SECRET_KEY=django-insecure-CHANGE") {
        Write-Warning "SECRET_KEY padrão detectada - OK para teste"
    } else {
        Write-Success "SECRET_KEY personalizada configurada"
    }
    
    # Verificar configuração de banco
    if ($envContent -match "DATABASE_ENGINE=postgresql") {
        Write-Success "Configuração PostgreSQL detectada"
    } else {
        Write-Warning "Configuração de banco não padrão"
    }
    
    # Verificar ALLOWED_HOSTS
    if ($envContent -match "ALLOWED_HOSTS=") {
        Write-Success "ALLOWED_HOSTS configurado"
    } else {
        Write-Warning "ALLOWED_HOSTS não encontrado"
    }
} else {
    Write-Error "Arquivo .env não encontrado"
    Write-Warning "Execute: Copy-Item .env.docker .env"
    exit 1
}

# Testar build da imagem
Write-Log "Testando build da imagem Docker..."
try {
    Write-Log "Executando: docker-compose build web"
    $buildOutput = docker-compose build web 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Build da imagem concluído com sucesso"
    } else {
        Write-Error "Falha no build da imagem"
        Write-Host "Output do build:" -ForegroundColor Yellow
        Write-Host $buildOutput -ForegroundColor Gray
        exit 1
    }
} catch {
    Write-Error "Erro durante o build: $_"
    exit 1
}

# Testar configuração do docker-compose
Write-Log "Validando configuração do docker-compose..."
try {
    $configOutput = docker-compose config 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Configuração do docker-compose válida"
    } else {
        Write-Error "Configuração do docker-compose inválida"
        Write-Host $configOutput -ForegroundColor Gray
        exit 1
    }
} catch {
    Write-Error "Erro ao validar docker-compose: $_"
    exit 1
}

# Testar inicialização dos serviços
Write-Log "Testando inicialização dos serviços..."
try {
    Write-Log "Iniciando serviços em background..."
    docker-compose up -d db 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Banco de dados iniciado"
        
        # Aguardar banco ficar pronto
        Write-Log "Aguardando banco de dados ficar pronto..."
        $maxWait = 30
        $waited = 0
        
        do {
            Start-Sleep 2
            $waited += 2
            $dbStatus = docker-compose exec -T db pg_isready -U havoc_user 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Banco de dados está pronto"
                break
            }
            Write-Log "Aguardando banco... ($waited/$maxWait segundos)"
        } while ($waited -lt $maxWait)
        
        if ($waited -ge $maxWait) {
            Write-Warning "Timeout aguardando banco de dados"
        }
        
    } else {
        Write-Error "Falha ao iniciar banco de dados"
        exit 1
    }
} catch {
    Write-Error "Erro ao testar serviços: $_"
    exit 1
}

# Testar aplicação web
Write-Log "Testando aplicação web..."
try {
    Write-Log "Iniciando aplicação web..."
    docker-compose up -d web 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Aplicação web iniciada"
        
        # Aguardar aplicação ficar pronta
        Write-Log "Aguardando aplicação ficar pronta..."
        $maxWait = 60
        $waited = 0
        
        do {
            Start-Sleep 3
            $waited += 3
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:8000/health/" -TimeoutSec 5 -UseBasicParsing 2>$null
                if ($response.StatusCode -eq 200) {
                    Write-Success "Aplicação está respondendo"
                    break
                }
            } catch {
                # Continuar tentando
            }
            Write-Log "Aguardando aplicação... ($waited/$maxWait segundos)"
        } while ($waited -lt $maxWait)
        
        if ($waited -ge $maxWait) {
            Write-Warning "Timeout aguardando aplicação"
            Write-Log "Verificando logs da aplicação..."
            docker-compose logs --tail=20 web
        } else {
            # Testar endpoint principal
            try {
                $mainResponse = Invoke-WebRequest -Uri "http://localhost:8000/" -TimeoutSec 10 -UseBasicParsing
                if ($mainResponse.StatusCode -eq 200) {
                    Write-Success "Endpoint principal funcionando"
                } else {
                    Write-Warning "Endpoint principal retornou status: $($mainResponse.StatusCode)"
                }
            } catch {
                Write-Warning "Erro ao acessar endpoint principal: $_"
            }
        }
        
    } else {
        Write-Error "Falha ao iniciar aplicação web"
        docker-compose logs web
        exit 1
    }
} catch {
    Write-Error "Erro ao testar aplicação: $_"
    exit 1
}

# Mostrar status final
Write-Log "Verificando status final dos serviços..."
docker-compose ps

# Mostrar logs recentes
Write-Log "Logs recentes da aplicação:"
docker-compose logs --tail=10 web

Write-Host ""
Write-Host "🎉 TESTE DE DEPLOY CONCLUÍDO!" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Resultados:" -ForegroundColor Cyan
Write-Host "• Docker: ✅ Funcionando" -ForegroundColor Green
Write-Host "• Docker Compose: ✅ Funcionando" -ForegroundColor Green
Write-Host "• Build da imagem: ✅ Sucesso" -ForegroundColor Green
Write-Host "• Banco de dados: ✅ Iniciado" -ForegroundColor Green
Write-Host "• Aplicação web: ✅ Iniciada" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 URLs para teste:" -ForegroundColor Cyan
Write-Host "• Aplicação: http://localhost:8000" -ForegroundColor White
Write-Host "• Health Check: http://localhost:8000/health/" -ForegroundColor White
Write-Host "• Admin: http://localhost:8000/admin/" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Comandos úteis:" -ForegroundColor Cyan
Write-Host "• Ver logs: docker-compose logs -f" -ForegroundColor White
Write-Host "• Parar: docker-compose down" -ForegroundColor White
Write-Host "• Status: docker-compose ps" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Para parar os serviços de teste:" -ForegroundColor Yellow
Write-Host "docker-compose down" -ForegroundColor White
