"""
Serviço para gerenciar configurações de banco de dados
"""
import os
import json
from pathlib import Path
from django.conf import settings
from django.db import connections
from django.core.management import call_command
from django.utils import timezone
from apps.config.models import DatabaseConfiguration, UserActivityLog


class DatabaseService:
    """Serviço para gerenciar configurações de banco de dados"""
    
    @staticmethod
    def get_active_configuration():
        """Retorna a configuração ativa"""
        return DatabaseConfiguration.objects.filter(
            is_active=True
        ).first()
    
    @staticmethod
    def get_default_configuration():
        """Retorna a configuração padrão"""
        return DatabaseConfiguration.objects.filter(
            is_default=True
        ).first()
    
    @staticmethod
    def list_configurations():
        """Lista todas as configurações"""
        return DatabaseConfiguration.objects.all().order_by(
            '-is_default', '-is_active', 'name'
        )
    
    @staticmethod
    def create_configuration(name, engine, database_name, **kwargs):
        """Cria uma nova configuração de banco"""
        config = DatabaseConfiguration(
            name=name,
            engine=engine,
            name_db=database_name,
            **kwargs
        )
        config.save()
        return config
    
    @staticmethod
    def test_configuration(config_id):
        """Testa uma configuração específica"""
        try:
            config = DatabaseConfiguration.objects.get(id=config_id)
            success, message = config.test_connection()
            config.save()
            return success, message, config
        except DatabaseConfiguration.DoesNotExist:
            return False, "Configuração não encontrada", None
    
    @staticmethod
    def activate_configuration(config_id, user=None):
        """Ativa uma configuração específica"""
        try:
            config = DatabaseConfiguration.objects.get(id=config_id)
            
            # Testar conexão antes de ativar
            success, test_message = config.test_connection()
            if not success:
                return False, f"Erro na conexão: {test_message}", config
            
            # Ativar configuração
            success, message = config.activate_configuration()
            
            if success and user:
                # Registrar ativação no log
                UserActivityLog.objects.create(
                    user=user,
                    action='database_config_activated',
                    description=f'Configuração de banco "{config.name}" ativada',
                    metadata={
                        'config_id': config.id,
                        'config_name': config.name,
                        'engine': config.engine,
                    }
                )
            
            return success, message, config
            
        except DatabaseConfiguration.DoesNotExist:
            return False, "Configuração não encontrada", None
    
    @staticmethod
    def switch_database(config_id, user=None):
        """Troca o banco de dados ativo"""
        success, message, config = DatabaseService.activate_configuration(config_id, user)
        
        if success:
            # Fechar conexões existentes
            connections.close_all()
            
            # Recarregar configurações do Django
            DatabaseService._reload_django_settings()
            
            return True, f"Banco de dados trocado para '{config.name}' com sucesso", config
        
        return success, message, config
    
    @staticmethod
    def _reload_django_settings():
        """Recarrega as configurações do Django"""
        # Nota: Em produção, seria necessário reiniciar o servidor
        # Esta função é mais útil para desenvolvimento
        try:
            # Limpar cache de configurações
            if hasattr(settings, '_wrapped'):
                delattr(settings, '_wrapped')
            
            # Recarregar variáveis de ambiente
            from django.core.management.utils import get_random_secret_key
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
            
            return True
        except Exception as e:
            return False
    
    @staticmethod
    def backup_configurations():
        """Cria backup de todas as configurações"""
        try:
            # Criar diretório de backup
            backup_dir = Path('backups/database_configs')
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Nome do arquivo
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            backup_file = backup_dir / f'all_db_configs_{timestamp}.json'
            
            # Coletar dados
            configs = DatabaseConfiguration.objects.all()
            backup_data = {
                'timestamp': timezone.now().isoformat(),
                'total_configs': configs.count(),
                'configurations': []
            }
            
            for config in configs:
                config_data = {
                    'name': config.name,
                    'description': config.description,
                    'engine': config.engine,
                    'name_db': config.name_db,
                    'host': config.host,
                    'port': config.port,
                    'user': config.user,
                    'options': config.options,
                    'is_default': config.is_default,
                    'is_active': config.is_active,
                    'created_at': config.created_at.isoformat() if config.created_at else None,
                }
                backup_data['configurations'].append(config_data)
            
            # Salvar backup
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            return True, f"Backup salvo em {backup_file}", backup_file
            
        except Exception as e:
            return False, f"Erro ao criar backup: {str(e)}", None
    
    @staticmethod
    def restore_configurations(backup_file_path, user=None):
        """Restaura configurações de um backup"""
        try:
            backup_path = Path(backup_file_path)
            if not backup_path.exists():
                return False, "Arquivo de backup não encontrado", None
            
            # Ler backup
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            restored_count = 0
            errors = []
            
            for config_data in backup_data.get('configurations', []):
                try:
                    # Verificar se já existe
                    existing = DatabaseConfiguration.objects.filter(
                        name=config_data['name']
                    ).first()
                    
                    if existing:
                        # Atualizar existente
                        for key, value in config_data.items():
                            if key not in ['created_at']:
                                setattr(existing, key, value)
                        
                        if user:
                            existing.updated_by = user
                        
                        existing.save()
                        restored_count += 1
                    else:
                        # Criar novo
                        config = DatabaseConfiguration(**{
                            k: v for k, v in config_data.items() 
                            if k not in ['created_at']
                        })
                        
                        if user:
                            config.created_by = user
                            config.updated_by = user
                        
                        config.save()
                        restored_count += 1
                        
                except Exception as e:
                    errors.append(f"Erro ao restaurar '{config_data.get('name', 'unknown')}': {str(e)}")
            
            if user:
                UserActivityLog.objects.create(
                    user=user,
                    action='database_configs_restored',
                    description=f'Restauradas {restored_count} configurações de banco',
                    metadata={
                        'backup_file': str(backup_path),
                        'restored_count': restored_count,
                        'errors': errors,
                    }
                )
            
            if errors:
                return True, f"Restauradas {restored_count} configurações com {len(errors)} erros", errors
            else:
                return True, f"Restauradas {restored_count} configurações com sucesso", None
                
        except Exception as e:
            return False, f"Erro ao restaurar backup: {str(e)}", None
    
    @staticmethod
    def get_connection_info():
        """Retorna informações sobre a conexão atual"""
        try:
            from django.db import connection
            
            # Informações da conexão atual
            db_info = {
                'engine': connection.settings_dict.get('ENGINE', 'Unknown'),
                'name': connection.settings_dict.get('NAME', 'Unknown'),
                'host': connection.settings_dict.get('HOST', 'localhost'),
                'port': connection.settings_dict.get('PORT', 'Default'),
                'user': connection.settings_dict.get('USER', 'Unknown'),
            }
            
            # Configuração ativa no sistema
            active_config = DatabaseService.get_active_configuration()
            
            return {
                'current_connection': db_info,
                'active_config': active_config,
                'is_synced': active_config and active_config.engine == db_info['engine'] and active_config.name_db == db_info['name']
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'current_connection': None,
                'active_config': None,
                'is_synced': False
            }
    
    @staticmethod
    def migrate_database(config_id=None):
        """Executa migrações no banco especificado"""
        try:
            if config_id:
                config = DatabaseConfiguration.objects.get(id=config_id)
                # Ativar configuração temporariamente para migração
                original_active = DatabaseService.get_active_configuration()
                config.activate_configuration()
            
            # Executar migrações
            call_command('migrate', verbosity=1, interactive=False)
            
            if config_id and original_active:
                # Restaurar configuração original
                original_active.activate_configuration()
            
            return True, "Migrações executadas com sucesso"
            
        except Exception as e:
            return False, f"Erro ao executar migrações: {str(e)}"
