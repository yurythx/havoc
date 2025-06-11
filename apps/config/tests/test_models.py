"""
Testes para os modelos do app config.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from apps.config.models import (
    SystemConfiguration, 
    DatabaseConfiguration, 
    EmailConfiguration,
    AppModuleConfiguration
)

User = get_user_model()


class SystemConfigurationModelTest(TestCase):
    """Testes para o modelo SystemConfiguration."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
    
    def test_system_configuration_creation(self):
        """Testa criação de configuração do sistema."""
        config = SystemConfiguration.objects.create(
            key='site_name',
            value='Test Site',
            description='Nome do site',
            updated_by=self.user
        )

        self.assertEqual(config.key, 'site_name')
        self.assertEqual(config.value, 'Test Site')
        self.assertEqual(config.description, 'Nome do site')
        self.assertTrue(config.is_active)
        self.assertEqual(config.updated_by, self.user)
        self.assertIsNotNone(config.created_at)
        self.assertIsNotNone(config.updated_at)
    
    def test_system_configuration_str_representation(self):
        """Testa representação string da configuração."""
        config = SystemConfiguration.objects.create(
            key='test_key',
            value='Test Value',
            updated_by=self.user
        )

        expected = f"test_key: Test Value..."
        self.assertEqual(str(config), expected)

    def test_system_configuration_defaults(self):
        """Testa valores padrão da configuração."""
        config = SystemConfiguration.objects.create(
            key='test_config',
            value='test_value',
            updated_by=self.user
        )

        self.assertTrue(config.is_active)
        self.assertEqual(config.description, '')

    def test_system_configuration_json_methods(self):
        """Testa métodos de JSON."""
        config = SystemConfiguration.objects.create(
            key='json_config',
            value='{"test": "value", "number": 123}',
            updated_by=self.user
        )

        json_value = config.get_value_as_json()
        self.assertEqual(json_value['test'], 'value')
        self.assertEqual(json_value['number'], 123)

        # Testa set_value_from_dict
        new_data = {'new_key': 'new_value', 'count': 456}
        config.set_value_from_dict(new_data)

        parsed_value = config.get_value_as_json()
        self.assertEqual(parsed_value['new_key'], 'new_value')
        self.assertEqual(parsed_value['count'], 456)


class DatabaseConfigurationModelTest(TestCase):
    """Testes para o modelo DatabaseConfiguration."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
    
    def test_database_configuration_creation(self):
        """Testa criação de configuração de banco de dados."""
        config = DatabaseConfiguration.objects.create(
            name='test_db',
            engine='postgresql',
            host='localhost',
            port=5432,
            user='testuser',
            password='testpass',
            created_by=self.user
        )
        
        self.assertEqual(config.name, 'test_db')
        self.assertEqual(config.engine, 'postgresql')
        self.assertEqual(config.host, 'localhost')
        self.assertEqual(config.port, 5432)
        self.assertEqual(config.user, 'testuser')
        self.assertEqual(config.password, 'testpass')
        self.assertEqual(config.created_by, self.user)
    
    def test_database_configuration_str_representation(self):
        """Testa representação string da configuração de banco."""
        config = DatabaseConfiguration.objects.create(
            name='test_db',
            engine='django.db.backends.postgresql',
            created_by=self.user
        )

        expected = f"🟢 {config.name}"
        self.assertEqual(str(config), expected)

    def test_database_configuration_defaults(self):
        """Testa valores padrão da configuração de banco."""
        config = DatabaseConfiguration.objects.create(
            name='test_db',
            created_by=self.user
        )

        self.assertEqual(config.engine, 'django.db.backends.postgresql')
        self.assertEqual(config.host, 'localhost')
        self.assertTrue(config.is_active)
        self.assertFalse(config.is_default)
    
    def test_database_configuration_engine_choices(self):
        """Testa escolhas válidas para engine."""
        valid_engines = [
            'django.db.backends.sqlite3',
            'django.db.backends.postgresql',
            'django.db.backends.mysql',
            'django.db.backends.oracle'
        ]

        for i, engine in enumerate(valid_engines):
            config = DatabaseConfiguration.objects.create(
                name=f'test_db_{i}',
                engine=engine,
                created_by=self.user
            )
            self.assertEqual(config.engine, engine)


class EmailConfigurationModelTest(TestCase):
    """Testes para o modelo EmailConfiguration."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
    
    def test_email_configuration_creation(self):
        """Testa criação de configuração de email."""
        config = EmailConfiguration.objects.create(
            name='Gmail Config',
            email_backend='django.core.mail.backends.smtp.EmailBackend',
            email_host='smtp.gmail.com',
            email_port=587,
            email_use_tls=True,
            email_host_user='test@gmail.com',
            email_host_password='password123',
            default_from_email='noreply@test.com',
            created_by=self.user
        )

        self.assertEqual(config.name, 'Gmail Config')
        self.assertEqual(config.email_backend, 'django.core.mail.backends.smtp.EmailBackend')
        self.assertEqual(config.email_host, 'smtp.gmail.com')
        self.assertEqual(config.email_port, 587)
        self.assertTrue(config.email_use_tls)
        self.assertEqual(config.email_host_user, 'test@gmail.com')
        self.assertEqual(config.email_host_password, 'password123')
        self.assertEqual(config.default_from_email, 'noreply@test.com')
        self.assertEqual(config.created_by, self.user)
    
    def test_email_configuration_str_representation(self):
        """Testa representação string da configuração de email."""
        config = EmailConfiguration.objects.create(
            name='Test Config',
            email_backend='django.core.mail.backends.smtp.EmailBackend',
            email_host='smtp.gmail.com',
            default_from_email='test@example.com',
            created_by=self.user
        )

        expected = f"🟢 {config.name}"
        self.assertEqual(str(config), expected)

    def test_email_configuration_defaults(self):
        """Testa valores padrão da configuração de email."""
        config = EmailConfiguration.objects.create(
            name='Default Config',
            email_host='localhost',
            default_from_email='test@example.com',
            created_by=self.user
        )

        self.assertEqual(config.email_backend, 'django.core.mail.backends.smtp.EmailBackend')
        self.assertEqual(config.email_port, 587)
        self.assertTrue(config.email_use_tls)  # Padrão é True
        self.assertFalse(config.email_use_ssl)
        self.assertTrue(config.is_active)
        self.assertFalse(config.is_default)

    def test_email_configuration_backend_choices(self):
        """Testa escolhas válidas para backend."""
        valid_backends = [
            'django.core.mail.backends.smtp.EmailBackend',
            'django.core.mail.backends.console.EmailBackend',
            'django.core.mail.backends.locmem.EmailBackend',
            'django.core.mail.backends.filebased.EmailBackend'
        ]

        for i, backend in enumerate(valid_backends):
            config = EmailConfiguration.objects.create(
                name=f'Test Config {i}',
                email_backend=backend,
                email_host='localhost',
                default_from_email='test@example.com',
                created_by=self.user
            )
            self.assertEqual(config.email_backend, backend)
    
    def test_email_configuration_validation(self):
        """Testa validações da configuração de email."""
        # Testa validação de configuração padrão única
        EmailConfiguration.objects.create(
            name='Default Config',
            email_host='localhost',
            default_from_email='test@example.com',
            is_default=True,
            created_by=self.user
        )

        # Tentar criar outra configuração padrão deve falhar
        with self.assertRaises(ValidationError):
            config = EmailConfiguration(
                name='Another Default',
                email_host='localhost',
                default_from_email='test2@example.com',
                is_default=True,
                created_by=self.user
            )
            config.full_clean()


class AppModuleConfigurationModelTest(TestCase):
    """Testes para o modelo AppModuleConfiguration."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
    
    def test_app_module_configuration_creation(self):
        """Testa criação de configuração de módulo."""
        config = AppModuleConfiguration.objects.create(
            app_name='articles',
            display_name='Artigos',
            description='Módulo de gerenciamento de artigos',
            is_enabled=True,
            created_by=self.user
        )

        self.assertEqual(config.app_name, 'articles')
        self.assertEqual(config.display_name, 'Artigos')
        self.assertEqual(config.description, 'Módulo de gerenciamento de artigos')
        self.assertTrue(config.is_enabled)
        self.assertEqual(config.created_by, self.user)
        self.assertEqual(config.module_type, 'feature')
        self.assertEqual(config.status, 'active')
    
    def test_app_module_configuration_str_representation(self):
        """Testa representação string da configuração de módulo."""
        config = AppModuleConfiguration.objects.create(
            app_name='articles',
            display_name='Artigos',
            created_by=self.user
        )

        expected = f"{config.display_name} ({config.app_name})"
        self.assertEqual(str(config), expected)

    def test_app_module_configuration_defaults(self):
        """Testa valores padrão da configuração de módulo."""
        config = AppModuleConfiguration.objects.create(
            app_name='test_app',
            display_name='Test App',
            created_by=self.user
        )

        self.assertTrue(config.is_enabled)
        self.assertEqual(config.module_type, 'feature')
        self.assertEqual(config.status, 'active')
        self.assertFalse(config.is_core)
    
    def test_app_module_configuration_unique_constraint(self):
        """Testa constraint único para app_name."""
        AppModuleConfiguration.objects.create(
            app_name='articles',
            display_name='Artigos',
            created_by=self.user
        )
        
        # Tentar criar outro módulo com mesmo app_name deve falhar
        with self.assertRaises(IntegrityError):
            AppModuleConfiguration.objects.create(
                app_name='articles',
                display_name='Artigos 2',
                created_by=self.user
            )
    
    def test_app_module_configuration_core_apps(self):
        """Testa comportamento de apps principais."""
        # Criar um app principal
        config = AppModuleConfiguration.objects.create(
            app_name='accounts',  # App principal
            display_name='Contas',
            created_by=self.user
        )

        # Deve ser automaticamente marcado como core
        self.assertTrue(config.is_core)
        self.assertTrue(config.is_enabled)
        self.assertEqual(config.module_type, 'core')

    def test_app_module_configuration_properties(self):
        """Testa propriedades do módulo."""
        config = AppModuleConfiguration.objects.create(
            app_name='test_app',
            display_name='Test App',
            status='active',
            is_enabled=True,
            created_by=self.user
        )

        # Testa is_available
        self.assertTrue(config.is_available)

        # Testa can_be_disabled
        self.assertTrue(config.can_be_disabled)

        # Testa com app core
        core_config = AppModuleConfiguration.objects.create(
            app_name='config',  # App principal
            display_name='Configurações',
            created_by=self.user
        )

        self.assertFalse(core_config.can_be_disabled)
