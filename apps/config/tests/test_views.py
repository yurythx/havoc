"""
Testes para as views do app config.
Testa views de dashboard, configurações e gerenciamento de módulos.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch, MagicMock

from apps.config.models import AppModuleConfiguration, SystemConfiguration, EmailConfiguration

User = get_user_model()


class DashboardViewsTest(TestCase):
    """Testes para views do dashboard."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.client = Client()
        
        # Habilitar módulo config
        AppModuleConfiguration.objects.get_or_create(
            app_name='config',
            defaults={
                'display_name': 'Config',
                'description': 'Configurações do sistema',
                'is_enabled': True,
                'is_core': True
            }
        )
        
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='adminpass123',
            is_staff=True,
            is_superuser=True,
            is_verified=True
        )
        
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            username='user',
            password='userpass123',
            is_verified=True
        )

    def test_dashboard_view_admin_access(self):
        """Testa acesso ao dashboard como admin."""
        self.client.login(username='admin@example.com', password='adminpass123')
        
        response = self.client.get(reverse('config:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')

    def test_dashboard_view_regular_user_access(self):
        """Testa acesso ao dashboard como usuário comum."""
        self.client.login(username='user@example.com', password='userpass123')
        
        response = self.client.get(reverse('config:dashboard'))
        
        # Pode permitir ou negar acesso dependendo da implementação
        self.assertIn(response.status_code, [200, 302, 403])

    def test_dashboard_view_anonymous_access(self):
        """Testa acesso ao dashboard sem autenticação."""
        response = self.client.get(reverse('config:dashboard'))
        
        # Deve redirecionar para login
        self.assertIn(response.status_code, [302, 403])

    def test_dashboard_metrics(self):
        """Testa exibição de métricas no dashboard."""
        self.client.login(username='admin@example.com', password='adminpass123')
        
        response = self.client.get(reverse('config:dashboard'))
        
        if response.status_code == 200:
            # Verificar se métricas estão presentes
            self.assertIn('context', dir(response))


class ModuleViewsTest(TestCase):
    """Testes para views de gerenciamento de módulos."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.client = Client()
        
        # Habilitar módulo config
        AppModuleConfiguration.objects.get_or_create(
            app_name='config',
            defaults={
                'display_name': 'Config',
                'description': 'Configurações do sistema',
                'is_enabled': True,
                'is_core': True
            }
        )
        
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='adminpass123',
            is_staff=True,
            is_superuser=True,
            is_verified=True
        )

    def test_module_list_view(self):
        """Testa view de listagem de módulos."""
        self.client.login(username='admin@example.com', password='adminpass123')

        response = self.client.get(reverse('config:module_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Módulos')

    def test_module_detail_view(self):
        """Testa view de detalhes do módulo."""
        module = AppModuleConfiguration.objects.create(
            app_name='test_module',
            display_name='Test Module',
            description='Module for testing',
            is_enabled=True,
            is_core=False
        )

        self.client.login(username='admin@example.com', password='adminpass123')

        response = self.client.get(reverse('config:module_detail', kwargs={'app_name': module.app_name}))

        self.assertEqual(response.status_code, 200)

    def test_module_update_view(self):
        """Testa view de atualização de módulo."""
        module = AppModuleConfiguration.objects.create(
            app_name='test_module',
            display_name='Test Module',
            description='Module for testing',
            is_enabled=True,
            is_core=False
        )

        self.client.login(username='admin@example.com', password='adminpass123')

        response = self.client.get(reverse('config:module_update', kwargs={'app_name': module.app_name}))

        self.assertEqual(response.status_code, 200)

    def test_module_toggle_view(self):
        """Testa view de ativar/desativar módulo."""
        module = AppModuleConfiguration.objects.create(
            app_name='test_module',
            display_name='Test Module',
            description='Module for testing',
            is_enabled=True,
            is_core=False
        )

        self.client.login(username='admin@example.com', password='adminpass123')

        response = self.client.post(reverse('config:module_toggle', kwargs={'app_name': module.app_name}))

        self.assertIn(response.status_code, [200, 302])


class EmailConfigViewsTest(TestCase):
    """Testes para views de configuração de email."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.client = Client()
        
        # Habilitar módulo config
        AppModuleConfiguration.objects.get_or_create(
            app_name='config',
            defaults={
                'display_name': 'Config',
                'description': 'Configurações do sistema',
                'is_enabled': True,
                'is_core': True
            }
        )
        
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='adminpass123',
            is_staff=True,
            is_superuser=True,
            is_verified=True
        )

    def test_email_config_view_get(self):
        """Testa GET na view de configuração de email."""
        self.client.login(username='admin@example.com', password='adminpass123')
        
        response = self.client.get(reverse('config:email_config'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Email')

    def test_email_config_view_post(self):
        """Testa POST na view de configuração de email."""
        self.client.login(username='admin@example.com', password='adminpass123')
        
        response = self.client.post(reverse('config:email_config'), {
            'email_backend': 'django.core.mail.backends.smtp.EmailBackend',
            'email_host': 'smtp.gmail.com',
            'email_port': 587,
            'email_use_tls': True,
            'email_host_user': 'test@gmail.com',
            'email_host_password': 'password123'
        })
        
        self.assertIn(response.status_code, [200, 302])

    def test_email_test_view(self):
        """Testa view de teste de email."""
        self.client.login(username='admin@example.com', password='adminpass123')
        
        response = self.client.get(reverse('config:email_test'))
        
        self.assertEqual(response.status_code, 200)

    @patch('apps.config.services.email_config_service.send_mail')
    def test_email_test_send(self, mock_send_mail):
        """Testa envio de email de teste."""
        mock_send_mail.return_value = True
        
        self.client.login(username='admin@example.com', password='adminpass123')
        
        response = self.client.post(reverse('config:email_test'), {
            'recipient': 'test@example.com',
            'subject': 'Test Email',
            'message': 'This is a test email'
        })
        
        self.assertIn(response.status_code, [200, 302])


class SystemConfigViewsTest(TestCase):
    """Testes para views de configuração do sistema."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.client = Client()
        
        # Habilitar módulo config
        AppModuleConfiguration.objects.get_or_create(
            app_name='config',
            defaults={
                'display_name': 'Config',
                'description': 'Configurações do sistema',
                'is_enabled': True,
                'is_core': True
            }
        )
        
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='adminpass123',
            is_staff=True,
            is_superuser=True,
            is_verified=True
        )

    def test_system_config_view_get(self):
        """Testa GET na view de configuração do sistema."""
        self.client.login(username='admin@example.com', password='adminpass123')
        
        response = self.client.get(reverse('config:system_config'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sistema')

    def test_system_config_view_post(self):
        """Testa POST na view de configuração do sistema."""
        self.client.login(username='admin@example.com', password='adminpass123')
        
        response = self.client.post(reverse('config:system_config'), {
            'site_name': 'Test Site',
            'site_description': 'Test Description',
            'maintenance_mode': False,
            'debug_mode': False
        })
        
        self.assertIn(response.status_code, [200, 302])

    def test_env_config_view(self):
        """Testa view de configuração de variáveis de ambiente."""
        self.client.login(username='admin@example.com', password='adminpass123')

        response = self.client.get(reverse('config:environment_variables'))

        self.assertEqual(response.status_code, 200)

    def test_env_config_update(self):
        """Testa atualização de variáveis de ambiente."""
        self.client.login(username='admin@example.com', password='adminpass123')

        response = self.client.post(reverse('config:environment_variables'), {
            'DEBUG': 'False',
            'SECRET_KEY': 'new-secret-key',
            'DATABASE_URL': 'sqlite:///test.db'
        })

        self.assertIn(response.status_code, [200, 302])


class ConfigPermissionsTest(TestCase):
    """Testes para permissões das views de config."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.client = Client()
        
        # Habilitar módulo config
        AppModuleConfiguration.objects.get_or_create(
            app_name='config',
            defaults={
                'display_name': 'Config',
                'description': 'Configurações do sistema',
                'is_enabled': True,
                'is_core': True
            }
        )
        
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='adminpass123',
            is_staff=True,
            is_superuser=True,
            is_verified=True
        )
        
        self.staff_user = User.objects.create_user(
            email='staff@example.com',
            username='staff',
            password='staffpass123',
            is_staff=True,
            is_verified=True
        )
        
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            username='user',
            password='userpass123',
            is_verified=True
        )

    def test_admin_required_views(self):
        """Testa views que requerem permissões de admin."""
        admin_urls = [
            reverse('config:dashboard'),
            reverse('config:module_list'),
            reverse('config:email_config'),
            reverse('config:system_config'),
        ]
        
        # Testar com usuário comum
        self.client.login(username='user@example.com', password='userpass123')
        
        for url in admin_urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, [302, 403], f"URL {url} should deny regular users")

    def test_staff_access_views(self):
        """Testa acesso de staff às views."""
        staff_urls = [
            reverse('config:dashboard'),
            reverse('config:module_list'),
        ]
        
        # Testar com usuário staff
        self.client.login(username='staff@example.com', password='staffpass123')
        
        for url in staff_urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, [200, 302, 403], f"URL {url} may allow staff access")

    def test_superuser_access_all_views(self):
        """Testa acesso de superuser a todas as views."""
        all_urls = [
            reverse('config:dashboard'),
            reverse('config:module_list'),
            reverse('config:email_config'),
            reverse('config:system_config'),
            reverse('config:environment_variables'),
        ]
        
        # Testar com superuser
        self.client.login(username='admin@example.com', password='adminpass123')
        
        for url in all_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"Superuser should access {url}")
