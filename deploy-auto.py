#!/usr/bin/env python3
"""
SCRIPT DE DEPLOY AUTOMATIZADO PYTHON - PROJETO HAVOC
Deploy inteligente multiplataforma que detecta o ambiente e executa a melhor estratégia
"""

import os
import sys
import platform
import subprocess
import shutil
import time
import argparse
from pathlib import Path

# Cores para terminal
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

def log(message, color=Colors.BLUE):
    """Log com timestamp e cor"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"{color}[{timestamp}]{Colors.NC} {message}")

def success(message):
    """Mensagem de sucesso"""
    print(f"{Colors.GREEN}✅ {message}{Colors.NC}")

def warning(message):
    """Mensagem de aviso"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.NC}")

def error(message):
    """Mensagem de erro"""
    print(f"{Colors.RED}❌ {message}{Colors.NC}")

def info(message):
    """Mensagem informativa"""
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.NC}")

def show_banner():
    """Mostra banner do aplicativo"""
    print(f"{Colors.PURPLE}")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                    🚀 HAVOC AUTO DEPLOY 🚀                   ║")
    print("║                                                              ║")
    print("║  Deploy Automatizado Inteligente Multiplataforma            ║")
    print("║  Detecta ambiente e executa a melhor estratégia             ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"{Colors.NC}")
    print()

def run_command(command, shell=True, check=True):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(command, shell=shell, check=check, 
                              capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr
    except Exception as e:
        return False, "", str(e)

def detect_environment():
    """Detecta o ambiente de execução"""
    log("Detectando ambiente de execução...")
    
    # Verificar se é container
    if Path('/.dockerenv').exists():
        info("Ambiente: Container Docker")
        return "container"
    
    # Verificar se Docker está disponível
    docker_ok, _, _ = run_command("docker --version", check=False)
    compose_ok, _, _ = run_command("docker-compose --version", check=False)
    
    if docker_ok and compose_ok:
        info("Ambiente: Docker disponível")
        return "docker"
    
    # Detectar sistema operacional
    system = platform.system().lower()
    
    if system == "linux":
        # Verificar se é Ubuntu
        if Path('/etc/lsb-release').exists():
            with open('/etc/lsb-release', 'r') as f:
                content = f.read()
                if 'Ubuntu' in content:
                    info(f"Ambiente: Ubuntu Linux")
                    return "ubuntu"
        info("Ambiente: Linux genérico")
        return "linux"
    
    elif system == "windows":
        info("Ambiente: Windows")
        return "windows"
    
    elif system == "darwin":
        info("Ambiente: macOS")
        return "macos"
    
    else:
        warning("Ambiente não detectado, usando configuração genérica")
        return "unknown"

def check_prerequisites(environment):
    """Verifica pré-requisitos do ambiente"""
    log("Verificando pré-requisitos...")
    
    if environment == "docker":
        docker_ok, _, _ = run_command("docker --version", check=False)
        compose_ok, _, _ = run_command("docker-compose --version", check=False)
        
        if not docker_ok:
            error("Docker não está funcionando")
            return False
        if not compose_ok:
            error("Docker Compose não está funcionando")
            return False
        
        success("Docker e Docker Compose disponíveis")
        return True
    
    elif environment in ["ubuntu", "linux", "macos"]:
        python_ok, _, _ = run_command("python3 --version", check=False)
        if not python_ok:
            warning("Python3 não encontrado, pode precisar ser instalado")
        else:
            success("Python3 disponível")
        return True
    
    elif environment == "windows":
        python_ok, _, _ = run_command("python --version", check=False)
        if not python_ok:
            error("Python não encontrado no Windows")
            return False
        success("Python disponível")
        return True
    
    return True

def setup_env_file():
    """Configura arquivo .env"""
    log("Configurando arquivo de ambiente...")
    
    if not Path('.env').exists():
        if Path('.env.example').exists():
            shutil.copy('.env.example', '.env')
            success("Arquivo .env criado a partir do .env.example")
        else:
            # Criar .env básico
            env_content = """# Configuração básica gerada automaticamente
ENVIRONMENT=development
DEBUG=True
DJANGO_SECRET_KEY=django-insecure-auto-generated-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_ENGINE=sqlite
DATABASE_NAME=db.sqlite3
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
"""
            with open('.env', 'w') as f:
                f.write(env_content)
            success("Arquivo .env básico criado")
        
        warning("IMPORTANTE: Edite o arquivo .env com suas configurações antes do deploy em produção")
    else:
        info("Arquivo .env já existe")

def deploy_docker():
    """Deploy via Docker"""
    log("Executando deploy via Docker...")

    if not Path('docker-compose.yml').exists():
        error("Arquivo docker-compose.yml não encontrado")
        return False

    # Verificar se existe .env.docker e copiar para .env
    env_docker_path = Path('.env.docker')
    env_path = Path('.env')

    if env_docker_path.exists():
        log("Usando configurações do .env.docker...")
        import shutil
        shutil.copy2(env_docker_path, env_path)

    log("Construindo imagens...")
    success_build, _, _ = run_command("docker-compose build")
    if not success_build:
        error("Falha ao construir imagens Docker")
        return False
    
    log("Iniciando serviços...")
    success_up, _, _ = run_command("docker-compose up -d")
    if not success_up:
        error("Falha ao iniciar serviços")
        return False
    
    log("Aguardando serviços ficarem prontos...")
    time.sleep(30)
    
    # Verificar health check
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:8000/health/", timeout=10)
        success("Aplicação está funcionando!")
    except:
        warning("Health check falhou, mas serviços podem estar iniciando")
    
    # Mostrar status
    run_command("docker-compose ps")
    return True

def deploy_ubuntu():
    """Deploy via Ubuntu"""
    log("Executando deploy via Ubuntu...")
    
    script_path = Path("scripts/deploy_ubuntu.sh")
    if script_path.exists():
        os.chmod(script_path, 0o755)
        os.chdir("scripts")
        success_deploy, _, _ = run_command("./deploy_ubuntu.sh dev")
        os.chdir("..")
        return success_deploy
    else:
        error("Script deploy_ubuntu.sh não encontrado")
        return False

def deploy_linux():
    """Deploy via Linux genérico"""
    log("Executando deploy via Linux...")
    
    script_path = Path("scripts/deploy_melhorado.sh")
    if script_path.exists():
        os.chmod(script_path, 0o755)
        os.chdir("scripts")
        success_deploy, _, _ = run_command("./deploy_melhorado.sh dev")
        os.chdir("..")
        return success_deploy
    else:
        error("Script deploy_melhorado.sh não encontrado")
        return False

def deploy_windows():
    """Deploy via Windows"""
    log("Executando deploy via Windows...")
    
    script_path = Path("scripts/deploy_simples.ps1")
    if script_path.exists():
        info("Execute o seguinte comando no PowerShell:")
        print("cd scripts")
        print(".\\deploy_simples.ps1 dev")
        return True
    else:
        error("Script deploy_simples.ps1 não encontrado")
        return False

def execute_deploy(environment):
    """Executa deploy baseado no ambiente"""
    if environment == "docker":
        return deploy_docker()
    elif environment == "ubuntu":
        return deploy_ubuntu()
    elif environment in ["linux", "macos"]:
        return deploy_linux()
    elif environment == "windows":
        return deploy_windows()
    elif environment == "container":
        info("Executando dentro de container, nada a fazer")
        return True
    else:
        error(f"Ambiente não suportado: {environment}")
        return False

def show_post_deploy_info(environment):
    """Mostra informações pós-deploy"""
    print()
    success("🎉 Deploy automatizado concluído!")
    print()
    info("📋 Informações de acesso:")
    print("• URL Principal: http://localhost:8000")
    print("• Admin Django: http://localhost:8000/admin/")
    print("• Health Check: http://localhost:8000/health/")
    print()
    info("🔑 Credenciais padrão:")
    print("• Usuário: admin@havoc.com")
    print("• Senha: admin123")
    print()
    
    if environment == "docker":
        info("🐳 Comandos Docker úteis:")
        print("• Ver logs: docker-compose logs -f")
        print("• Parar: docker-compose down")
        print("• Status: docker-compose ps")
    else:
        info("💻 Comandos úteis:")
        print("• Verificar: python deploy-auto.py --check")
        print("• Reativar env: source env/bin/activate (Linux/Mac)")
    
    print()
    warning("⚠️  Para produção, lembre-se de:")
    print("• Configurar SECRET_KEY segura no .env")
    print("• Configurar banco PostgreSQL")
    print("• Configurar HTTPS")
    print("• Configurar backup automático")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Deploy automatizado inteligente do Havoc")
    parser.add_argument("--env-only", action="store_true", help="Apenas configura arquivo .env")
    parser.add_argument("--check", action="store_true", help="Apenas verifica pré-requisitos")
    parser.add_argument("--force-env", choices=["docker", "ubuntu", "linux", "windows", "macos"], 
                       help="Força detecção de ambiente específico")
    
    args = parser.parse_args()
    
    if args.env_only:
        setup_env_file()
        return
    
    show_banner()
    
    # Detectar ou forçar ambiente
    if args.force_env:
        environment = args.force_env
        info(f"Ambiente forçado: {environment}")
    else:
        environment = detect_environment()
    
    # Verificar pré-requisitos
    if not check_prerequisites(environment):
        error("Pré-requisitos não atendidos")
        sys.exit(1)
    
    if args.check:
        success("Sistema verificado com sucesso!")
        return
    
    # Executar deploy
    setup_env_file()
    
    if execute_deploy(environment):
        show_post_deploy_info(environment)
    else:
        error("Deploy falhou")
        sys.exit(1)

if __name__ == "__main__":
    main()
