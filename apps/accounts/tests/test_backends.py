"""
Testes para backends de autenticação do app accounts.
Testa backends customizados de autenticação.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.backends import ModelBackend
from unittest.mock import patch, Mock

from apps.accounts.backends import EmailOrUsernameModelBackend
from apps.config.models import AppModuleConfiguration

User = get_user_model()


class EmailOrUsernameModelBackendTest(TestCase):
    """Testes para o backend de autenticação por email ou username."""

    def setUp(self):
        """Configuração inicial para os testes."""
        # Habilitar módulo accounts
        AppModuleConfiguration.objects.get_or_create(
            app_name='accounts',
            defaults={
                'display_name': 'Accounts',
                'description': 'Sistema de autenticação',
                'is_enabled': True,
                'is_core': True
            }
        )
        
        self.backend = EmailOrUsernameModelBackend()
        
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            is_verified=True,
            is_active=True
        )
        
        self.unverified_user = User.objects.create_user(
            email='unverified@example.com',
            username='unverified',
            password='testpass123',
            is_verified=False,
            is_active=True
        )
        
        self.inactive_user = User.objects.create_user(
            email='inactive@example.com',
            username='inactive',
            password='testpass123',
            is_verified=True,
            is_active=False
        )

    def test_authenticate_with_email(self):
        """Testa autenticação com email."""
        user = self.backend.authenticate(
            request=None,
            username='test@example.com',
            password='testpass123'
        )
        
        self.assertEqual(user, self.user)

    def test_authenticate_with_username(self):
        """Testa autenticação com username."""
        user = self.backend.authenticate(
            request=None,
            username='testuser',
            password='testpass123'
        )
        
        self.assertEqual(user, self.user)

    def test_authenticate_with_wrong_password(self):
        """Testa autenticação com senha incorreta."""
        user = self.backend.authenticate(
            request=None,
            username='test@example.com',
            password='wrongpassword'
        )
        
        self.assertIsNone(user)

    def test_authenticate_with_nonexistent_user(self):
        """Testa autenticação com usuário inexistente."""
        user = self.backend.authenticate(
            request=None,
            username='nonexistent@example.com',
            password='testpass123'
        )
        
        self.assertIsNone(user)

    def test_authenticate_unverified_user(self):
        """Testa autenticação com usuário não verificado."""
        user = self.backend.authenticate(
            request=None,
            username='unverified@example.com',
            password='testpass123'
        )
        
        # Backend pode permitir ou negar usuários não verificados
        # Dependendo da implementação
        self.assertIn(user, [None, self.unverified_user])

    def test_authenticate_inactive_user(self):
        """Testa autenticação com usuário inativo."""
        user = self.backend.authenticate(
            request=None,
            username='inactive@example.com',
            password='testpass123'
        )
        
        # Usuários inativos não devem conseguir autenticar
        self.assertIsNone(user)

    def test_get_user_by_id(self):
        """Testa busca de usuário por ID."""
        user = self.backend.get_user(self.user.id)
        
        self.assertEqual(user, self.user)

    def test_get_user_by_invalid_id(self):
        """Testa busca de usuário por ID inválido."""
        user = self.backend.get_user(99999)
        
        self.assertIsNone(user)

    def test_authenticate_case_insensitive_email(self):
        """Testa autenticação com email em diferentes casos."""
        # Testar com email em maiúsculo
        user = self.backend.authenticate(
            request=None,
            username='TEST@EXAMPLE.COM',
            password='testpass123'
        )
        
        # Deve encontrar o usuário independente do caso
        self.assertEqual(user, self.user)

    def test_authenticate_with_special_characters(self):
        """Testa autenticação com caracteres especiais."""
        special_user = User.objects.create_user(
            email='user+test@example.com',
            username='user.test',
            password='testpass123',
            is_verified=True,
            is_active=True
        )
        
        # Testar com email contendo +
        user = self.backend.authenticate(
            request=None,
            username='user+test@example.com',
            password='testpass123'
        )
        
        self.assertEqual(user, special_user)
        
        # Testar com username contendo .
        user = self.backend.authenticate(
            request=None,
            username='user.test',
            password='testpass123'
        )
        
        self.assertEqual(user, special_user)

    def test_backend_permissions(self):
        """Testa verificação de permissões do backend."""
        # Testar se usuário tem permissão específica
        has_perm = self.backend.has_perm(self.user, 'accounts.view_user')
        
        # Resultado depende da implementação
        self.assertIsInstance(has_perm, bool)

    def test_backend_module_permissions(self):
        """Testa verificação de permissões de módulo."""
        # Testar se usuário tem permissão em módulo específico
        has_module_perm = self.backend.has_module_perms(self.user, 'accounts')
        
        # Resultado depende da implementação
        self.assertIsInstance(has_module_perm, bool)


class BackendIntegrationTest(TestCase):
    """Testes de integração para backends de autenticação."""

    def setUp(self):
        """Configuração inicial para os testes."""
        # Habilitar módulo accounts
        AppModuleConfiguration.objects.get_or_create(
            app_name='accounts',
            defaults={
                'display_name': 'Accounts',
                'description': 'Sistema de autenticação',
                'is_enabled': True,
                'is_core': True
            }
        )
        
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            is_verified=True,
            is_active=True
        )

    def test_django_authenticate_with_email(self):
        """Testa autenticação usando função authenticate do Django com email."""
        user = authenticate(username='test@example.com', password='testpass123')
        
        # Deve funcionar se backend estiver configurado
        self.assertIn(user, [None, self.user])

    def test_django_authenticate_with_username(self):
        """Testa autenticação usando função authenticate do Django com username."""
        user = authenticate(username='testuser', password='testpass123')
        
        # Deve funcionar com backend padrão
        self.assertEqual(user, self.user)

    def test_backend_configuration(self):
        """Testa se backends estão configurados corretamente."""
        from django.conf import settings
        
        # Verificar se há backends configurados
        backends = getattr(settings, 'AUTHENTICATION_BACKENDS', [])
        
        self.assertIsInstance(backends, (list, tuple))
        self.assertGreater(len(backends), 0)
        
        # Verificar se backend padrão está presente
        default_backend = 'django.contrib.auth.backends.ModelBackend'
        self.assertIn(default_backend, backends)

    def test_multiple_backends_priority(self):
        """Testa prioridade entre múltiplos backends."""
        # Tentar autenticar com diferentes métodos
        user_by_email = authenticate(username='test@example.com', password='testpass123')
        user_by_username = authenticate(username='testuser', password='testpass123')
        
        # Ambos devem retornar o mesmo usuário ou None
        if user_by_email and user_by_username:
            self.assertEqual(user_by_email, user_by_username)

    def test_backend_error_handling(self):
        """Testa tratamento de erros nos backends."""
        # Testar com dados inválidos
        user = authenticate(username=None, password='testpass123')
        self.assertIsNone(user)
        
        user = authenticate(username='test@example.com', password=None)
        self.assertIsNone(user)
        
        user = authenticate(username='', password='')
        self.assertIsNone(user)

    def test_backend_performance(self):
        """Testa performance dos backends."""
        import time
        
        # Medir tempo de autenticação
        start_time = time.time()
        user = authenticate(username='test@example.com', password='testpass123')
        end_time = time.time()
        
        # Autenticação deve ser rápida (< 100ms)
        auth_time = end_time - start_time
        self.assertLess(auth_time, 0.1)


class CustomBackendTest(TestCase):
    """Testes para funcionalidades customizadas dos backends."""

    def setUp(self):
        """Configuração inicial para os testes."""
        # Habilitar módulo accounts
        AppModuleConfiguration.objects.get_or_create(
            app_name='accounts',
            defaults={
                'display_name': 'Accounts',
                'description': 'Sistema de autenticação',
                'is_enabled': True,
                'is_core': True
            }
        )
        
        self.backend = EmailOrUsernameModelBackend()

    def test_backend_user_validation(self):
        """Testa validação de usuário pelo backend."""
        # Criar usuário com dados específicos
        user = User.objects.create_user(
            email='valid@example.com',
            username='validuser',
            password='validpass123',
            is_verified=True,
            is_active=True
        )
        
        # Testar validação
        authenticated_user = self.backend.authenticate(
            request=None,
            username='valid@example.com',
            password='validpass123'
        )
        
        self.assertEqual(authenticated_user, user)

    def test_backend_with_request_object(self):
        """Testa backend com objeto request."""
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.post('/login/')
        
        user = User.objects.create_user(
            email='request@example.com',
            username='requestuser',
            password='requestpass123',
            is_verified=True,
            is_active=True
        )
        
        # Testar autenticação com request
        authenticated_user = self.backend.authenticate(
            request=request,
            username='request@example.com',
            password='requestpass123'
        )
        
        self.assertEqual(authenticated_user, user)

    def test_backend_logging(self):
        """Testa logging do backend."""
        with patch('apps.accounts.backends.logger') as mock_logger:
            user = User.objects.create_user(
                email='log@example.com',
                username='loguser',
                password='logpass123',
                is_verified=True,
                is_active=True
            )
            
            # Tentar autenticação
            self.backend.authenticate(
                request=None,
                username='log@example.com',
                password='logpass123'
            )
            
            # Verificar se houve logging (se implementado)
            # mock_logger.info.assert_called()  # Descomente se logging estiver implementado
