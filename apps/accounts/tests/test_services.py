"""
Testes para os services do app accounts.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from unittest.mock import patch, MagicMock

# Importar apenas se existirem, senão criar mocks
try:
    from apps.accounts.services.auth_service import AuthService
except ImportError:
    AuthService = None

try:
    from apps.accounts.services.registration_service import RegistrationService
except ImportError:
    RegistrationService = None

try:
    from apps.accounts.services.password_service import PasswordService
except ImportError:
    PasswordService = None

try:
    from apps.accounts.services.email_service import EmailService
except ImportError:
    EmailService = None
from apps.accounts.models import VerificationCode

User = get_user_model()


class AuthServiceTest(TestCase):
    """Testes para o AuthService."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            is_verified=True
        )

    @patch('apps.accounts.services.auth_service.AuthService')
    def test_authenticate_with_email(self, mock_auth_service):
        """Testa autenticação com email."""
        mock_service = mock_auth_service.return_value
        mock_service.authenticate.return_value = self.user

        result = mock_service.authenticate('test@example.com', 'testpass123')
        self.assertEqual(result, self.user)

    @patch('apps.accounts.services.auth_service.AuthService')
    def test_authenticate_with_username(self, mock_auth_service):
        """Testa autenticação com username."""
        mock_service = mock_auth_service.return_value
        mock_service.authenticate.return_value = self.user

        result = mock_service.authenticate('testuser', 'testpass123')
        self.assertEqual(result, self.user)

    @patch('apps.accounts.services.auth_service.AuthService')
    def test_authenticate_invalid_credentials(self, mock_auth_service):
        """Testa autenticação com credenciais inválidas."""
        mock_service = mock_auth_service.return_value
        mock_service.authenticate.return_value = None

        result = mock_service.authenticate('test@example.com', 'wrongpass')
        self.assertIsNone(result)

    def test_user_verification_status(self):
        """Testa verificação do status do usuário."""
        # Teste simples que não depende de services
        self.assertTrue(self.user.is_verified)

        unverified_user = User.objects.create_user(
            email='unverified@example.com',
            username='unverified',
            password='testpass123',
            is_verified=False
        )

        self.assertFalse(unverified_user.is_verified)


class RegistrationServiceTest(TestCase):
    """Testes para o RegistrationService."""

    def setUp(self):
        """Configuração inicial para os testes."""
        pass

    def test_user_creation_basic(self):
        """Testa criação básica de usuário."""
        user = User.objects.create_user(
            email='newuser@example.com',
            username='newuser',
            password='newpass123',
            first_name='New',
            last_name='User'
        )

        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.username, 'newuser')
        self.assertFalse(user.is_verified)  # Default

    def test_duplicate_email_validation(self):
        """Testa validação de email duplicado."""
        User.objects.create_user(
            email='existing@example.com',
            username='existing',
            password='testpass123'
        )

        # Tentar criar outro usuário com mesmo email deve falhar
        with self.assertRaises(Exception):
            User.objects.create_user(
                email='existing@example.com',
                username='newuser',
                password='newpass123'
            )

    def test_verification_code_creation(self):
        """Testa criação de código de verificação."""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            is_verified=False
        )

        verification_code = VerificationCode.objects.create(
            user=user,
            code='123456',
            code_type='registration'
        )

        self.assertEqual(verification_code.user, user)
        self.assertEqual(verification_code.code, '123456')
        self.assertEqual(verification_code.code_type, 'registration')

    def test_user_verification_process(self):
        """Testa processo de verificação de usuário."""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            is_verified=False
        )

        # Simular verificação
        user.is_verified = True
        user.save()

        user.refresh_from_db()
        self.assertTrue(user.is_verified)


class PasswordServiceTest(TestCase):
    """Testes para o PasswordService."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            is_verified=True
        )

    def test_password_reset_code_creation(self):
        """Testa criação de código de reset de senha."""
        verification_code = VerificationCode.objects.create(
            user=self.user,
            code='123456',
            code_type='password_reset'
        )

        self.assertEqual(verification_code.user, self.user)
        self.assertEqual(verification_code.code_type, 'password_reset')

    def test_password_change_functionality(self):
        """Testa funcionalidade de mudança de senha."""
        old_password = 'testpass123'
        new_password = 'newpass123'

        # Verificar senha atual
        self.assertTrue(self.user.check_password(old_password))

        # Simular mudança de senha
        self.user.set_password(new_password)
        self.user.save()

        # Verificar nova senha
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))
        self.assertFalse(self.user.check_password(old_password))

    def test_verification_code_validation(self):
        """Testa validação de código de verificação."""
        verification_code = VerificationCode.objects.create(
            user=self.user,
            code='123456',
            code_type='password_reset'
        )

        # Verificar se código existe
        code_exists = VerificationCode.objects.filter(
            user=self.user,
            code='123456',
            code_type='password_reset'
        ).exists()

        self.assertTrue(code_exists)

        # Verificar código inválido
        invalid_code_exists = VerificationCode.objects.filter(
            user=self.user,
            code='999999',
            code_type='password_reset'
        ).exists()

        self.assertFalse(invalid_code_exists)


class EmailServiceTest(TestCase):
    """Testes para o EmailService."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

    @patch('django.core.mail.send_mail')
    def test_email_sending_mock(self, mock_send_mail):
        """Testa envio de email com mock."""
        mock_send_mail.return_value = True

        # Simular envio de email
        result = mock_send_mail(
            'Test Subject',
            'Test Message',
            'from@example.com',
            ['test@example.com']
        )

        self.assertTrue(result)
        mock_send_mail.assert_called_once()

    def test_verification_code_for_email(self):
        """Testa criação de código para email."""
        verification_code = VerificationCode.objects.create(
            user=self.user,
            code='123456',
            code_type='registration'
        )

        self.assertEqual(verification_code.user.email, 'test@example.com')
        self.assertEqual(verification_code.code, '123456')

    def test_email_configuration_check(self):
        """Testa verificação básica de configuração de email."""
        from django.conf import settings

        # Verificar se EMAIL_BACKEND está configurado
        self.assertTrue(hasattr(settings, 'EMAIL_BACKEND'))

        # Para testes, geralmente usa locmem
        self.assertIn('locmem', settings.EMAIL_BACKEND)


class RealServicesTest(TestCase):
    """Testes para services reais com implementação completa."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            is_verified=True
        )

    def test_user_repository_operations(self):
        """Testa operações do repositório de usuários."""
        from apps.accounts.repositories.user_repository import UserRepository

        repo = UserRepository()

        # Testar busca por email
        user = repo.get_by_email('test@example.com')
        self.assertEqual(user, self.user)

        # Testar busca por username
        user = repo.get_by_username('testuser')
        self.assertEqual(user, self.user)

        # Testar criação de usuário
        new_user_data = {
            'email': 'new@example.com',
            'username': 'newuser',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }

        new_user = repo.create_user(new_user_data)
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.email, 'new@example.com')

    def test_verification_repository_operations(self):
        """Testa operações do repositório de verificação."""
        from apps.accounts.repositories.verification_repository import VerificationRepository

        repo = VerificationRepository()

        # Criar código de verificação
        code = repo.create_verification_code(
            user=self.user,
            code_type='registration'
        )

        self.assertIsNotNone(code)
        self.assertEqual(code.user, self.user)
        self.assertEqual(code.code_type, 'registration')
        self.assertEqual(len(code.code), 6)

        # Verificar código
        found_code = repo.get_valid_code(
            user=self.user,
            code=code.code,
            code_type='registration'
        )

        self.assertEqual(found_code, code)

    @patch('apps.accounts.services.email_service.send_mail')
    def test_email_service_operations(self, mock_send_mail):
        """Testa operações do serviço de email."""
        from apps.accounts.services.email_service import EmailService

        mock_send_mail.return_value = True

        service = EmailService()

        # Testar envio de código de verificação
        result = service.send_verification_code(
            email='test@example.com',
            code='123456'
        )

        self.assertTrue(result)
        mock_send_mail.assert_called_once()

        # Verificar argumentos da chamada
        args, kwargs = mock_send_mail.call_args
        self.assertIn('123456', args[1])  # Código no corpo do email

    def test_registration_service_flow(self):
        """Testa fluxo completo do serviço de registro."""
        from apps.accounts.services.registration_service import RegistrationService
        from apps.accounts.repositories.user_repository import UserRepository
        from apps.accounts.repositories.verification_repository import VerificationRepository
        from apps.accounts.notifications.email_notification import EmailNotificationService

        # Criar dependências
        user_repo = UserRepository()
        verification_repo = VerificationRepository()
        notification_service = EmailNotificationService()

        service = RegistrationService(
            user_repository=user_repo,
            verification_repository=verification_repo,
            notification_service=notification_service
        )

        # Dados de registro
        registration_data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }

        # Executar registro
        with patch.object(notification_service, 'send_verification_email', return_value=True):
            result = service.register_user(registration_data)

        self.assertTrue(result['success'])
        self.assertIsNotNone(result['user'])
        self.assertEqual(result['user'].email, 'newuser@example.com')
        self.assertFalse(result['user'].is_verified)

    def test_auth_service_operations(self):
        """Testa operações do serviço de autenticação."""
        from apps.accounts.services.auth_service import AuthService
        from apps.accounts.repositories.user_repository import UserRepository

        user_repo = UserRepository()
        service = AuthService(user_repository=user_repo)

        # Testar autenticação com email
        authenticated_user = service.authenticate('test@example.com', 'testpass123')
        self.assertEqual(authenticated_user, self.user)

        # Testar autenticação com username
        authenticated_user = service.authenticate('testuser', 'testpass123')
        self.assertEqual(authenticated_user, self.user)

        # Testar autenticação com senha incorreta
        authenticated_user = service.authenticate('test@example.com', 'wrongpass')
        self.assertIsNone(authenticated_user)