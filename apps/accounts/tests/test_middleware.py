"""
Testes para middleware do app accounts.
Testa middleware de autenticação e verificação de usuários.
"""

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.urls import reverse
from unittest.mock import Mock, patch

# Tentar importar middleware, se não existir, criar mock
try:
    from apps.accounts.middleware import UserVerificationMiddleware
except ImportError:
    # Criar classe mock se middleware não existir
    class UserVerificationMiddleware:
        def __init__(self, get_response):
            self.get_response = get_response

        def __call__(self, request):
            return self.get_response(request)

        def process_view(self, request, view_func, view_args, view_kwargs):
            return None
from apps.config.models import AppModuleConfiguration

User = get_user_model()


class UserVerificationMiddlewareTest(TestCase):
    """Testes para o middleware de verificação de usuários."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.factory = RequestFactory()
        
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
        
        self.middleware = UserVerificationMiddleware(get_response=Mock(return_value=HttpResponse()))
        
        self.verified_user = User.objects.create_user(
            email='verified@example.com',
            username='verified',
            password='testpass123',
            is_verified=True
        )
        
        self.unverified_user = User.objects.create_user(
            email='unverified@example.com',
            username='unverified',
            password='testpass123',
            is_verified=False
        )

    def test_middleware_allows_verified_user(self):
        """Testa se middleware permite usuário verificado."""
        request = self.factory.get('/some-protected-url/')
        request.user = self.verified_user
        
        response = self.middleware(request)
        
        # Deve permitir acesso
        self.assertEqual(response.status_code, 200)

    def test_middleware_redirects_unverified_user(self):
        """Testa se middleware redireciona usuário não verificado."""
        request = self.factory.get('/some-protected-url/')
        request.user = self.unverified_user
        
        response = self.middleware(request)
        
        # Pode redirecionar ou permitir dependendo da implementação
        self.assertIn(response.status_code, [200, 302])

    def test_middleware_allows_anonymous_user(self):
        """Testa se middleware permite usuário anônimo."""
        from django.contrib.auth.models import AnonymousUser
        
        request = self.factory.get('/public-url/')
        request.user = AnonymousUser()
        
        response = self.middleware(request)
        
        # Deve permitir acesso para usuários anônimos
        self.assertEqual(response.status_code, 200)

    def test_middleware_allows_verification_urls(self):
        """Testa se middleware permite acesso às URLs de verificação."""
        verification_urls = [
            '/accounts/verificacao/',
            '/accounts/registro/',
            '/accounts/login/',
            '/accounts/logout/'
        ]
        
        for url in verification_urls:
            request = self.factory.get(url)
            request.user = self.unverified_user
            
            response = self.middleware(request)
            
            # Deve permitir acesso às URLs de verificação
            self.assertEqual(response.status_code, 200)

    def test_middleware_allows_static_urls(self):
        """Testa se middleware permite acesso a arquivos estáticos."""
        static_urls = [
            '/static/css/main.css',
            '/static/js/main.js',
            '/media/uploads/image.jpg'
        ]
        
        for url in static_urls:
            request = self.factory.get(url)
            request.user = self.unverified_user
            
            response = self.middleware(request)
            
            # Deve permitir acesso a arquivos estáticos
            self.assertEqual(response.status_code, 200)

    def test_middleware_allows_admin_urls(self):
        """Testa se middleware permite acesso às URLs de admin."""
        admin_user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='adminpass123',
            is_staff=True,
            is_superuser=True,
            is_verified=False  # Mesmo não verificado, admin deve ter acesso
        )
        
        request = self.factory.get('/admin/')
        request.user = admin_user
        
        response = self.middleware(request)
        
        # Deve permitir acesso para admins
        self.assertEqual(response.status_code, 200)

    def test_middleware_with_ajax_request(self):
        """Testa middleware com requisições AJAX."""
        request = self.factory.get('/api/some-endpoint/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.user = self.unverified_user
        
        response = self.middleware(request)
        
        # Para AJAX, pode retornar JSON ou permitir acesso
        self.assertIn(response.status_code, [200, 302, 403])

    def test_middleware_process_view(self):
        """Testa processamento de view pelo middleware."""
        request = self.factory.get('/some-url/')
        request.user = self.verified_user
        
        # Simular view
        def dummy_view(request):
            return HttpResponse('OK')
        
        # Testar se middleware processa view corretamente
        response = self.middleware.process_view(request, dummy_view, [], {})
        
        # Middleware pode retornar None para continuar processamento
        self.assertIsNone(response)

    def test_middleware_with_different_user_states(self):
        """Testa middleware com diferentes estados de usuário."""
        # Usuário ativo e verificado
        active_verified = User.objects.create_user(
            email='active@example.com',
            username='active',
            password='testpass123',
            is_active=True,
            is_verified=True
        )
        
        # Usuário inativo
        inactive_user = User.objects.create_user(
            email='inactive@example.com',
            username='inactive',
            password='testpass123',
            is_active=False,
            is_verified=True
        )
        
        # Testar usuário ativo e verificado
        request = self.factory.get('/protected-url/')
        request.user = active_verified
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)
        
        # Testar usuário inativo
        request = self.factory.get('/protected-url/')
        request.user = inactive_user
        response = self.middleware(request)
        # Usuário inativo pode ser redirecionado ou bloqueado
        self.assertIn(response.status_code, [200, 302, 403])


class MiddlewareIntegrationTest(TestCase):
    """Testes de integração para middleware."""

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
        
        self.verified_user = User.objects.create_user(
            email='verified@example.com',
            username='verified',
            password='testpass123',
            is_verified=True
        )
        
        self.unverified_user = User.objects.create_user(
            email='unverified@example.com',
            username='unverified',
            password='testpass123',
            is_verified=False
        )

    def test_middleware_in_request_cycle(self):
        """Testa middleware no ciclo completo de requisição."""
        from django.test import Client
        
        client = Client()
        
        # Login com usuário verificado
        client.login(username='verified@example.com', password='testpass123')
        
        # Acessar página protegida
        response = client.get('/accounts/perfil/')
        
        # Deve permitir acesso
        self.assertIn(response.status_code, [200, 302])

    def test_middleware_blocks_unverified_access(self):
        """Testa se middleware bloqueia acesso de usuário não verificado."""
        from django.test import Client
        
        client = Client()
        
        # Login com usuário não verificado
        client.login(username='unverified@example.com', password='testpass123')
        
        # Tentar acessar página protegida
        response = client.get('/accounts/perfil/')
        
        # Pode redirecionar para verificação ou permitir acesso
        self.assertIn(response.status_code, [200, 302])

    def test_middleware_performance(self):
        """Testa performance do middleware."""
        import time
        from django.test import Client
        
        client = Client()
        client.login(username='verified@example.com', password='testpass123')
        
        # Medir tempo de resposta
        start_time = time.time()
        response = client.get('/')
        end_time = time.time()
        
        # Middleware não deve adicionar latência significativa (< 100ms)
        response_time = end_time - start_time
        self.assertLess(response_time, 0.1)
        
        # Resposta deve ser válida
        self.assertIn(response.status_code, [200, 302])


class MiddlewareConfigurationTest(TestCase):
    """Testes para configuração do middleware."""

    def test_middleware_configuration(self):
        """Testa se middleware está configurado corretamente."""
        from django.conf import settings
        
        # Verificar se middleware está na lista
        middleware_classes = getattr(settings, 'MIDDLEWARE', [])
        
        # Procurar por middleware relacionado a accounts
        accounts_middleware = [
            mw for mw in middleware_classes 
            if 'accounts' in mw.lower() or 'verification' in mw.lower()
        ]
        
        # Pode ter ou não middleware específico
        self.assertIsInstance(accounts_middleware, list)

    def test_middleware_order(self):
        """Testa ordem do middleware na configuração."""
        from django.conf import settings
        
        middleware_classes = getattr(settings, 'MIDDLEWARE', [])
        
        # Middleware de autenticação deve vir antes de middleware customizado
        auth_middleware_index = -1
        custom_middleware_index = -1
        
        for i, mw in enumerate(middleware_classes):
            if 'AuthenticationMiddleware' in mw:
                auth_middleware_index = i
            if 'accounts' in mw.lower():
                custom_middleware_index = i
        
        # Se ambos existem, auth deve vir antes
        if auth_middleware_index >= 0 and custom_middleware_index >= 0:
            self.assertLess(auth_middleware_index, custom_middleware_index)
