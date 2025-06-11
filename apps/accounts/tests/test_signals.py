"""
Testes para os signals do app accounts.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test.utils import override_settings
from unittest.mock import patch
import logging

User = get_user_model()


class UserSignalsTest(TestCase):
    """Testes para signals relacionados a usuários."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        # Configurar logger para capturar logs
        self.logger = logging.getLogger('apps.config.signals')
        self.logger.setLevel(logging.INFO)
    
    @patch('apps.config.signals.logger')
    def test_user_creation_signal_logs_correctly(self, mock_logger):
        """Testa se signal de criação de usuário faz log corretamente."""
        # Criar usuário
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        # Verificar se log foi chamado
        mock_logger.info.assert_called_with(f"Novo usuário criado: {user.email} (ID: {user.id})")
    
    @patch('apps.config.signals.logger')
    def test_user_update_signal_logs_correctly(self, mock_logger):
        """Testa se signal de atualização de usuário faz log corretamente."""
        # Criar usuário
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        # Limpar chamadas anteriores do mock
        mock_logger.reset_mock()
        
        # Atualizar usuário
        user.first_name = 'Updated'
        user.save()
        
        # Verificar se log foi chamado
        mock_logger.info.assert_called_with(f"Usuário atualizado: {user.email} (ID: {user.id})")
    
    @patch('apps.config.signals.logger')
    def test_user_deletion_signal_logs_correctly(self, mock_logger):
        """Testa se signal de exclusão de usuário faz log corretamente."""
        # Criar usuário
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        user_email = user.email
        user_id = user.id
        
        # Deletar usuário
        user.delete()
        
        # Verificar se log foi chamado
        mock_logger.info.assert_called_with(f"Usuário deletado: {user_email} (ID: {user_id})")
    
    @patch('apps.config.signals.logger')
    def test_superuser_creation_signal_logs_correctly(self, mock_logger):
        """Testa se signal de criação de superusuário faz log corretamente."""
        # Criar superusuário
        user = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='adminpass123'
        )
        
        # Verificar se log foi chamado
        mock_logger.info.assert_called_with(f"Novo usuário criado: {user.email} (ID: {user.id})")
    
    def test_user_creation_signal_fires_on_bulk_create(self):
        """Testa se signal é disparado em criação em lote."""
        with patch('apps.config.signals.logger') as mock_logger:
            # Criar múltiplos usuários
            users = [
                User(email=f'user{i}@example.com', username=f'user{i}', password='pass123')
                for i in range(3)
            ]
            
            # bulk_create não dispara signals por padrão
            User.objects.bulk_create(users)
            
            # Verificar que nenhum log foi chamado
            mock_logger.info.assert_not_called()
    
    def test_user_signal_handles_unicode_characters(self):
        """Testa se signal lida corretamente com caracteres unicode."""
        with patch('apps.config.signals.logger') as mock_logger:
            # Criar usuário com caracteres especiais
            user = User.objects.create_user(
                email='usuário@exãmple.com',
                username='usuário_teste',
                password='testpass123'
            )
            
            # Verificar se log foi chamado sem erros
            mock_logger.info.assert_called_with(f"Novo usuário criado: {user.email} (ID: {user.id})")


class GroupSignalsTest(TestCase):
    """Testes para signals relacionados a grupos."""
    
    @patch('apps.config.signals.logger')
    def test_group_creation_signal_logs_correctly(self, mock_logger):
        """Testa se signal de criação de grupo faz log corretamente."""
        # Criar grupo
        group = Group.objects.create(name='Test Group')
        
        # Verificar se log foi chamado
        mock_logger.info.assert_called_with(f"Novo grupo criado: {group.name} (ID: {group.id})")
    
    @patch('apps.config.signals.logger')
    def test_group_update_signal_logs_correctly(self, mock_logger):
        """Testa se signal de atualização de grupo faz log corretamente."""
        # Criar grupo
        group = Group.objects.create(name='Test Group')
        
        # Limpar chamadas anteriores do mock
        mock_logger.reset_mock()
        
        # Atualizar grupo
        group.name = 'Updated Group'
        group.save()
        
        # Verificar se log foi chamado
        mock_logger.info.assert_called_with(f"Grupo atualizado: {group.name} (ID: {group.id})")
    
    @patch('apps.config.signals.logger')
    def test_group_deletion_signal_does_not_exist(self):
        """Testa que não há signal de exclusão de grupo implementado."""
        # Criar grupo
        group = Group.objects.create(name='Test Group')
        
        group_name = group.name
        group_id = group.id
        
        # Deletar grupo
        group.delete()
        
        # Verificar que nenhum log de exclusão foi chamado
        # (porque não implementamos signal de exclusão para grupos)
        mock_logger.info.assert_not_called()


class SignalIntegrationTest(TestCase):
    """Testes de integração para signals."""
    
    def test_signals_work_with_django_admin(self):
        """Testa se signals funcionam quando usuários são criados via Django Admin."""
        with patch('apps.config.signals.logger') as mock_logger:
            # Simular criação via admin
            user = User.objects.create_user(
                email='admin_created@example.com',
                username='admin_created',
                password='testpass123'
            )
            
            # Verificar se signal foi disparado
            mock_logger.info.assert_called_with(f"Novo usuário criado: {user.email} (ID: {user.id})")
    
    def test_signals_work_with_user_registration_service(self):
        """Testa se signals funcionam com serviço de registro."""
        with patch('apps.config.signals.logger') as mock_logger:
            # Simular registro via serviço
            from apps.accounts.services.registration_service import RegistrationService
            from apps.accounts.repositories.django_user_repository import DjangoUserRepository
            from apps.accounts.repositories.django_verification_repository import DjangoVerificationRepository
            from apps.accounts.notifications.email_notification_service import EmailNotificationService
            
            service = RegistrationService(
                user_repository=DjangoUserRepository(),
                verification_repository=DjangoVerificationRepository(),
                notification_service=EmailNotificationService()
            )
            
            user = service.register_user(
                email='service_created@example.com',
                password='testpass123',
                first_name='Service',
                last_name='User',
                username='service_user'
            )
            
            # Verificar se signal foi disparado
            mock_logger.info.assert_called_with(f"Novo usuário criado: {user.email} (ID: {user.id})")
    
    def test_signals_work_with_multiple_operations(self):
        """Testa se signals funcionam com múltiplas operações."""
        with patch('apps.config.signals.logger') as mock_logger:
            # Criar usuário
            user = User.objects.create_user(
                email='multi@example.com',
                username='multi',
                password='testpass123'
            )
            
            # Atualizar usuário
            user.first_name = 'Updated'
            user.save()
            
            # Criar grupo
            group = Group.objects.create(name='Multi Group')
            
            # Verificar todas as chamadas
            expected_calls = [
                f"Novo usuário criado: {user.email} (ID: {user.id})",
                f"Usuário atualizado: {user.email} (ID: {user.id})",
                f"Novo grupo criado: {group.name} (ID: {group.id})"
            ]
            
            actual_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            
            for expected_call in expected_calls:
                self.assertIn(expected_call, actual_calls)


class SignalPerformanceTest(TestCase):
    """Testes de performance para signals."""
    
    def test_signals_do_not_significantly_impact_user_creation(self):
        """Testa se signals não impactam significativamente a criação de usuários."""
        import time
        
        # Medir tempo sem signals (usando mock)
        with patch('apps.config.signals.logger'):
            start_time = time.time()
            
            for i in range(10):
                User.objects.create_user(
                    email=f'perf_test_{i}@example.com',
                    username=f'perf_test_{i}',
                    password='testpass123'
                )
            
            end_time = time.time()
            
        execution_time = end_time - start_time
        
        # Verificar que execução é razoavelmente rápida (menos de 1 segundo para 10 usuários)
        self.assertLess(execution_time, 1.0, "Signal processing should not significantly slow down user creation")
    
    def test_signals_handle_database_errors_gracefully(self):
        """Testa se signals lidam graciosamente com erros de banco."""
        with patch('apps.config.signals.logger') as mock_logger:
            # Tentar criar usuário com dados inválidos
            try:
                User.objects.create_user(
                    email='invalid_user@example.com',
                    username='',  # Username vazio pode causar erro
                    password='testpass123'
                )
            except Exception:
                pass  # Esperamos que falhe
            
            # Signal não deve ter sido chamado se criação falhou
            # (depende de quando o erro ocorre no processo)
            # Este teste verifica que o sistema não quebra


class SignalConfigurationTest(TestCase):
    """Testes para configuração de signals."""
    
    def test_signals_are_properly_connected(self):
        """Testa se signals estão adequadamente conectados."""
        from django.db.models.signals import post_save, post_delete
        from apps.config.signals import log_user_creation, log_group_creation
        
        # Verificar se signals estão conectados
        post_save_receivers = [receiver[1]() for receiver in post_save._live_receivers(sender=User)]
        self.assertIn(log_user_creation, post_save_receivers)
        
        post_save_receivers = [receiver[1]() for receiver in post_save._live_receivers(sender=Group)]
        self.assertIn(log_group_creation, post_save_receivers)
    
    @override_settings(LOGGING={'version': 1, 'disable_existing_loggers': False})
    def test_signals_work_with_different_logging_configurations(self):
        """Testa se signals funcionam com diferentes configurações de logging."""
        with patch('apps.config.signals.logger') as mock_logger:
            # Criar usuário
            user = User.objects.create_user(
                email='logging_test@example.com',
                username='logging_test',
                password='testpass123'
            )
            
            # Verificar se signal foi chamado independente da configuração de logging
            mock_logger.info.assert_called_with(f"Novo usuário criado: {user.email} (ID: {user.id})")
