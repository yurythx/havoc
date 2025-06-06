from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db.models import QuerySet

User = get_user_model()

class IUserManagementService(ABC):
    """Interface para serviços de gerenciamento de usuários"""
    
    @abstractmethod
    def create_user(self, user_data: Dict[str, Any], created_by: User) -> User:
        """
        Cria um novo usuário
        :param user_data: Dados do usuário
        :param created_by: Usuário que está criando
        :return: Usuário criado
        """
        pass
    
    @abstractmethod
    def update_user(self, user_id: int, user_data: Dict[str, Any], updated_by: User) -> User:
        """
        Atualiza um usuário existente
        :param user_id: ID do usuário
        :param user_data: Dados para atualização
        :param updated_by: Usuário que está atualizando
        :return: Usuário atualizado
        """
        pass
    
    @abstractmethod
    def delete_user(self, user_id: int, deleted_by: User) -> bool:
        """
        Deleta um usuário
        :param user_id: ID do usuário
        :param deleted_by: Usuário que está deletando
        :return: True se deletado com sucesso
        """
        pass
    
    @abstractmethod
    def get_user_by_id(self, user_id: int) -> User:
        """
        Obtém um usuário pelo ID
        :param user_id: ID do usuário
        :return: Usuário encontrado
        """
        pass
    
    @abstractmethod
    def list_users(self, filters: Dict[str, Any] = None) -> QuerySet:
        """
        Lista usuários com filtros opcionais
        :param filters: Filtros para aplicar
        :return: QuerySet de usuários
        """
        pass
    
    @abstractmethod
    def search_users(self, query: str) -> QuerySet:
        """
        Busca usuários por termo
        :param query: Termo de busca
        :return: QuerySet de usuários encontrados
        """
        pass

class IPermissionManagementService(ABC):
    """Interface para serviços de gerenciamento de permissões"""
    
    @abstractmethod
    def assign_permission_to_user(self, user_id: int, permission_id: int, assigned_by: User) -> bool:
        """
        Atribui uma permissão a um usuário
        :param user_id: ID do usuário
        :param permission_id: ID da permissão
        :param assigned_by: Usuário que está atribuindo
        :return: True se atribuído com sucesso
        """
        pass
    
    @abstractmethod
    def remove_permission_from_user(self, user_id: int, permission_id: int, removed_by: User) -> bool:
        """
        Remove uma permissão de um usuário
        :param user_id: ID do usuário
        :param permission_id: ID da permissão
        :param removed_by: Usuário que está removendo
        :return: True se removido com sucesso
        """
        pass
    
    @abstractmethod
    def assign_group_to_user(self, user_id: int, group_id: int, assigned_by: User) -> bool:
        """
        Atribui um grupo a um usuário
        :param user_id: ID do usuário
        :param group_id: ID do grupo
        :param assigned_by: Usuário que está atribuindo
        :return: True se atribuído com sucesso
        """
        pass
    
    @abstractmethod
    def remove_group_from_user(self, user_id: int, group_id: int, removed_by: User) -> bool:
        """
        Remove um grupo de um usuário
        :param user_id: ID do usuário
        :param group_id: ID do grupo
        :param removed_by: Usuário que está removendo
        :return: True se removido com sucesso
        """
        pass
    
    @abstractmethod
    def get_user_permissions(self, user_id: int) -> List[Permission]:
        """
        Obtém todas as permissões de um usuário
        :param user_id: ID do usuário
        :return: Lista de permissões
        """
        pass
    
    @abstractmethod
    def get_user_groups(self, user_id: int) -> List[Group]:
        """
        Obtém todos os grupos de um usuário
        :param user_id: ID do usuário
        :return: Lista de grupos
        """
        pass

class ISystemConfigService(ABC):
    """Interface para serviços de configuração do sistema"""
    
    @abstractmethod
    def get_config(self, key: str) -> Any:
        """
        Obtém uma configuração pelo key
        :param key: Chave da configuração
        :return: Valor da configuração
        """
        pass
    
    @abstractmethod
    def set_config(self, key: str, value: Any, description: str = "", updated_by: User = None) -> bool:
        """
        Define uma configuração
        :param key: Chave da configuração
        :param value: Valor da configuração
        :param description: Descrição da configuração
        :param updated_by: Usuário que está atualizando
        :return: True se definido com sucesso
        """
        pass
    
    @abstractmethod
    def delete_config(self, key: str, deleted_by: User = None) -> bool:
        """
        Deleta uma configuração
        :param key: Chave da configuração
        :param deleted_by: Usuário que está deletando
        :return: True se deletado com sucesso
        """
        pass
    
    @abstractmethod
    def list_configs(self, active_only: bool = True) -> QuerySet:
        """
        Lista todas as configurações
        :param active_only: Se deve listar apenas configurações ativas
        :return: QuerySet de configurações
        """
        pass

class IAuditLogService(ABC):
    """Interface para serviços de log de auditoria"""
    
    @abstractmethod
    def log_user_action(self, user: User, action: str, target_user: User = None, 
                       description: str = "", ip_address: str = None, 
                       user_agent: str = None, extra_data: Dict = None) -> None:
        """
        Registra uma ação do usuário
        :param user: Usuário que executou a ação
        :param action: Tipo de ação
        :param target_user: Usuário alvo (se aplicável)
        :param description: Descrição da ação
        :param ip_address: Endereço IP
        :param user_agent: User agent
        :param extra_data: Dados extras
        """
        pass
    
    @abstractmethod
    def get_user_activity_logs(self, user_id: int, limit: int = 100) -> QuerySet:
        """
        Obtém logs de atividade de um usuário
        :param user_id: ID do usuário
        :param limit: Limite de registros
        :return: QuerySet de logs
        """
        pass
    
    @abstractmethod
    def get_system_activity_logs(self, filters: Dict[str, Any] = None, limit: int = 100) -> QuerySet:
        """
        Obtém logs de atividade do sistema
        :param filters: Filtros para aplicar
        :param limit: Limite de registros
        :return: QuerySet de logs
        """
        pass
