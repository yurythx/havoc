#!/usr/bin/env python
"""
Script para verificar configurações de banco de dados
Garante que portas internas/externas estão corretas
"""
import os
import re
from pathlib import Path

def check_env_file(file_path, context=""):
    """Verifica configurações em arquivo .env"""
    if not Path(file_path).exists():
        print(f"❌ {file_path} não encontrado")
        return False
    
    print(f"\n📄 Verificando {file_path} {context}:")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar variáveis de banco
    db_vars = {}
    for line in content.split('\n'):
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            key, value = line.split('=', 1)
            if any(keyword in key.upper() for keyword in ['DB_', 'DATABASE_', 'POSTGRES_']):
                db_vars[key] = value
    
    # Verificar DATABASE_URL
    database_url_pattern = r'DATABASE_URL=postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
    database_url_match = re.search(database_url_pattern, content)
    
    if database_url_match:
        user, password, host, port, db_name = database_url_match.groups()
        print(f"   📋 DATABASE_URL encontrada:")
        print(f"      Host: {host}")
        print(f"      Porta: {port}")
        print(f"      Banco: {db_name}")
        print(f"      Usuário: {user}")
        
        # Verificar se porta está correta
        if context == "(Docker interno)" and port != "5432":
            print(f"      ⚠️  ATENÇÃO: Porta {port} deveria ser 5432 para Docker interno")
        elif context == "(Host externo)" and port != "5433":
            print(f"      ⚠️  ATENÇÃO: Porta {port} deveria ser 5433 para acesso externo")
    
    # Verificar variáveis individuais
    if db_vars:
        print(f"   📋 Variáveis de banco:")
        for key, value in db_vars.items():
            print(f"      {key}: {value}")
            
            # Verificar porta específica
            if key == 'DB_PORT' or key == 'DATABASE_PORT':
                if context == "(Docker interno)" and value != "5432":
                    print(f"      ⚠️  ATENÇÃO: {key}={value} deveria ser 5432 para Docker interno")
                elif context == "(Host externo)" and value != "5433":
                    print(f"      ⚠️  ATENÇÃO: {key}={value} deveria ser 5433 para acesso externo")
    
    return True

def check_docker_compose():
    """Verifica docker-compose.yml"""
    compose_file = Path('docker-compose.yml')
    if not compose_file.exists():
        print("❌ docker-compose.yml não encontrado")
        return False
    
    print(f"\n🐳 Verificando docker-compose.yml:")
    
    with open(compose_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar mapeamento de portas
    port_mapping_pattern = r'"(\d+):(\d+)"'
    port_mappings = re.findall(port_mapping_pattern, content)
    
    for external, internal in port_mappings:
        print(f"   📋 Mapeamento de porta: {external}:{internal}")
        if external == "5433" and internal == "5432":
            print(f"      ✅ PostgreSQL: Correto (host:5433 → container:5432)")
        elif external == "8000" and internal == "8000":
            print(f"      ✅ Django: Correto (host:8000 → container:8000)")
        else:
            print(f"      ℹ️  Outro serviço: {external} → {internal}")
    
    # Verificar variáveis de ambiente do serviço web
    web_section_pattern = r'web:.*?environment:(.*?)(?=volumes:|ports:|depends_on:|$)'
    web_match = re.search(web_section_pattern, content, re.DOTALL)
    
    if web_match:
        env_section = web_match.group(1)
        print(f"   📋 Variáveis de ambiente do serviço web:")
        
        # Extrair variáveis DATABASE_* e DB_*
        env_lines = [line.strip() for line in env_section.split('\n') if line.strip().startswith('- ')]
        for line in env_lines:
            if any(keyword in line.upper() for keyword in ['DATABASE_', 'DB_']):
                var_part = line.replace('- ', '')
                print(f"      {var_part}")
                
                # Verificar se usa porta 5432 (interna)
                if 'PORT' in var_part and '5433' in var_part:
                    print(f"      ⚠️  ATENÇÃO: Porta 5433 no container - deveria ser 5432")
    
    return True

def show_port_summary():
    """Mostra resumo das portas corretas"""
    print(f"\n📋 RESUMO DAS PORTAS CORRETAS:")
    print(f"   🐳 Docker Compose:")
    print(f"      • PostgreSQL: \"5433:5432\" (host:5433 → container:5432)")
    print(f"      • Django: \"8000:8000\" (host:8000 → container:8000)")
    print(f"   ")
    print(f"   🔧 Variáveis de ambiente:")
    print(f"      • Container (docker-compose): DATABASE_PORT=5432")
    print(f"      • Host (.env local): DB_PORT=5433")
    print(f"   ")
    print(f"   🌐 URLs de acesso:")
    print(f"      • Aplicação: http://localhost:8000")
    print(f"      • PostgreSQL (externo): localhost:5433")
    print(f"      • PostgreSQL (interno): db:5432")

def main():
    """Função principal"""
    print("🔍 VERIFICAÇÃO DE CONFIGURAÇÃO DE BANCO DE DADOS")
    print("=" * 55)
    
    # Verificar arquivos .env
    files_to_check = [
        ('.env', "(Host externo)"),
        ('.env.docker', "(Docker interno)"),
        ('.env.local', "(Desenvolvimento)"),
    ]
    
    for file_path, context in files_to_check:
        check_env_file(file_path, context)
    
    # Verificar docker-compose.yml
    check_docker_compose()
    
    # Mostrar resumo
    show_port_summary()
    
    print(f"\n✅ Verificação concluída!")
    print(f"\n💡 Lembre-se:")
    print(f"   • Dentro do Docker: sempre use porta 5432")
    print(f"   • Do host para Docker: use porta 5433")
    print(f"   • DATABASE_URL no container: @db:5432")
    print(f"   • DATABASE_URL no host: @localhost:5433")

if __name__ == '__main__':
    main()
