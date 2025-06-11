from typing import List, Dict, Optional
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.conf import settings
from apps.config.models.app_module_config import AppModuleConfiguration
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class ModuleService:
    """Serviço para gerenciamento de módulos do sistema"""
    
    def __init__(self):
        self.core_apps = AppModuleConfiguration.CORE_APPS
    
    def get_all_modules(self) -> List[AppModuleConfiguration]:
        """Retorna todos os módulos"""
        return AppModuleConfiguration.objects.all().order_by('menu_order', 'display_name')

    def get_enabled_modules(self) -> List[AppModuleConfiguration]:
        """Retorna todos os módulos habilitados"""
        return AppModuleConfiguration.get_enabled_modules()
    
    def get_available_modules(self) -> List[AppModuleConfiguration]:
        """Retorna módulos disponíveis para uso"""
        return AppModuleConfiguration.objects.filter(
            is_enabled=True,
            status='active'
        ).order_by('menu_order', 'display_name')
    
    def get_menu_modules(self) -> List[AppModuleConfiguration]:
        """Retorna módulos que devem aparecer no menu"""
        return self.get_available_modules().filter(show_in_menu=True)
    
    def get_module_by_name(self, app_name: str) -> Optional[AppModuleConfiguration]:
        """Busca módulo por nome"""
        try:
            return AppModuleConfiguration.objects.get(app_name=app_name)
        except AppModuleConfiguration.DoesNotExist:
            return None
    
    def is_module_enabled(self, app_name: str) -> bool:
        """Verifica se um módulo está habilitado"""
        module = self.get_module_by_name(app_name)
        return module.is_available if module else False
    
    def is_core_module(self, app_name: str) -> bool:
        """Verifica se é um módulo principal"""
        return app_name in self.core_apps
    
    @transaction.atomic
    def enable_module(self, app_name: str, user=None) -> bool:
        """Habilita um módulo"""
        try:
            module = self.get_module_by_name(app_name)
            if not module:
                logger.error(f"Módulo {app_name} não encontrado")
                return False
            
            # Verifica dependências
            if not module.check_dependencies():
                logger.error(f"Dependências do módulo {app_name} não atendidas")
                return False
            
            module.is_enabled = True
            module.status = 'active'
            module.updated_by = user
            module.save()
            
            logger.info(f"Módulo {app_name} habilitado por {user.email if user else 'sistema'}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao habilitar módulo {app_name}: {str(e)}")
            return False
    
    @transaction.atomic
    def disable_module(self, app_name: str, user=None) -> bool:
        """Desabilita um módulo (se não for principal)"""
        try:
            module = self.get_module_by_name(app_name)
            if not module:
                logger.error(f"Módulo {app_name} não encontrado")
                return False
            
            # Não permite desabilitar módulos principais
            if module.is_core:
                logger.error(f"Tentativa de desabilitar módulo principal: {app_name}")
                return False
            
            # Verifica se outros módulos dependem deste
            dependent_modules = module.get_dependent_modules()
            if dependent_modules.exists():
                dependent_names = [m.display_name for m in dependent_modules]
                logger.error(f"Módulo {app_name} não pode ser desabilitado. Dependências: {dependent_names}")
                return False
            
            module.is_enabled = False
            module.status = 'inactive'
            module.updated_by = user
            module.save()
            
            logger.info(f"Módulo {app_name} desabilitado por {user.email if user else 'sistema'}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao desabilitar módulo {app_name}: {str(e)}")
            return False
    
    @transaction.atomic
    def create_module(self, module_data: Dict, user: User = None) -> Optional[AppModuleConfiguration]:
        """Cria um novo módulo"""
        try:
            # Verifica se já existe
            if self.get_module_by_name(module_data.get('app_name')):
                logger.error(f"Módulo {module_data.get('app_name')} já existe")
                return None
            
            module = AppModuleConfiguration(
                created_by=user,
                updated_by=user,
                **module_data
            )
            module.full_clean()
            module.save()
            
            logger.info(f"Módulo {module.app_name} criado por {user.email if user else 'sistema'}")
            return module
            
        except ValidationError as e:
            logger.error(f"Erro de validação ao criar módulo: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Erro ao criar módulo: {str(e)}")
            return None
    
    @transaction.atomic
    def update_module(self, app_name: str, module_data: Dict, user: User = None) -> bool:
        """Atualiza um módulo existente"""
        try:
            module = self.get_module_by_name(app_name)
            if not module:
                logger.error(f"Módulo {app_name} não encontrado")
                return False
            
            # Atualiza campos permitidos
            allowed_fields = [
                'display_name', 'description', 'url_pattern', 'menu_icon',
                'menu_order', 'show_in_menu', 'dependencies', 'required_permissions',
                'module_settings', 'version', 'author', 'documentation_url'
            ]
            
            for field, value in module_data.items():
                if field in allowed_fields:
                    setattr(module, field, value)
            
            module.updated_by = user
            module.full_clean()
            module.save()
            
            logger.info(f"Módulo {app_name} atualizado por {user.email if user else 'sistema'}")
            return True
            
        except ValidationError as e:
            logger.error(f"Erro de validação ao atualizar módulo {app_name}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Erro ao atualizar módulo {app_name}: {str(e)}")
            return False
    
    def get_module_statistics(self) -> Dict:
        """Retorna estatísticas dos módulos"""
        total = AppModuleConfiguration.objects.count()
        enabled = AppModuleConfiguration.objects.filter(is_enabled=True).count()
        core = AppModuleConfiguration.objects.filter(is_core=True).count()
        
        return {
            'total': total,
            'enabled': enabled,
            'disabled': total - enabled,
            'core': core,
            'custom': total - core,
        }
    
    def validate_module_dependencies(self, app_name: str) -> Dict:
        """Valida as dependências de um módulo"""
        module = self.get_module_by_name(app_name)
        if not module:
            return {'valid': False, 'error': 'Módulo não encontrado'}
        
        if not module.dependencies:
            return {'valid': True, 'dependencies': []}
        
        missing_deps = []
        inactive_deps = []
        
        for dep_name in module.dependencies:
            dep_module = self.get_module_by_name(dep_name)
            if not dep_module:
                missing_deps.append(dep_name)
            elif not dep_module.is_available:
                inactive_deps.append(dep_name)
        
        valid = len(missing_deps) == 0 and len(inactive_deps) == 0
        
        return {
            'valid': valid,
            'dependencies': module.dependencies,
            'missing': missing_deps,
            'inactive': inactive_deps,
        }
    
    def get_installed_apps_list(self) -> List[str]:
        """Retorna lista de apps instalados no Django"""
        return [app.split('.')[-1] for app in settings.INSTALLED_APPS if app.startswith('apps.')]
    
    def sync_with_installed_apps(self, user: User = None) -> Dict:
        """Sincroniza módulos com apps instalados"""
        installed_apps = self.get_installed_apps_list()
        existing_modules = {m.app_name for m in AppModuleConfiguration.objects.all()}
        
        created = []
        missing = []
        
        # Cria módulos para apps instalados que não existem
        for app_name in installed_apps:
            if app_name not in existing_modules:
                module_data = {
                    'app_name': app_name,
                    'display_name': app_name.title(),
                    'description': f'Módulo {app_name}',
                    'url_pattern': f'{app_name}/',
                    'menu_icon': 'fas fa-puzzle-piece',
                    'is_enabled': app_name in self.core_apps,
                    'module_type': 'core' if app_name in self.core_apps else 'feature',
                }
                
                module = self.create_module(module_data, user)
                if module:
                    created.append(app_name)
        
        # Identifica módulos que não têm app correspondente
        for module_name in existing_modules:
            if module_name not in installed_apps and module_name not in self.core_apps:
                missing.append(module_name)
        
        return {
            'created': created,
            'missing': missing,
            'total_installed': len(installed_apps),
            'total_modules': AppModuleConfiguration.objects.count(),
        }
    
    def initialize_system(self, user: User = None):
        """Inicializa o sistema de módulos"""
        try:
            # Inicializa módulos principais
            AppModuleConfiguration.initialize_core_modules()
            
            # Sincroniza com apps instalados
            sync_result = self.sync_with_installed_apps(user)
            
            logger.info(f"Sistema de módulos inicializado. Criados: {sync_result['created']}")
            return sync_result
            
        except Exception as e:
            logger.error(f"Erro ao inicializar sistema de módulos: {str(e)}")
            return None
