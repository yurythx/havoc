"""
Testes para os templates do app accounts.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.template import Context, Template
from apps.accounts.models import VerificationCode

User = get_user_model()


class TemplateRenderingTest(TestCase):
    """Testes para renderização de templates."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User',
            is_verified=True
        )
    
    def test_login_template_renders_correctly(self):
        """Testa se template de login renderiza corretamente."""
        response = self.client.get(reverse('accounts:login'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        
        # Verifica elementos essenciais
        self.assertContains(response, 'Entrar')
        self.assertContains(response, 'form')
        self.assertContains(response, 'login')
        self.assertContains(response, 'password')
        self.assertContains(response, 'csrf')
    
    def test_registration_template_renders_correctly(self):
        """Testa se template de registro renderiza corretamente."""
        response = self.client.get(reverse('accounts:registration'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/registration.html')
        
        # Verifica elementos essenciais
        self.assertContains(response, 'Criar Conta')
        self.assertContains(response, 'form')
        self.assertContains(response, 'email')
        self.assertContains(response, 'username')
        self.assertContains(response, 'password1')
        self.assertContains(response, 'password2')
    
    def test_profile_template_renders_correctly(self):
        """Testa se template de perfil renderiza corretamente."""
        self.client.login(email='test@example.com', password='testpass123')
        
        response = self.client.get(reverse('accounts:profile', kwargs={'slug': self.user.slug}))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        
        # Verifica dados do usuário
        self.assertContains(response, 'Test User')
        self.assertContains(response, 'test@example.com')
        self.assertContains(response, 'testuser')
    
    def test_profile_update_template_renders_correctly(self):
        """Testa se template de edição de perfil renderiza corretamente."""
        self.client.login(email='test@example.com', password='testpass123')
        
        response = self.client.get(reverse('accounts:profile_update', kwargs={'slug': self.user.slug}))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile_update.html')
        
        # Verifica elementos do formulário
        self.assertContains(response, 'Editar Perfil')
        self.assertContains(response, 'first_name')
        self.assertContains(response, 'last_name')
        self.assertContains(response, 'bio')
    
    def test_verification_template_renders_correctly(self):
        """Testa se template de verificação renderiza corretamente."""
        # Simular sessão de registro
        session = self.client.session
        session['registration_email'] = 'test@example.com'
        session.save()
        
        response = self.client.get(reverse('accounts:verification'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/verification.html')
        
        # Verifica elementos essenciais
        self.assertContains(response, 'Verificação')
        self.assertContains(response, 'código')
        self.assertContains(response, 'form')
    
    def test_password_reset_request_template_renders_correctly(self):
        """Testa se template de solicitação de reset renderiza corretamente."""
        response = self.client.get(reverse('accounts:password_reset_request'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/password_reset_request.html')
        
        # Verifica elementos essenciais
        self.assertContains(response, 'Redefinir Senha')
        self.assertContains(response, 'email')
        self.assertContains(response, 'form')
    
    def test_password_reset_confirm_template_renders_correctly(self):
        """Testa se template de confirmação de reset renderiza corretamente."""
        response = self.client.get(reverse('accounts:password_reset_confirm', kwargs={'slug': self.user.slug}))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/password_reset_confirm.html')
        
        # Verifica elementos essenciais
        self.assertContains(response, 'Nova Senha')
        self.assertContains(response, 'code')
        self.assertContains(response, 'new_password1')
        self.assertContains(response, 'new_password2')


class TemplateContextTest(TestCase):
    """Testes para contexto dos templates."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User',
            bio='Test bio',
            phone='11999999999',
            location='São Paulo, SP',
            is_verified=True
        )
    
    def test_profile_template_context_contains_user_data(self):
        """Testa se contexto do template de perfil contém dados do usuário."""
        self.client.login(email='test@example.com', password='testpass123')
        
        response = self.client.get(reverse('accounts:profile', kwargs={'slug': self.user.slug}))
        
        # Verifica se dados do usuário estão no contexto
        self.assertEqual(response.context['user'], self.user)
        self.assertEqual(response.context['profile_user'], self.user)
        
        # Verifica se dados aparecem no template
        self.assertContains(response, 'Test bio')
        self.assertContains(response, '11999999999')
        self.assertContains(response, 'São Paulo, SP')
    
    def test_profile_update_template_context_contains_form(self):
        """Testa se contexto do template de edição contém formulário."""
        self.client.login(email='test@example.com', password='testpass123')
        
        response = self.client.get(reverse('accounts:profile_update', kwargs={'slug': self.user.slug}))
        
        # Verifica se formulário está no contexto
        self.assertIn('form', response.context)
        
        # Verifica se formulário tem dados do usuário
        form = response.context['form']
        self.assertEqual(form.instance, self.user)
        self.assertEqual(form.initial.get('first_name'), 'Test')
        self.assertEqual(form.initial.get('last_name'), 'User')
    
    def test_login_template_context_contains_form(self):
        """Testa se contexto do template de login contém formulário."""
        response = self.client.get(reverse('accounts:login'))
        
        # Verifica se formulário está no contexto
        self.assertIn('form', response.context)
        
        # Verifica tipo do formulário
        from apps.accounts.forms.authentication import FlexibleLoginForm
        self.assertIsInstance(response.context['form'], FlexibleLoginForm)
    
    def test_registration_template_context_contains_form(self):
        """Testa se contexto do template de registro contém formulário."""
        response = self.client.get(reverse('accounts:registration'))
        
        # Verifica se formulário está no contexto
        self.assertIn('form', response.context)
        
        # Verifica tipo do formulário
        from apps.accounts.forms.registration import RegistrationForm
        self.assertIsInstance(response.context['form'], RegistrationForm)


class TemplateInheritanceTest(TestCase):
    """Testes para herança de templates."""
    
    def test_templates_extend_base_template(self):
        """Testa se templates estendem template base."""
        templates_to_test = [
            'accounts/login.html',
            'accounts/registration.html',
            'accounts/profile.html',
            'accounts/profile_update.html',
            'accounts/verification.html',
            'accounts/password_reset_request.html',
            'accounts/password_reset_confirm.html',
        ]
        
        for template_name in templates_to_test:
            try:
                # Renderizar template com contexto mínimo
                rendered = render_to_string(template_name, {
                    'user': User(),
                    'form': type('MockForm', (), {'as_p': lambda: ''})(),
                    'profile_user': User(),
                })
                
                # Verificar se contém elementos do template base
                self.assertIn('<!DOCTYPE html>', rendered)
                self.assertIn('<html', rendered)
                self.assertIn('<head>', rendered)
                self.assertIn('<body>', rendered)
                
            except Exception as e:
                self.fail(f"Template {template_name} failed to render: {e}")


class TemplateFormRenderingTest(TestCase):
    """Testes para renderização de formulários nos templates."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.client = Client()
    
    def test_login_form_renders_with_crispy_forms(self):
        """Testa se formulário de login renderiza com crispy forms."""
        response = self.client.get(reverse('accounts:login'))
        
        # Verifica se usa crispy forms
        self.assertContains(response, 'crispy')
        self.assertContains(response, 'form-control')
        self.assertContains(response, 'btn')
    
    def test_registration_form_renders_with_crispy_forms(self):
        """Testa se formulário de registro renderiza com crispy forms."""
        response = self.client.get(reverse('accounts:registration'))
        
        # Verifica se usa crispy forms
        self.assertContains(response, 'crispy')
        self.assertContains(response, 'form-control')
        self.assertContains(response, 'btn')
        self.assertContains(response, 'row')
        self.assertContains(response, 'col-md-6')
    
    def test_form_errors_display_correctly(self):
        """Testa se erros de formulário são exibidos corretamente."""
        # Enviar dados inválidos para gerar erros
        response = self.client.post(reverse('accounts:login'), {
            'login': 'invalid@email.com',
            'password': 'wrongpassword'
        })
        
        # Verifica se erros são exibidos
        self.assertContains(response, 'erro')
        self.assertContains(response, 'inválidas')
    
    def test_form_success_messages_display_correctly(self):
        """Testa se mensagens de sucesso são exibidas corretamente."""
        # Criar usuário e fazer login
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            is_verified=True
        )
        
        response = self.client.post(reverse('accounts:login'), {
            'login': 'test@example.com',
            'password': 'testpass123'
        }, follow=True)
        
        # Verifica se há mensagens de sucesso
        messages = list(response.context['messages'])
        self.assertTrue(any('sucesso' in str(message).lower() or 'bem-vindo' in str(message).lower() for message in messages))


class TemplateAccessibilityTest(TestCase):
    """Testes para acessibilidade dos templates."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            is_verified=True
        )
    
    def test_templates_have_proper_labels(self):
        """Testa se templates têm labels adequados para acessibilidade."""
        response = self.client.get(reverse('accounts:login'))
        
        # Verifica se campos têm labels
        self.assertContains(response, '<label')
        self.assertContains(response, 'for=')
    
    def test_templates_have_proper_form_structure(self):
        """Testa se templates têm estrutura de formulário adequada."""
        response = self.client.get(reverse('accounts:registration'))
        
        # Verifica estrutura básica
        self.assertContains(response, '<form')
        self.assertContains(response, 'method="post"')
        self.assertContains(response, 'csrf')
        self.assertContains(response, '<button')
        self.assertContains(response, 'type="submit"')
    
    def test_profile_template_has_avatar_alt_text(self):
        """Testa se template de perfil tem texto alternativo para avatar."""
        self.client.login(email='test@example.com', password='testpass123')
        
        response = self.client.get(reverse('accounts:profile', kwargs={'slug': self.user.slug}))
        
        # Verifica se imagens têm alt text
        if 'img' in response.content.decode():
            self.assertContains(response, 'alt=')


class TemplateResponsivenessTest(TestCase):
    """Testes para responsividade dos templates."""
    
    def test_templates_use_bootstrap_classes(self):
        """Testa se templates usam classes Bootstrap para responsividade."""
        response = self.client.get(reverse('accounts:login'))
        
        # Verifica classes Bootstrap
        self.assertContains(response, 'container')
        self.assertContains(response, 'row')
        self.assertContains(response, 'col-')
    
    def test_forms_use_responsive_classes(self):
        """Testa se formulários usam classes responsivas."""
        response = self.client.get(reverse('accounts:registration'))
        
        # Verifica classes responsivas
        self.assertContains(response, 'col-md-')
        self.assertContains(response, 'form-control')
        self.assertContains(response, 'btn')
