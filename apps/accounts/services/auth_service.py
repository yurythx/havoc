from django.contrib.auth import authenticate
from apps.accounts.interfaces.services import IAuthService
from django.core.exceptions import ObjectDoesNotExist

class AuthService(IAuthService):
    """Serviço para autenticação de usuários"""
    
    def __init__(self, user_repository):
        self.user_repository = user_repository
    
    def authenticate_user(self, email: str, password: str):
        """
        Autentica um usuário
        :return: Instância do usuário se autenticação for válida, None caso contrário
        :raises ValueError: Se o usuário não estiver verificado
        """
        user = authenticate(email=email, password=password)
        
        if user is None:
            return None
            
        if not user.is_verified:
            raise ValueError("Este usuário não está verificado. Por favor, verifique seu e-mail.")
            
        return user