#!/usr/bin/env python
"""
Gerenciador inteligente de portas para deploy automatizado
Detecta conflitos e resolve automaticamente
"""
import socket
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Importar yaml com fallback
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

class PortManager:
    """Gerenciador inteligente de portas"""
    
    # Configuração padrão de portas
    DEFAULT_PORTS = {
        'web': 8000,
        'postgres': 5432,
        'postgres_external': 5433,
        'redis': 6379,
        'nginx_http': 80,
        'nginx_https': 443,
        'mysql': 3306,
        'mongodb': 27017,
        'elasticsearch': 9200
    }
    
    # Ranges de portas alternativas
    PORT_RANGES = {
        'web': range(8000, 8100),
        'postgres_external': range(5433, 5500),
        'redis': range(6379, 6400),
        'nginx_http': range(8080, 8200),
        'nginx_https': range(8443, 8500),
        'mysql': range(3306, 3400),
        'mongodb': range(27017, 27100),
        'elasticsearch': range(9200, 9300)
    }
    
    def __init__(self):
        self.conflicts = {}
        self.resolutions = {}
        
    def check_port(self, host: str, port: int) -> bool:
        """Verifica se uma porta está disponível"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            return result != 0  # True se disponível
        except:
            return True
    
    def find_alternative_port(self, service: str, preferred_port: int) -> int:
        """Encontra uma porta alternativa para um serviço"""
        # Primeiro tenta a porta preferida
        if self.check_port('localhost', preferred_port):
            return preferred_port
        
        # Busca no range específico do serviço
        if service in self.PORT_RANGES:
            for port in self.PORT_RANGES[service]:
                if self.check_port('localhost', port):
                    return port
        
        # Busca em range genérico (8000-9000)
        for port in range(8000, 9000):
            if self.check_port('localhost', port):
                return port
        
        # Se não encontrar, retorna a porta original + 1000
        return preferred_port + 1000
    
    def scan_port_conflicts(self) -> Dict[str, Dict]:
        """Escaneia conflitos de porta nos arquivos de configuração"""
        conflicts = {}
        
        # Verificar docker-compose.yml
        docker_conflicts = self._scan_docker_compose()
        if docker_conflicts:
            conflicts['docker-compose'] = docker_conflicts
        
        # Verificar .env files
        env_conflicts = self._scan_env_files()
        if env_conflicts:
            conflicts['env_files'] = env_conflicts
        
        return conflicts
    
    def _scan_docker_compose(self) -> Dict:
        """Escaneia conflitos no docker-compose.yml"""
        compose_file = Path('docker-compose.yml')
        if not compose_file.exists():
            return {}

        try:
            if YAML_AVAILABLE:
                with open(compose_file, 'r', encoding='utf-8') as f:
                    compose_data = yaml.safe_load(f)
            else:
                # Fallback: parse manual simples para portas
                return self._scan_docker_compose_manual()

            conflicts = {}
            services = compose_data.get('services', {})

            for service_name, service_config in services.items():
                ports = service_config.get('ports', [])
                for port_mapping in ports:
                    if isinstance(port_mapping, str):
                        external_port = int(port_mapping.split(':')[0])
                        if not self.check_port('localhost', external_port):
                            conflicts[f'{service_name}_port'] = {
                                'current': external_port,
                                'available': self.find_alternative_port(service_name, external_port),
                                'mapping': port_mapping
                            }

            return conflicts
        except Exception as e:
            print(f"Erro ao analisar docker-compose.yml: {e}")
            return {}

    def _scan_docker_compose_manual(self) -> Dict:
        """Parse manual do docker-compose.yml sem yaml"""
        conflicts = {}

        try:
            with open('docker-compose.yml', 'r', encoding='utf-8') as f:
                content = f.read()

            # Buscar padrões de porta simples
            import re
            port_patterns = [
                r'"(\d+):(\d+)"',  # "5433:5432"
                r"'(\d+):(\d+)'",  # '5433:5432'
                r'- (\d+):(\d+)',  # - 5433:5432
            ]

            for pattern in port_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    external_port = int(match[0])
                    if not self.check_port('localhost', external_port):
                        conflicts[f'port_{external_port}'] = {
                            'current': external_port,
                            'available': self.find_alternative_port('generic', external_port),
                            'mapping': f'{external_port}:{match[1]}'
                        }

            return conflicts
        except Exception as e:
            print(f"Erro no parse manual: {e}")
            return {}
    
    def _scan_env_files(self) -> Dict:
        """Escaneia conflitos nos arquivos .env"""
        env_files = ['.env', '.env.docker', '.env.local']
        conflicts = {}
        
        for env_file in env_files:
            if Path(env_file).exists():
                file_conflicts = self._scan_single_env_file(env_file)
                if file_conflicts:
                    conflicts[env_file] = file_conflicts
        
        return conflicts
    
    def _scan_single_env_file(self, env_file: str) -> Dict:
        """Escaneia um arquivo .env específico"""
        conflicts = {}
        
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if '=' in line and 'PORT' in line.upper():
                        key, value = line.split('=', 1)
                        try:
                            port = int(value)
                            if not self.check_port('localhost', port):
                                service = key.lower().replace('_port', '').replace('db_', 'postgres_')
                                conflicts[key] = {
                                    'current': port,
                                    'available': self.find_alternative_port(service, port),
                                    'line': line_num
                                }
                        except ValueError:
                            continue
        except Exception as e:
            print(f"Erro ao analisar {env_file}: {e}")
        
        return conflicts
    
    def resolve_conflicts_automatically(self) -> bool:
        """Resolve todos os conflitos automaticamente"""
        print("🔍 Detectando conflitos de porta...")
        
        conflicts = self.scan_port_conflicts()
        
        if not conflicts:
            print("✅ Nenhum conflito de porta detectado!")
            return True
        
        print(f"⚠️  Detectados conflitos em {len(conflicts)} arquivo(s)")
        
        # Resolver conflitos do docker-compose.yml
        if 'docker-compose' in conflicts:
            self._resolve_docker_compose_conflicts(conflicts['docker-compose'])
        
        # Resolver conflitos dos arquivos .env
        if 'env_files' in conflicts:
            self._resolve_env_conflicts(conflicts['env_files'])
        
        print("✅ Todos os conflitos de porta foram resolvidos automaticamente!")
        return True
    
    def _resolve_docker_compose_conflicts(self, conflicts: Dict):
        """Resolve conflitos no docker-compose.yml"""
        print("🐳 Resolvendo conflitos no docker-compose.yml...")
        
        compose_file = Path('docker-compose.yml')
        with open(compose_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for conflict_key, conflict_info in conflicts.items():
            old_mapping = conflict_info['mapping']
            old_port = conflict_info['current']
            new_port = conflict_info['available']
            
            # Criar novo mapeamento
            new_mapping = old_mapping.replace(f"{old_port}:", f"{new_port}:")
            
            # Substituir no conteúdo
            content = content.replace(f'"{old_mapping}"', f'"{new_mapping}"')
            content = content.replace(f"'{old_mapping}'", f"'{new_mapping}'")
            content = content.replace(f"- {old_mapping}", f"- {new_mapping}")
            
            print(f"   📝 {conflict_key}: {old_port} → {new_port}")
            self.resolutions[f"docker_{conflict_key}"] = {'old': old_port, 'new': new_port}
        
        # Salvar arquivo atualizado
        with open(compose_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _resolve_env_conflicts(self, env_conflicts: Dict):
        """Resolve conflitos nos arquivos .env"""
        print("📄 Resolvendo conflitos nos arquivos .env...")
        
        for env_file, conflicts in env_conflicts.items():
            print(f"   📝 Atualizando {env_file}...")
            
            with open(env_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for key, conflict_info in conflicts.items():
                old_port = conflict_info['current']
                new_port = conflict_info['available']
                
                # Atualizar linha específica
                for i, line in enumerate(lines):
                    if line.startswith(f"{key}="):
                        lines[i] = f"{key}={new_port}\n"
                        print(f"      {key}: {old_port} → {new_port}")
                        self.resolutions[f"{env_file}_{key}"] = {'old': old_port, 'new': new_port}
                        break
            
            # Salvar arquivo atualizado
            with open(env_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
    
    def show_resolution_summary(self):
        """Mostra resumo das resoluções aplicadas"""
        if not self.resolutions:
            return
        
        print("\n📋 Resumo das correções de porta aplicadas:")
        for key, resolution in self.resolutions.items():
            print(f"   • {key}: {resolution['old']} → {resolution['new']}")
        
        print("\n💡 Dicas importantes:")
        print("   • As portas foram alteradas automaticamente para evitar conflitos")
        print("   • Use as novas portas para acessar os serviços")
        print("   • Os arquivos de configuração foram atualizados")

def main():
    """Função principal para teste"""
    manager = PortManager()
    
    print("🚀 Gerenciador Inteligente de Portas - Havoc\n")
    
    success = manager.resolve_conflicts_automatically()
    
    if success:
        manager.show_resolution_summary()
        print("\n🎉 Resolução de conflitos concluída!")
    else:
        print("\n❌ Falha na resolução de conflitos")

if __name__ == '__main__':
    main()
