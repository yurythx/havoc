#!/usr/bin/env python
"""
Script para diagnosticar problemas de conexão com banco de dados
"""
import os
import sys
import socket
import subprocess
import time

def check_port_connectivity(host, port, timeout=5):
    """Verifica se uma porta está acessível"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"Erro ao verificar porta: {e}")
        return False

def check_docker_services():
    """Verifica status dos serviços Docker"""
    print("🐳 Verificando serviços Docker...")
    
    try:
        result = subprocess.run(['docker-compose', 'ps'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker Compose funcionando")
            print(result.stdout)
            return True
        else:
            print(f"❌ Erro no Docker Compose: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Docker Compose não encontrado")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def check_database_container():
    """Verifica se o container do banco está rodando"""
    print("\n🔍 Verificando container do banco...")
    
    try:
        # Verificar se container existe e está rodando
        result = subprocess.run(['docker', 'ps', '--filter', 'name=db', '--format', 'table {{.Names}}\t{{.Status}}'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:  # Tem header + pelo menos um container
                print("✅ Container do banco encontrado:")
                print(result.stdout)
                return True
            else:
                print("❌ Container do banco não encontrado")
                return False
        else:
            print(f"❌ Erro ao verificar containers: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def check_database_logs():
    """Verifica logs do banco de dados"""
    print("\n📋 Logs do banco de dados (últimas 20 linhas):")
    
    try:
        result = subprocess.run(['docker-compose', 'logs', '--tail=20', 'db'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"❌ Erro ao obter logs: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def check_web_logs():
    """Verifica logs da aplicação web"""
    print("\n📋 Logs da aplicação web (últimas 20 linhas):")
    
    try:
        result = subprocess.run(['docker-compose', 'logs', '--tail=20', 'web'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"❌ Erro ao obter logs: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_database_connection():
    """Testa conexão com banco de dados"""
    print("\n🔗 Testando conexão com banco...")
    
    # Verificar conectividade de rede
    if check_port_connectivity('localhost', 5433):
        print("✅ Porta 5433 (PostgreSQL Docker) acessível")
    else:
        print("❌ Porta 5433 não acessível")
        return False
    
    # Tentar conectar via psql no container
    try:
        print("🔍 Testando conexão via container...")
        result = subprocess.run([
            'docker-compose', 'exec', '-T', 'db', 
            'psql', '-U', 'postgres', '-d', 'havoc_prod', '-c', 'SELECT 1;'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Conexão com banco OK!")
            return True
        else:
            print(f"❌ Falha na conexão: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("⏰ Timeout na conexão com banco")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def show_environment_vars():
    """Mostra variáveis de ambiente relevantes"""
    print("\n⚙️  Variáveis de ambiente do Docker:")
    
    try:
        result = subprocess.run(['docker-compose', 'config'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            # Filtrar apenas linhas com DATABASE ou DB
            lines = result.stdout.split('\n')
            relevant_lines = [line for line in lines if 'DATABASE' in line or 'DB_' in line or 'POSTGRES' in line]
            
            if relevant_lines:
                print("📋 Configurações de banco:")
                for line in relevant_lines:
                    print(f"   {line.strip()}")
            else:
                print("❌ Nenhuma configuração de banco encontrada")
        else:
            print(f"❌ Erro ao obter configuração: {result.stderr}")
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Função principal"""
    print("🔧 DIAGNÓSTICO DE BANCO DE DADOS - HAVOC")
    print("=" * 50)
    
    # Verificações em sequência
    checks = [
        ("Serviços Docker", check_docker_services),
        ("Container do Banco", check_database_container),
        ("Logs do Banco", check_database_logs),
        ("Logs da Web", check_web_logs),
        ("Conexão com Banco", test_database_connection),
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        print(f"\n{'='*20} {check_name} {'='*20}")
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ Erro inesperado em {check_name}: {e}")
            results[check_name] = False
    
    # Mostrar variáveis de ambiente
    show_environment_vars()
    
    # Resumo final
    print(f"\n{'='*50}")
    print("📊 RESUMO DO DIAGNÓSTICO:")
    
    for check_name, success in results.items():
        status = "✅ OK" if success else "❌ FALHA"
        print(f"   {check_name}: {status}")
    
    # Sugestões baseadas nos resultados
    print(f"\n💡 SUGESTÕES:")
    
    if not results.get("Serviços Docker", False):
        print("   • Inicie o Docker: docker-compose up -d")
    
    if not results.get("Container do Banco", False):
        print("   • Reconstrua os containers: docker-compose build")
        print("   • Verifique o docker-compose.yml")
    
    if not results.get("Conexão com Banco", False):
        print("   • Verifique credenciais no .env.docker")
        print("   • Aguarde o banco inicializar completamente")
        print("   • Verifique logs do banco para erros")
    
    # Status geral
    all_ok = all(results.values())
    if all_ok:
        print(f"\n🎉 DIAGNÓSTICO: TUDO OK!")
    else:
        print(f"\n⚠️  DIAGNÓSTICO: PROBLEMAS ENCONTRADOS")
        print("   Execute as sugestões acima e rode o diagnóstico novamente")

if __name__ == '__main__':
    main()
