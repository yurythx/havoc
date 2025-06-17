#!/usr/bin/env python
"""
Script simples para verificar se as correções foram aplicadas
"""
import re
from pathlib import Path

def check_settings_fixes():
    """Verifica correções no settings.py"""
    print("🔍 Verificando correções no settings.py...")
    
    settings_file = Path('core/settings.py')
    if not settings_file.exists():
        print("❌ settings.py não encontrado")
        return False
    
    with open(settings_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar isolation level
    if 'default_transaction_isolation' not in content:
        print("   ✅ Isolation level removido (PostgreSQL usará padrão 'read committed')")
    else:
        # Verificar se ainda há configuração problemática
        problematic_patterns = [
            'default_transaction_isolation="read"',
            'default_transaction_isolation=read_committed',
        ]

        has_problem = any(pattern in content for pattern in problematic_patterns)
        if has_problem:
            print("   ❌ Isolation level ainda tem problemas")
            return False
        else:
            print("   ✅ Isolation level configurado corretamente")
    
    # Verificar STATICFILES_DIRS
    if 'static_dir.exists()' in content:
        print("   ✅ STATICFILES_DIRS configurado condicionalmente")
    else:
        print("   ❌ STATICFILES_DIRS não configurado condicionalmente")
        return False
    
    return True

def check_dockerfile_fixes():
    """Verifica correções no Dockerfile"""
    print("\n🐳 Verificando correções no Dockerfile...")
    
    dockerfile = Path('Dockerfile')
    if not dockerfile.exists():
        print("❌ Dockerfile não encontrado")
        return False
    
    with open(dockerfile, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se diretório static é criado
    if '/app/static' in content:
        print("   ✅ Diretório /app/static será criado no container")
    else:
        print("   ❌ Diretório /app/static não será criado")
        return False
    
    return True

def check_env_files():
    """Verifica arquivos .env"""
    print("\n📄 Verificando arquivos .env...")
    
    # Verificar .env.docker
    env_docker = Path('.env.docker')
    if env_docker.exists():
        with open(env_docker, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'DJANGO_SECRET_KEY=' in content:
            print("   ✅ DJANGO_SECRET_KEY definido em .env.docker")
        else:
            print("   ❌ DJANGO_SECRET_KEY não definido em .env.docker")
            return False
    else:
        print("   ❌ .env.docker não encontrado")
        return False
    
    return True

def check_docker_compose():
    """Verifica docker-compose.yml"""
    print("\n🐳 Verificando docker-compose.yml...")
    
    compose_file = Path('docker-compose.yml')
    if not compose_file.exists():
        print("❌ docker-compose.yml não encontrado")
        return False
    
    with open(compose_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar env_file
    if 'env_file:' in content:
        print("   ✅ env_file configurado")
    else:
        print("   ❌ env_file não configurado")
        return False
    
    # Verificar DJANGO_SECRET_KEY
    if 'DJANGO_SECRET_KEY=' in content:
        print("   ✅ DJANGO_SECRET_KEY nas variáveis de ambiente")
    else:
        print("   ❌ DJANGO_SECRET_KEY não nas variáveis de ambiente")
        return False
    
    return True

def main():
    """Função principal"""
    print("🔧 VERIFICAÇÃO DAS CORREÇÕES APLICADAS")
    print("=" * 45)
    
    checks = [
        ("Settings.py", check_settings_fixes),
        ("Dockerfile", check_dockerfile_fixes),
        ("Arquivos .env", check_env_files),
        ("Docker Compose", check_docker_compose),
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ Erro em {check_name}: {e}")
            results[check_name] = False
    
    # Resumo
    print("\n" + "=" * 45)
    print("📊 RESUMO DAS VERIFICAÇÕES:")
    
    all_passed = True
    for check_name, passed in results.items():
        status = "✅ OK" if passed else "❌ FALHA"
        print(f"   {check_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n🎯 CORREÇÕES APLICADAS:")
    print("   • Isolation level: read_committed → 'read committed'")
    print("   • STATICFILES_DIRS: configuração condicional")
    print("   • DJANGO_SECRET_KEY: adicionado aos arquivos")
    print("   • Dockerfile: diretório /app/static criado")
    print("   • Docker Compose: env_file e variáveis corretas")
    
    if all_passed:
        print("\n🎉 TODAS AS CORREÇÕES FORAM APLICADAS!")
        print("\n🚀 Pronto para deploy:")
        print("   1. Inicie o Docker Desktop")
        print("   2. Execute: python deploy-auto.py")
        print("   3. Ou: docker-compose up -d")
    else:
        print("\n⚠️  ALGUMAS CORREÇÕES FALHARAM")
        print("   Verifique os problemas acima")

if __name__ == '__main__':
    main()
