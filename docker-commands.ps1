# Script PowerShell para comandos Docker do projeto Havoc
# Uso: .\docker-commands.ps1 <comando>

param(
    [Parameter(Mandatory=$true)]
    [string]$Command
)

# Cores para output
$Red = "`e[31m"
$Green = "`e[32m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Reset = "`e[0m"

# Função para logging
function Write-Log {
    param([string]$Message, [string]$Color = $Reset)
    Write-Host "${Color}$Message${Reset}"
}

# Variáveis
$DockerCompose = "docker-compose"
$DockerComposeDev = "docker-compose -f docker-compose.dev.yml"
$DockerComposeProd = "docker-compose -f docker-compose.yml"

switch ($Command.ToLower()) {
    "help" {
        Write-Log "Comandos disponíveis para o projeto Havoc:" $Blue
        Write-Log ""
        Write-Log "DESENVOLVIMENTO:" $Green
        Write-Log "  dev-build          Constrói imagens para desenvolvimento"
        Write-Log "  dev-up             Inicia serviços em desenvolvimento"
        Write-Log "  dev-down           Para serviços de desenvolvimento"
        Write-Log "  dev-logs           Mostra logs de desenvolvimento"
        Write-Log "  dev-shell          Shell do container de desenvolvimento"
        Write-Log "  dev-migrate        Executa migrações em desenvolvimento"
        Write-Log "  dev-test           Executa testes em desenvolvimento"
        Write-Log ""
        Write-Log "PRODUÇÃO:" $Green
        Write-Log "  build              Constrói imagens para produção"
        Write-Log "  up                 Inicia serviços em produção"
        Write-Log "  down               Para serviços de produção"
        Write-Log "  logs               Mostra logs de produção"
        Write-Log "  shell              Shell do container de produção"
        Write-Log "  migrate            Executa migrações em produção"
        Write-Log "  deploy             Deploy completo"
        Write-Log ""
        Write-Log "MANUTENÇÃO:" $Green
        Write-Log "  status             Status dos serviços"
        Write-Log "  restart            Reinicia serviços"
        Write-Log "  backup-db          Backup do banco de dados"
        Write-Log "  clean              Limpa recursos Docker"
        Write-Log ""
        Write-Log "CONFIGURAÇÃO:" $Green
        Write-Log "  setup-env          Cria arquivo .env"
        Write-Log "  init               Inicialização completa"
    }
    
    # Comandos de desenvolvimento
    "dev-build" {
        Write-Log "Construindo imagens para desenvolvimento..." $Yellow
        & $DockerComposeDev.Split() build
    }
    
    "dev-up" {
        Write-Log "Iniciando serviços em modo desenvolvimento..." $Yellow
        & $DockerComposeDev.Split() up -d
    }
    
    "dev-down" {
        Write-Log "Parando serviços de desenvolvimento..." $Yellow
        & $DockerComposeDev.Split() down
    }
    
    "dev-logs" {
        & $DockerComposeDev.Split() logs -f
    }
    
    "dev-shell" {
        & $DockerComposeDev.Split() exec web bash
    }
    
    "dev-migrate" {
        & $DockerComposeDev.Split() exec web python manage.py migrate
    }
    
    "dev-test" {
        & $DockerComposeDev.Split() exec web python manage.py test
    }
    
    # Comandos de produção
    "build" {
        Write-Log "Construindo imagens para produção..." $Yellow
        & $DockerComposeProd.Split() build
    }
    
    "up" {
        Write-Log "Iniciando serviços em modo produção..." $Yellow
        & $DockerComposeProd.Split() up -d
    }
    
    "down" {
        Write-Log "Parando serviços de produção..." $Yellow
        & $DockerComposeProd.Split() down
    }
    
    "logs" {
        & $DockerComposeProd.Split() logs -f
    }
    
    "shell" {
        & $DockerComposeProd.Split() exec web bash
    }
    
    "migrate" {
        & $DockerComposeProd.Split() exec web python manage.py migrate
    }
    
    "collectstatic" {
        & $DockerComposeProd.Split() exec web python manage.py collectstatic --noinput
    }
    
    # Comandos de manutenção
    "status" {
        & $DockerComposeProd.Split() ps
    }
    
    "restart" {
        Write-Log "Reiniciando serviços..." $Yellow
        & $DockerComposeProd.Split() restart
    }
    
    "backup-db" {
        Write-Log "Fazendo backup do banco de dados..." $Yellow
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        & $DockerComposeProd.Split() exec db pg_dump -U postgres havoc_prod > "backup_$timestamp.sql"
        Write-Log "Backup salvo como backup_$timestamp.sql" $Green
    }
    
    "clean" {
        Write-Log "Limpando recursos Docker..." $Yellow
        docker system prune -f
        docker volume prune -f
    }
    
    # Comandos de configuração
    "setup-env" {
        if (!(Test-Path ".env")) {
            Write-Log "Criando arquivo .env..." $Yellow
            Copy-Item ".env.prod" ".env"
            Write-Log "Arquivo .env criado! Edite-o com suas configurações." $Green
        } else {
            Write-Log "Arquivo .env já existe." $Yellow
        }
    }
    
    "init" {
        Write-Log "Inicializando projeto Havoc..." $Green
        & $MyInvocation.MyCommand.Path "setup-env"
        & $MyInvocation.MyCommand.Path "dev-build"
        & $MyInvocation.MyCommand.Path "dev-up"
        Write-Log "Aguardando serviços..." $Yellow
        Start-Sleep -Seconds 30
        & $MyInvocation.MyCommand.Path "dev-migrate"
        Write-Log "Projeto inicializado! Acesse http://localhost:8000" $Green
    }
    
    "deploy" {
        Write-Log "Iniciando deploy..." $Green
        & $MyInvocation.MyCommand.Path "build"
        & $MyInvocation.MyCommand.Path "up"
        Write-Log "Aguardando serviços..." $Yellow
        Start-Sleep -Seconds 30
        & $MyInvocation.MyCommand.Path "migrate"
        & $MyInvocation.MyCommand.Path "collectstatic"
        Write-Log "Deploy concluído!" $Green
    }
    
    default {
        Write-Log "Comando não reconhecido: $Command" $Red
        Write-Log "Use '.\docker-commands.ps1 help' para ver comandos disponíveis" $Yellow
    }
}

# Exemplos de uso:
# .\docker-commands.ps1 help
# .\docker-commands.ps1 init
# .\docker-commands.ps1 dev-up
# .\docker-commands.ps1 deploy
