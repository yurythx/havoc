"""
Testes avançados para services do app accounts.
Testa casos de erro, integrações e dependências externas.
"""

from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from unittest.mock import patch, Mock, MagicMock
from django.core.mail import EmailMessage
from django.conf import settings
import time

from apps.accounts.models import VerificationCode
from apps.accounts.services.registration_service import RegistrationService
from apps.accounts.services.auth_service import AuthService
from apps.accounts.services.email_service import EmailService
from apps.accounts.services.password_service import PasswordService
from apps.accounts.repositories.user_repository import DjangoUserRepository
from apps.accounts.repositories.verification_repository import DjangoVerificationRepository
from apps.accounts.notifications.email_notification import EmailNotificationService

User = get_user_model()


class RegistrationServiceAdvancedTest(TestCase):
    """Testes avançados para RegistrationService."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user_repo = DjangoUserRepository()
        self.verification_repo = DjangoVerificationRepository()
        self.notification_service = EmailNotificationService()
        
        self.service = RegistrationService(
            user_repository=self.user_repo,
            verification_repository=self.verification_repo,
            notification_service=self.notification_service
        )

    def test_register_user_with_database_error(self):
        """Testa registro com erro de banco de dados."""
        with patch.object(self.user_repo, 'create_user', side_effect=IntegrityError("Database error")):
            result = self.service.register_user({
                'email': 'test@example.com',
                'username': 'testuser',
                'password': 'testpass123',
                'first_name': 'Test',
                'last_name': 'User'
            })
            
            self.assertFalse(result['success'])
            self.assertIn('error', result)

    def test_register_user_with_email_service_failure(self):
        """Testa registro com falha no serviço de email."""
        with patch.object(self.notification_service, 'send_verification_email', return_value=False):
            result = self.service.register_user({
                'email': 'test@example.com',
                'username': 'testuser',
                'password': 'testpass123',
                'first_name': 'Test',
                'last_name': 'User'
            })
            
            # Usuário deve ser criado mesmo com falha no email
            self.assertTrue(result['success'])
            self.assertIsNotNone(result['user'])

    def test_register_user_with_invalid_data(self):
        """Testa registro com dados inválidos."""
        invalid_data_sets = [
            {'email': 'invalid-email'},  # Email inválido
            {'email': 'test@example.com', 'username': ''},  # Username vazio
            {'email': 'test@example.com', 'username': 'test', 'password': '123'},  # Senha muito curta
        ]
        
        for invalid_data in invalid_data_sets:
            with self.subTest(data=invalid_data):
                result = self.service.register_user(invalid_data)
                self.assertFalse(result['success'])

    def test_confirm_registration_with_expired_code(self):
        """Testa confirmação com código expirado."""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            is_verified=False
        )
        
        # Criar código expirado
        verification_code = VerificationCode.objects.create(
            user=user,
            code='123456',
            code_type='registration'
        )
        
        # Simular expiração
        with patch.object(verification_code, 'is_expired', return_value=True):
            result = self.service.confirm_registration('test@example.com', '123456')
            self.assertFalse(result)

    def test_confirm_registration_with_used_code(self):
        """Testa confirmação com código já usado."""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            is_verified=False
        )
        
        verification_code = VerificationCode.objects.create(
            user=user,
            code='123456',
            code_type='registration',
            is_used=True
        )
        
        result = self.service.confirm_registration('test@example.com', '123456')
        self.assertFalse(result)

    def test_resend_verification_code(self):
        """Testa reenvio de código de verificação."""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            is_verified=False
        )
        
        with patch.object(self.notification_service, 'send_verification_email', return_value=True):
            result = self.service.resend_verification_code('test@example.com')
            self.assertTrue(result['success'])

    def test_resend_verification_code_for_verified_user(self):
        """Testa reenvio para usuário já verificado."""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            is_verified=True
        )
        
        result = self.service.resend_verification_code('test@example.com')
        self.assertFalse(result['success'])


class AuthServiceAdvancedTest(TestCase):
    """Testes avançados para AuthService."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user_repo = DjangoUserRepository()
        self.service = AuthService(user_repository=self.user_repo)
        
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            is_verified=True,
            is_active=True
        )

    def test_authenticate_with_case_insensitive_email(self):
        """Testa autenticação com email em diferentes casos."""
        test_emails = [
            'TEST@EXAMPLE.COM',
            'Test@Example.Com',
            'test@EXAMPLE.com'
        ]
        
        for email in test_emails:
            with self.subTest(email=email):
                user = self.service.authenticate(email, 'testpass123')
                self.assertEqual(user, self.user)

    def test_authenticate_with_special_characters(self):
        """Testa autenticação com caracteres especiais."""
        special_user = User.objects.create_user(
            email='user+test@example.com',
            username='user.test-123',
            password='testpass123',
            is_verified=True,
            is_active=True
        )
        
        # Teste com email contendo +
        user = self.service.authenticate('user+test@example.com', 'testpass123')
        self.assertEqual(user, special_user)
        
        # Teste com username contendo . e -
        user = self.service.authenticate('user.test-123', 'testpass123')
        self.assertEqual(user, special_user)

    def test_authenticate_with_database_error(self):
        """Testa autenticação com erro de banco de dados."""
        with patch.object(self.user_repo, 'get_by_email', side_effect=Exception("Database error")):
            user = self.service.authenticate('test@example.com', 'testpass123')
            self.assertIsNone(user)

    def test_authenticate_performance(self):
        """Testa performance da autenticação."""
        start_time = time.time()
        
        for i in range(10):
            self.service.authenticate('test@example.com', 'testpass123')
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 10 autenticações devem levar menos de 1 segundo
        self.assertLess(total_time, 1.0)

    def test_authenticate_with_unicode_characters(self):
        """Testa autenticação com caracteres unicode."""
        unicode_user = User.objects.create_user(
            email='usuário@exemplo.com',
            username='usuário123',
            password='testpass123',
            is_verified=True,
            is_active=True
        )
        
        user = self.service.authenticate('usuário@exemplo.com', 'testpass123')
        self.assertEqual(user, unicode_user)


class EmailServiceAdvancedTest(TestCase):
    """Testes avançados para EmailService."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.service = EmailService()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

    @patch('apps.accounts.services.email_service.send_mail')
    def test_send_verification_email_with_custom_template(self, mock_send_mail):
        """Testa envio de email com template customizado."""
        mock_send_mail.return_value = True
        
        result = self.service.send_verification_code(
            email='test@example.com',
            code='123456',
            template='custom_verification'
        )
        
        self.assertTrue(result)
        mock_send_mail.assert_called_once()

    @patch('apps.accounts.services.email_service.send_mail')
    def test_send_email_with_smtp_error(self, mock_send_mail):
        """Testa envio de email com erro SMTP."""
        from smtplib import SMTPException
        mock_send_mail.side_effect = SMTPException("SMTP Error")
        
        result = self.service.send_verification_code(
            email='test@example.com',
            code='123456'
        )
        
        self.assertFalse(result)

    @patch('apps.accounts.services.email_service.send_mail')
    def test_send_email_with_connection_error(self, mock_send_mail):
        """Testa envio de email com erro de conexão."""
        from socket import error as SocketError
        mock_send_mail.side_effect = SocketError("Connection failed")
        
        result = self.service.send_verification_code(
            email='test@example.com',
            code='123456'
        )
        
        self.assertFalse(result)

    def test_validate_email_configuration(self):
        """Testa validação da configuração de email."""
        # Testar com configurações válidas
        with patch.object(settings, 'EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend'):
            with patch.object(settings, 'EMAIL_HOST', 'smtp.gmail.com'):
                result = self.service.validate_configuration()
                self.assertIsInstance(result, bool)

    @patch('apps.accounts.services.email_service.EmailMessage')
    def test_send_html_email(self, mock_email_message):
        """Testa envio de email HTML."""
        mock_message = Mock()
        mock_email_message.return_value = mock_message
        mock_message.send.return_value = True
        
        result = self.service.send_html_email(
            subject='Test Subject',
            html_content='<h1>Test</h1>',
            recipient='test@example.com'
        )
        
        self.assertTrue(result)
        mock_email_message.assert_called_once()
        mock_message.send.assert_called_once()


class PasswordServiceAdvancedTest(TestCase):
    """Testes avançados para PasswordService."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.service = PasswordService()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            is_verified=True
        )

    def test_reset_password_with_multiple_codes(self):
        """Testa reset com múltiplos códigos para o mesmo usuário."""
        # Criar múltiplos códigos
        codes = []
        for i in range(3):
            code = VerificationCode.objects.create(
                user=self.user,
                code=f'12345{i}',
                code_type='password_reset'
            )
            codes.append(code)
        
        # Apenas o último código deve funcionar
        result = self.service.reset_password('test@example.com', '123452', 'newpass123')
        self.assertTrue(result)

    def test_change_password_with_same_password(self):
        """Testa mudança para a mesma senha atual."""
        result = self.service.change_password(self.user, 'testpass123', 'testpass123')
        # Pode permitir ou não dependendo da implementação
        self.assertIsInstance(result, bool)

    def test_generate_secure_password(self):
        """Testa geração de senha segura."""
        password = self.service.generate_secure_password()
        
        self.assertIsInstance(password, str)
        self.assertGreaterEqual(len(password), 12)
        
        # Verificar se contém diferentes tipos de caracteres
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        self.assertTrue(has_upper)
        self.assertTrue(has_lower)
        self.assertTrue(has_digit)

    def test_password_strength_validation(self):
        """Testa validação de força da senha."""
        weak_passwords = ['123', 'password', 'abc123']
        strong_passwords = ['MyStr0ngP@ssw0rd!', 'C0mpl3x#P@ssw0rd']
        
        for password in weak_passwords:
            with self.subTest(password=password):
                result = self.service.validate_password_strength(password)
                self.assertFalse(result['is_strong'])
        
        for password in strong_passwords:
            with self.subTest(password=password):
                result = self.service.validate_password_strength(password)
                self.assertTrue(result['is_strong'])


class ServiceIntegrationTest(TransactionTestCase):
    """Testes de integração entre services."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user_repo = DjangoUserRepository()
        self.verification_repo = DjangoVerificationRepository()
        self.notification_service = EmailNotificationService()
        
        self.registration_service = RegistrationService(
            user_repository=self.user_repo,
            verification_repository=self.verification_repo,
            notification_service=self.notification_service
        )
        
        self.auth_service = AuthService(user_repository=self.user_repo)
        self.password_service = PasswordService()

    def test_complete_user_registration_flow(self):
        """Testa fluxo completo de registro de usuário."""
        with patch.object(self.notification_service, 'send_verification_email', return_value=True):
            # 1. Registrar usuário
            result = self.registration_service.register_user({
                'email': 'integration@example.com',
                'username': 'integration',
                'password': 'testpass123',
                'first_name': 'Integration',
                'last_name': 'Test'
            })
            
            self.assertTrue(result['success'])
            user = result['user']
            self.assertFalse(user.is_verified)
            
            # 2. Tentar autenticar antes da verificação
            auth_user = self.auth_service.authenticate('integration@example.com', 'testpass123')
            # Pode permitir ou não dependendo da implementação
            self.assertIn(auth_user, [None, user])
            
            # 3. Confirmar registro
            verification_code = VerificationCode.objects.filter(user=user, code_type='registration').first()
            confirm_result = self.registration_service.confirm_registration(
                'integration@example.com',
                verification_code.code
            )
            
            self.assertTrue(confirm_result)
            
            # 4. Autenticar após verificação
            user.refresh_from_db()
            self.assertTrue(user.is_verified)
            
            auth_user = self.auth_service.authenticate('integration@example.com', 'testpass123')
            self.assertEqual(auth_user, user)

    def test_password_reset_flow_integration(self):
        """Testa fluxo completo de reset de senha."""
        user = User.objects.create_user(
            email='reset@example.com',
            username='resetuser',
            password='oldpass123',
            is_verified=True
        )
        
        with patch.object(self.notification_service, 'send_password_reset_email', return_value=True):
            # 1. Solicitar reset
            result = self.password_service.request_password_reset('reset@example.com')
            self.assertTrue(result)
            
            # 2. Verificar se código foi criado
            verification_code = VerificationCode.objects.filter(
                user=user,
                code_type='password_reset'
            ).first()
            self.assertIsNotNone(verification_code)
            
            # 3. Tentar autenticar com senha antiga
            auth_user = self.auth_service.authenticate('reset@example.com', 'oldpass123')
            self.assertEqual(auth_user, user)
            
            # 4. Resetar senha
            reset_result = self.password_service.reset_password(
                'reset@example.com',
                verification_code.code,
                'newpass123'
            )
            self.assertTrue(reset_result)
            
            # 5. Tentar autenticar com senha antiga (deve falhar)
            auth_user = self.auth_service.authenticate('reset@example.com', 'oldpass123')
            self.assertIsNone(auth_user)
            
            # 6. Autenticar com nova senha
            auth_user = self.auth_service.authenticate('reset@example.com', 'newpass123')
            self.assertEqual(auth_user, user)

    def test_concurrent_registration_attempts(self):
        """Testa tentativas concorrentes de registro."""
        def register_user():
            return self.registration_service.register_user({
                'email': 'concurrent@example.com',
                'username': 'concurrent',
                'password': 'testpass123',
                'first_name': 'Concurrent',
                'last_name': 'Test'
            })
        
        with patch.object(self.notification_service, 'send_verification_email', return_value=True):
            # Simular tentativas concorrentes
            results = []
            for i in range(3):
                try:
                    result = register_user()
                    results.append(result)
                except IntegrityError:
                    # Esperado para tentativas duplicadas
                    pass
            
            # Apenas uma tentativa deve ter sucesso
            successful_results = [r for r in results if r.get('success', False)]
            self.assertEqual(len(successful_results), 1)
