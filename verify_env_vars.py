#!/usr/bin/env python
"""
Script para verificar se todas as variáveis de ambiente necessárias estão configuradas
"""
import os
import subprocess
from pathlib import Path

def check_env_file_vars(file_path):
    """Verifica variáveis em arquivo .env"""
    if not Path(file_path).exists():
        print(f"❌ {file_path} não encontrado")
        return {}
    
    print(f"\n📄 Verificando {file_path}:")
    
    vars_found = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                vars_found[key] = value
                
                # Verificar variáveis críticas
                if key in ['DJANGO_SECRET_KEY', 'SECRET_KEY']:
                    if 'django-insecure' in value:
                        print(f"   ⚠️  {key}: Usando chave insegura (linha {line_num})")
                    else:
                        print(f"   ✅ {key}: Configurado com chave segura")
                elif key in ['DB_PASSWORD', 'DATABASE_PASSWORD']:
                    if len(value) < 8:
                        print(f"   ⚠️  {key}: Senha muito simples (linha {line_num})")
                    else:
                        print(f"   ✅ {key}: Configurado")
                elif key in ['DEBUG']:
                    print(f"   📋 {key}: {value}")
                elif key in ['ENVIRONMENT']:
                    print(f"   📋 {key}: {value}")
    
    return vars_found

def check_docker_compose_env():
    """Verifica variáveis no docker-compose.yml"""
    if not Path('docker-compose.yml').exists():
        print("❌ docker-compose.yml não encontrado")
        return []
    
    print(f"\n🐳 Verificando variáveis no docker-compose.yml:")
    
    try:
        result = subprocess.run(['docker-compose', 'config'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Erro ao ler docker-compose: {result.stderr}")
            return []
        
        # Procurar por variáveis de ambiente no output
        env_vars = []
        lines = result.stdout.split('\n')
        in_env_section = False
        
        for line in lines:
            if 'environment:' in line:
                in_env_section = True
                continue
            elif in_env_section:
                if line.strip().startswith('- '):
                    var_line = line.strip()[2:]  # Remove '- '
                    env_vars.append(var_line)
                    
                    # Verificar variáveis críticas
                    if 'DJANGO_SECRET_KEY' in var_line:
                        print(f"   ✅ DJANGO_SECRET_KEY: Configurado")
                    elif 'SECRET_KEY' in var_line:
                        print(f"   ✅ SECRET_KEY: Configurado")
                    elif 'DATABASE_' in var_line or 'DB_' in var_line:
                        print(f"   📋 {var_line}")
                elif not line.strip().startswith('-') and line.strip():
                    in_env_section = False
        
        return env_vars
        
    except FileNotFoundError:
        print("❌ Docker Compose não encontrado")
        return []
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

def check_critical_vars():
    """Verifica se variáveis críticas estão definidas"""
    print(f"\n🔍 Verificando variáveis críticas:")
    
    critical_vars = [
        'DJANGO_SECRET_KEY',
        'SECRET_KEY',
        'DATABASE_ENGINE',
        'DB_NAME',
        'DB_USER',
        'DB_PASSWORD',
        'ALLOWED_HOSTS',
    ]
    
    # Verificar em .env.docker (usado pelo container)
    env_docker_vars = {}
    if Path('.env.docker').exists():
        with open('.env.docker', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_docker_vars[key] = value
    
    missing_vars = []
    for var in critical_vars:
        if var in env_docker_vars:
            print(f"   ✅ {var}: Definido")
        else:
            print(f"   ❌ {var}: NÃO DEFINIDO")
            missing_vars.append(var)
    
    return missing_vars

def show_recommendations():
    """Mostra recomendações de segurança"""
    print(f"\n💡 RECOMENDAÇÕES DE SEGURANÇA:")
    print(f"   🔐 SECRET_KEY:")
    print(f"      • Use chaves geradas com get_random_secret_key()")
    print(f"      • Nunca use chaves que contenham 'django-insecure'")
    print(f"      • Mantenha a chave secreta e única por ambiente")
    print(f"   ")
    print(f"   🔒 Senhas:")
    print(f"      • Use senhas com pelo menos 12 caracteres")
    print(f"      • Inclua letras, números e símbolos")
    print(f"      • Nunca use senhas padrão em produção")
    print(f"   ")
    print(f"   🌐 Hosts:")
    print(f"      • Configure ALLOWED_HOSTS com domínios específicos")
    print(f"      • Use CSRF_TRUSTED_ORIGINS para origens confiáveis")
    print(f"      • Evite usar '*' em produção")

def main():
    """Função principal"""
    print("🔍 VERIFICAÇÃO DE VARIÁVEIS DE AMBIENTE - HAVOC")
    print("=" * 55)
    
    # Verificar arquivos .env
    env_vars = check_env_file_vars('.env')
    env_docker_vars = check_env_file_vars('.env.docker')
    
    # Verificar docker-compose
    compose_vars = check_docker_compose_env()
    
    # Verificar variáveis críticas
    missing_vars = check_critical_vars()
    
    # Mostrar recomendações
    show_recommendations()
    
    # Resumo final
    print(f"\n📊 RESUMO:")
    print(f"   📄 Variáveis em .env: {len(env_vars)}")
    print(f"   📄 Variáveis em .env.docker: {len(env_docker_vars)}")
    print(f"   🐳 Variáveis no docker-compose: {len(compose_vars)}")
    print(f"   ❌ Variáveis críticas faltando: {len(missing_vars)}")
    
    if missing_vars:
        print(f"\n⚠️  AÇÃO NECESSÁRIA:")
        print(f"   Adicione as seguintes variáveis ao .env.docker:")
        for var in missing_vars:
            print(f"   • {var}=<valor>")
    else:
        print(f"\n✅ Todas as variáveis críticas estão configuradas!")
    
    print(f"\n🚀 Para testar o deploy:")
    print(f"   python deploy-auto.py")

if __name__ == '__main__':
    main()
