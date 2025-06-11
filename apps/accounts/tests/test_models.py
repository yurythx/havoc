"""
Testes para os modelos do app accounts.
"""
import tempfile
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.accounts.models import User, VerificationCode

User = get_user_model()


class UserModelTest(TestCase):
    """Testes para o modelo User customizado."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123'
        }

    def test_create_user(self):
        """Testa criação de usuário comum."""
        user = User.objects.create_user(**self.user_data)

        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Testa criação de superusuário."""
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )

        self.assertEqual(user.username, 'admin')
        self.assertEqual(user.email, 'admin@example.com')
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_user_str_representation(self):
        """Testa representação string do usuário."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), user.email)

    def test_user_get_full_name(self):
        """Testa método get_full_name."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.get_full_name(), "Test User")

    def test_user_get_short_name(self):
        """Testa método get_short_name."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.get_short_name(), "Test")

    def test_email_unique_constraint(self):
        """Testa que email deve ser único."""
        User.objects.create_user(**self.user_data)

        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='testuser2',
                email='test@example.com',  # Email duplicado
                password='testpass123'
            )

    def test_username_unique_constraint(self):
        """Testa que username deve ser único."""
        User.objects.create_user(**self.user_data)

        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='testuser',  # Username duplicado
                email='test2@example.com',
                password='testpass123'
            )

    def test_email_validation(self):
        """Testa validação de email."""
        invalid_emails = [
            'invalid-email',
            '@example.com',
            'test@',
            'test..test@example.com'
        ]

        for invalid_email in invalid_emails:
            with self.assertRaises(ValidationError):
                user = User(
                    username='testuser',
                    email=invalid_email,
                    password='testpass123'
                )
                user.full_clean()


    def test_user_slug_generation(self):
        """Testa geração automática de slug."""
        user = User.objects.create_user(**self.user_data)
        self.assertTrue(user.slug)
        self.assertEqual(user.slug, 'test')  # Baseado no email test@example.com

    def test_user_avatar_methods(self):
        """Testa métodos relacionados ao avatar."""
        user = User.objects.create_user(**self.user_data)

        # Testa avatar padrão
        avatar_url = user.get_avatar_url()
        self.assertIn('ui-avatars.com', avatar_url)

        # Testa iniciais
        initials = user.get_initials()
        self.assertEqual(initials, 'TU')  # Test User

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_avatar_upload(self):
        """Testa upload de avatar."""
        user = User.objects.create_user(**self.user_data)

        # Criar arquivo de imagem fake
        image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'

        uploaded_file = SimpleUploadedFile(
            name='test_avatar.png',
            content=image_content,
            content_type='image/png'
        )

        user.avatar = uploaded_file
        user.save()

        self.assertTrue(user.avatar)
        self.assertIn('avatars/', user.avatar.name)

    def test_user_profile_fields(self):
        """Testa campos de perfil do usuário."""
        user = User.objects.create_user(**self.user_data)

        # Testa campos opcionais
        user.bio = "Esta é minha biografia"
        user.phone = "+55 11 99999-9999"
        user.birth_date = "1990-01-01"
        user.location = "São Paulo, SP"
        user.save()

        user.refresh_from_db()

        self.assertEqual(user.bio, "Esta é minha biografia")
        self.assertEqual(user.phone, "+55 11 99999-9999")
        self.assertEqual(str(user.birth_date), "1990-01-01")
        self.assertEqual(user.location, "São Paulo, SP")

    def test_user_verification_status(self):
        """Testa status de verificação do usuário."""
        user = User.objects.create_user(**self.user_data)

        # Por padrão, usuário não está verificado
        self.assertFalse(user.is_verified)

        # Testa verificação
        user.is_verified = True
        user.save()

        user.refresh_from_db()
        self.assertTrue(user.is_verified)


class VerificationCodeModelTest(TestCase):
    """Testes para o modelo VerificationCode."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_verification_code_creation(self):
        """Testa criação de código de verificação."""
        code = VerificationCode.objects.create(
            user=self.user,
            code='123456',
            code_type=VerificationCode.REGISTRATION
        )

        self.assertEqual(code.user, self.user)
        self.assertEqual(code.code, '123456')
        self.assertEqual(code.code_type, VerificationCode.REGISTRATION)
        self.assertIsNotNone(code.created_at)
        self.assertIsNotNone(code.expires_at)

    def test_verification_code_str_representation(self):
        """Testa representação string do código de verificação."""
        code = VerificationCode.objects.create(
            user=self.user,
            code='123456',
            code_type=VerificationCode.REGISTRATION
        )

        expected = f"{self.user.email} - {code.get_code_type_display()} - {code.code}"
        self.assertEqual(str(code), expected)

    def test_verification_code_expiration(self):
        """Testa expiração do código."""
        code = VerificationCode.objects.create(
            user=self.user,
            code='123456',
            code_type=VerificationCode.REGISTRATION
        )

        # Código não deve estar expirado inicialmente
        self.assertFalse(code.is_expired())

        # Verificar se expires_at foi definido automaticamente
        self.assertIsNotNone(code.expires_at)

    def test_verification_code_types(self):
        """Testa tipos de código de verificação."""
        # Testa tipo REGISTRATION
        code_reg = VerificationCode.objects.create(
            user=self.user,
            code='123456',
            code_type=VerificationCode.REGISTRATION
        )
        self.assertEqual(code_reg.code_type, VerificationCode.REGISTRATION)
        self.assertEqual(code_reg.get_code_type_display(), 'Registro de Conta')

        # Testa tipo PASSWORD_RESET
        code_pass = VerificationCode.objects.create(
            user=self.user,
            code='654321',
            code_type=VerificationCode.PASSWORD_RESET
        )
        self.assertEqual(code_pass.code_type, VerificationCode.PASSWORD_RESET)
        self.assertEqual(code_pass.get_code_type_display(), 'Redefinição de Senha')

    def test_verification_code_unique_constraint(self):
        """Testa constraint único por usuário e tipo."""
        # Criar primeiro código
        VerificationCode.objects.create(
            user=self.user,
            code='123456',
            code_type=VerificationCode.REGISTRATION
        )

        # Tentar criar segundo código do mesmo tipo deve falhar
        with self.assertRaises(IntegrityError):
            VerificationCode.objects.create(
                user=self.user,
                code='654321',
                code_type=VerificationCode.REGISTRATION
            )