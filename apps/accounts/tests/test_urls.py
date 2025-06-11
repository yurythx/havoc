"""
Testes para as URLs do app accounts.
"""
from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from apps.accounts.views import (
    RegistrationView, VerificationView, LoginView, LogoutView,
    PasswordResetRequestView, PasswordResetConfirmView,
    UserProfileView, UserUpdateView, RemoveAvatarView
)
from apps.accounts.views.email_test import (
    EmailDiagnosticView, TestEmailSendView, TestConnectionView,
    QuickEmailSetupView, PasswordResetTestView
)

User = get_user_model()


class AccountsURLsTest(TestCase):
    """Testes para URLs do app accounts."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
    
    def test_registration_url_resolves(self):
        """Testa se URL de registro resolve corretamente."""
        url = reverse('accounts:register')
        self.assertEqual(url, '/accounts/registro/')

        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, RegistrationView)
    
    def test_verification_url_resolves(self):
        """Testa se URL de verificação resolve corretamente."""
        url = reverse('accounts:verification')
        self.assertEqual(url, '/accounts/verificacao/')
        
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, VerificationView)
    
    def test_login_url_resolves(self):
        """Testa se URL de login resolve corretamente."""
        url = reverse('accounts:login')
        self.assertEqual(url, '/accounts/login/')
        
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, LoginView)
    
    def test_logout_url_resolves(self):
        """Testa se URL de logout resolve corretamente."""
        url = reverse('accounts:logout')
        self.assertEqual(url, '/accounts/logout/')
        
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, LogoutView)
    
    def test_password_reset_request_url_resolves(self):
        """Testa se URL de solicitação de reset resolve corretamente."""
        url = reverse('accounts:password_reset')
        self.assertEqual(url, '/accounts/redefinir-senha/')

        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, PasswordResetRequestView)

    def test_password_reset_confirm_url_resolves(self):
        """Testa se URL de confirmação de reset resolve corretamente."""
        url = reverse('accounts:password_reset_confirm')
        self.assertEqual(url, '/accounts/confirmar-senha/')

        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, PasswordResetConfirmView)

    def test_profile_url_resolves(self):
        """Testa se URL de perfil resolve corretamente."""
        url = reverse('accounts:profile')
        self.assertEqual(url, '/accounts/perfil/')

        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, UserProfileView)

    def test_settings_url_resolves(self):
        """Testa se URL de configurações resolve corretamente."""
        url = reverse('accounts:settings')
        self.assertEqual(url, '/accounts/configuracoes/')

        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, UserUpdateView)

    def test_remove_avatar_url_resolves(self):
        """Testa se URL de remoção de avatar resolve corretamente."""
        url = reverse('accounts:remove_avatar')
        self.assertEqual(url, '/accounts/remover-avatar/')

        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, RemoveAvatarView)
    
    def test_email_diagnostic_url_resolves(self):
        """Testa se URL de diagnóstico de email resolve corretamente."""
        url = reverse('accounts:email_diagnostic')
        self.assertEqual(url, '/accounts/email/diagnostico/')
        
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, EmailDiagnosticView)
    
    def test_test_email_send_url_resolves(self):
        """Testa se URL de teste de envio de email resolve corretamente."""
        url = reverse('accounts:test_email_send')
        self.assertEqual(url, '/accounts/email/testar-envio/')

        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, TestEmailSendView)

    def test_test_connection_url_resolves(self):
        """Testa se URL de teste de conexão resolve corretamente."""
        url = reverse('accounts:test_connection')
        self.assertEqual(url, '/accounts/email/testar-conexao/')

        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, TestConnectionView)
    
    def test_quick_email_setup_url_resolves(self):
        """Testa se URL de configuração rápida de email resolve corretamente."""
        url = reverse('accounts:quick_email_setup')
        self.assertEqual(url, '/accounts/email/configuracao-rapida/')
        
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, QuickEmailSetupView)
    
    def test_password_reset_test_url_resolves(self):
        """Testa se URL de teste de reset de senha resolve corretamente."""
        url = reverse('accounts:test_password_reset')
        self.assertEqual(url, '/accounts/email/testar-redefinicao/')

        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, PasswordResetTestView)


class URLPatternsTest(TestCase):
    """Testes para padrões de URL."""
    
    def test_all_account_urls_have_accounts_prefix(self):
        """Testa se todas as URLs do accounts têm o prefixo correto."""
        url_names = [
            'accounts:register',
            'accounts:verification',
            'accounts:login',
            'accounts:logout',
            'accounts:password_reset',
            'accounts:email_diagnostic',
            'accounts:test_email_send',
            'accounts:test_connection',
            'accounts:quick_email_setup',
            'accounts:test_password_reset',
        ]
        
        for url_name in url_names:
            url = reverse(url_name)
            self.assertTrue(url.startswith('/accounts/'), f"URL {url} should start with /accounts/")
    
    def test_profile_urls_require_slug_parameter(self):
        """Testa se URLs de perfil requerem parâmetro slug."""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        # URLs que não precisam de slug
        simple_url_names = [
            'accounts:profile',
            'accounts:settings',
            'accounts:remove_avatar',
        ]

        for url_name in simple_url_names:
            # Deve funcionar sem parâmetros
            url = reverse(url_name)
            self.assertIsNotNone(url)
    
    def test_password_reset_confirm_requires_slug_parameter(self):
        """Testa se URL de confirmação de reset requer parâmetro slug."""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        # Deve funcionar com slug
        url = reverse('accounts:password_reset_confirm', kwargs={'slug': user.slug})
        self.assertIsNotNone(url)
        
        # Deve falhar sem slug
        with self.assertRaises(Exception):
            reverse('accounts:password_reset_confirm')
    
    def test_url_names_are_consistent(self):
        """Testa se nomes de URL seguem padrão consistente."""
        # URLs que devem existir
        expected_urls = [
            'accounts:registration',
            'accounts:verification',
            'accounts:login',
            'accounts:logout',
            'accounts:password_reset_request',
            'accounts:password_reset_confirm',
            'accounts:profile',
            'accounts:profile_update',
            'accounts:remove_avatar',
            'accounts:email_diagnostic',
            'accounts:test_email_send',
            'accounts:test_connection',
            'accounts:quick_email_setup',
            'accounts:password_reset_test',
        ]
        
        for url_name in expected_urls:
            try:
                if 'profile' in url_name or 'password_reset_confirm' in url_name:
                    # URLs que precisam de slug
                    user = User.objects.create_user(
                        email=f'{url_name.replace(":", "_")}@example.com',
                        username=url_name.replace(':', '_'),
                        password='testpass123'
                    )
                    reverse(url_name, kwargs={'slug': user.slug})
                else:
                    reverse(url_name)
            except Exception as e:
                self.fail(f"URL {url_name} should exist and be reversible: {e}")


class URLAccessibilityTest(TestCase):
    """Testes para acessibilidade das URLs."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
    
    def test_public_urls_are_accessible(self):
        """Testa se URLs públicas são acessíveis."""
        public_urls = [
            reverse('accounts:registration'),
            reverse('accounts:login'),
            reverse('accounts:password_reset_request'),
        ]
        
        for url in public_urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, [200, 302], f"URL {url} should be accessible")
    
    def test_protected_urls_redirect_when_unauthenticated(self):
        """Testa se URLs protegidas redirecionam quando não autenticado."""
        protected_urls = [
            reverse('accounts:profile', kwargs={'slug': self.user.slug}),
            reverse('accounts:profile_update', kwargs={'slug': self.user.slug}),
            reverse('accounts:remove_avatar', kwargs={'slug': self.user.slug}),
        ]
        
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302, f"URL {url} should redirect unauthenticated users")
    
    def test_admin_urls_require_permissions(self):
        """Testa se URLs de admin requerem permissões."""
        admin_urls = [
            reverse('accounts:email_diagnostic'),
            reverse('accounts:test_email_send'),
            reverse('accounts:test_connection'),
        ]
        
        for url in admin_urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, [302, 403], f"URL {url} should require admin permissions")
    
    def test_logout_requires_post_method(self):
        """Testa se logout requer método POST."""
        # Login primeiro
        self.client.login(email='test@example.com', password='testpass123')
        
        logout_url = reverse('accounts:logout')
        
        # GET deve retornar método não permitido ou redirecionar
        get_response = self.client.get(logout_url)
        self.assertIn(get_response.status_code, [302, 405])
        
        # POST deve funcionar
        post_response = self.client.post(logout_url)
        self.assertEqual(post_response.status_code, 302)


class URLParameterValidationTest(TestCase):
    """Testes para validação de parâmetros de URL."""
    
    def test_profile_urls_with_invalid_slug(self):
        """Testa URLs de perfil com slug inválido."""
        invalid_slug = 'invalid-slug-that-does-not-exist'
        
        profile_urls = [
            reverse('accounts:profile', kwargs={'slug': invalid_slug}),
            reverse('accounts:profile_update', kwargs={'slug': invalid_slug}),
            reverse('accounts:remove_avatar', kwargs={'slug': invalid_slug}),
        ]
        
        for url in profile_urls:
            response = self.client.get(url)
            # Deve retornar 404 ou redirecionar
            self.assertIn(response.status_code, [404, 302], f"URL {url} with invalid slug should return 404 or redirect")
    
    def test_password_reset_confirm_with_invalid_slug(self):
        """Testa URL de confirmação de reset com slug inválido."""
        invalid_slug = 'invalid-slug-that-does-not-exist'
        
        url = reverse('accounts:password_reset_confirm', kwargs={'slug': invalid_slug})
        response = self.client.get(url)
        
        # Deve retornar 404 ou redirecionar
        self.assertIn(response.status_code, [404, 302])
    
    def test_profile_urls_with_valid_slug(self):
        """Testa URLs de perfil com slug válido."""
        user = User.objects.create_user(
            email='valid@example.com',
            username='validuser',
            password='testpass123'
        )
        
        # Login para acessar URLs protegidas
        self.client.login(email='valid@example.com', password='testpass123')
        
        profile_urls = [
            reverse('accounts:profile', kwargs={'slug': user.slug}),
            reverse('accounts:profile_update', kwargs={'slug': user.slug}),
        ]
        
        for url in profile_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"URL {url} with valid slug should be accessible")
