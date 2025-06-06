from abc import ABC, abstractmethod
from typing import Optional
from django.contrib.auth import get_user_model

User = get_user_model()

class IRegistrationService(ABC):
    """Interface para serviços de registro de usuário"""
    
    @abstractmethod
    def register_user(self, email: str, password: str, **extra_fields) -> User:
        """
        Registra um novo usuário e envia código de verificação
        :param email: Email do usuário
        :param password: Senha do usuário
        :param extra_fields: Campos adicionais do usuário
        :return: Instância do usuário criado
        :raises ValueError: Se o usuário já existir
        """
        pass
    
    @abstractmethod
    def confirm_registration(self, email: str, code: str) -> bool:
        """
        Confirma o registro de um usuário com o código recebido
        :param email: Email do usuário
        :param code: Código de verificação
        :return: True se a confirmação for bem-sucedida
        """
        pass


class IPasswordService(ABC):
    """Interface para serviços de recuperação de senha"""
    
    @abstractmethod
    def request_password_reset(self, email: str) -> bool:
        """
        Solicita um reset de senha, enviando código por email
        :param email: Email do usuário
        :return: True se a solicitação for válida
        """
        pass
    
    @abstractmethod
    def confirm_password_reset(self, email: str, code: str, new_password: str) -> bool:
        """
        Confirma o reset de senha com o código recebido
        :param email: Email do usuário
        :param code: Código de verificação
        :param new_password: Nova senha
        :return: True se a confirmação for bem-sucedida
        """
        pass


class IAuthService(ABC):
    """Interface para serviços de autenticação"""
    
    @abstractmethod
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Autentica um usuário
        :param email: Email do usuário
        :param password: Senha do usuário
        :return: Instância do usuário se autenticação for válida, None caso contrário
        :raises ValueError: Se o usuário não estiver verificado
        """
        pass