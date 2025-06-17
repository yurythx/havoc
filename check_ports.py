#!/usr/bin/env python
"""
Script para verificar portas disponíveis antes do deploy
"""
import socket
import subprocess
import sys

def check_port(host, port):
    """Verifica se uma porta está disponível"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result != 0  # True se disponível (conexão falhou)
    except:
        return True  # Assume disponível se houver erro

def check_docker_ports():
    """Verifica portas necessárias para Docker"""
    ports_to_check = [
        (8000, "Django Web Server"),
        (5432, "PostgreSQL (sistema)"),
        (5433, "PostgreSQL (Docker)"),
        (6379, "Redis"),
        (80, "Nginx HTTP"),
        (443, "Nginx HTTPS")
    ]
    
    print("🔍 Verificando disponibilidade de portas...\n")
    
    available_ports = []
    occupied_ports = []
    
    for port, description in ports_to_check:
        is_available = check_port('localhost', port)
        status = "✅ Disponível" if is_available else "❌ Em uso"
        print(f"   Porta {port:4d} ({description:20s}): {status}")
        
        if is_available:
            available_ports.append(port)
        else:
            occupied_ports.append((port, description))
    
    print(f"\n📊 Resumo:")
    print(f"   ✅ Portas disponíveis: {len(available_ports)}")
    print(f"   ❌ Portas ocupadas: {len(occupied_ports)}")
    
    if occupied_ports:
        print(f"\n⚠️  Portas ocupadas que podem causar conflito:")
        for port, desc in occupied_ports:
            print(f"   • {port} - {desc}")
            
        if 5432 in [p for p, _ in occupied_ports]:
            print(f"\n💡 Solução para PostgreSQL:")
            print(f"   • Docker configurado para usar porta 5433 (externa)")
            print(f"   • Porta interna do container continua 5432")
            print(f"   • Sem conflito com PostgreSQL local na 5432")
    
    return len(occupied_ports) == 0 or 5432 not in [p for p, _ in occupied_ports if p != 5432]

def show_docker_config():
    """Mostra configuração atual do Docker"""
    print(f"\n🐳 Configuração Docker atual:")
    print(f"   • Web: localhost:8000 → container:8000")
    print(f"   • PostgreSQL: localhost:5433 → container:5432")
    print(f"   • Redis: localhost:6379 → container:6379 (opcional)")
    print(f"   • Nginx: localhost:80/443 → container:80/443 (opcional)")

def check_docker_status():
    """Verifica se Docker está rodando"""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker instalado: {result.stdout.strip()}")
            
            # Verificar se está rodando
            result = subprocess.run(['docker', 'ps'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Docker está rodando")
                return True
            else:
                print(f"❌ Docker não está rodando")
                return False
        else:
            print(f"❌ Docker não encontrado")
            return False
    except FileNotFoundError:
        print(f"❌ Docker não instalado")
        return False

if __name__ == '__main__':
    print("🚀 Verificação de Portas para Deploy - Havoc\n")
    
    # Verificar Docker
    docker_ok = check_docker_status()
    print()
    
    # Verificar portas
    ports_ok = check_docker_ports()
    
    # Mostrar configuração
    show_docker_config()
    
    print(f"\n🎯 Status geral:")
    if docker_ok and ports_ok:
        print(f"   ✅ Sistema pronto para deploy Docker!")
        print(f"\n💻 Comandos para deploy:")
        print(f"   python deploy-auto.py")
        print(f"   # ou")
        print(f"   docker-compose up -d")
    else:
        print(f"   ⚠️  Verificar problemas acima antes do deploy")
        if not docker_ok:
            print(f"   • Iniciar Docker Desktop")
        if not ports_ok:
            print(f"   • Resolver conflitos de porta")
