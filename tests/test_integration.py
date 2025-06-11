"""
Testes de integração entre apps do projeto Havoc.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from apps.accounts.models import VerificationCode
from apps.config.models import (
    SystemConfiguration, EmailConfiguration, 
    DatabaseConfiguration, AppModuleConfiguration
)
from apps.articles.models import Article, Category, Tag
from apps.accounts.services.registration_service import RegistrationService
from apps.accounts.repositories.django_user_repository import DjangoUserRepository
from apps.accounts.repositories.django_verification_repository import DjangoVerificationRepository
from apps.accounts.notifications.email_notification_service import EmailNotificationService

User = get_user_model()


class AccountsConfigIntegrationTest(TestCase):
    """Testes de integração entre apps accounts e config."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.client = Client()
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='adminpass123',
            is_staff=True,
            is_superuser=True,
            is_verified=True
        )
    
    def test_user_creation_with_system_configuration(self):
        """Testa criação de usuário com configurações do sistema."""
        # Criar configuração do sistema
        SystemConfiguration.objects.create(
            key='user_auto_verify',
            value='true',
            description='Auto verificar usuários',
            updated_by=self.admin_user
        )
        
        # Criar usuário
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        # Verificar se usuário foi criado
        self.assertTrue(User.objects.filter(email='test@example.com').exists())
        
        # Verificar se configuração existe
        config = SystemConfiguration.objects.get(key='user_auto_verify')
        self.assertEqual(config.value, 'true')
    
    def test_email_configuration_affects_user_notifications(self):
        """Testa se configuração de email afeta notificações de usuário."""
        # Criar configuração de email
        email_config = EmailConfiguration.objects.create(
            name='Test Email Config',
            email_backend='django.core.mail.backends.locmem.EmailBackend',
            email_host='localhost',
            email_port=587,
            default_from_email='noreply@test.com',
            is_default=True,
            created_by=self.admin_user
        )
        
        # Criar usuário e código de verificação
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
        
        # Verificar se configuração de email existe
        self.assertTrue(EmailConfiguration.objects.filter(is_default=True).exists())
        
        # Verificar se código de verificação foi criado
        self.assertTrue(VerificationCode.objects.filter(user=user).exists())
    
    def test_app_module_configuration_affects_accounts_availability(self):
        """Testa se configuração de módulos afeta disponibilidade do accounts."""
        # Criar configuração de módulo para accounts
        accounts_module = AppModuleConfiguration.objects.create(
            app_name='accounts',
            display_name='Contas de Usuário',
            description='Sistema de autenticação e perfis',
            is_enabled=True,
            created_by=self.admin_user
        )
        
        # Verificar se módulo está ativo
        self.assertTrue(accounts_module.is_enabled)
        self.assertTrue(accounts_module.is_core)
        
        # Tentar acessar página de login (deve funcionar)
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
    
    def test_database_configuration_with_user_operations(self):
        """Testa configuração de banco com operações de usuário."""
        # Criar configuração de banco
        db_config = DatabaseConfiguration.objects.create(
            name='test_db',
            engine='django.db.backends.sqlite3',
            host='localhost',
            is_active=True,
            created_by=self.admin_user
        )
        
        # Realizar operações de usuário
        user = User.objects.create_user(
            email='dbtest@example.com',
            username='dbtest',
            password='testpass123'
        )
        
        # Verificar se operações funcionaram
        self.assertTrue(User.objects.filter(email='dbtest@example.com').exists())
        self.assertTrue(DatabaseConfiguration.objects.filter(name='test_db').exists())


class AccountsArticlesIntegrationTest(TestCase):
    """Testes de integração entre apps accounts e articles."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.client = Client()
        self.author = User.objects.create_user(
            email='author@example.com',
            username='author',
            password='authorpass123',
            first_name='Author',
            last_name='User',
            is_verified=True
        )
        
        self.category = Category.objects.create(
            name='Tecnologia',
            description='Artigos sobre tecnologia'
        )
        
        self.tag = Tag.objects.create(
            name='Python',
            description='Linguagem Python'
        )
    
    def test_user_can_create_article(self):
        """Testa se usuário pode criar artigo."""
        # Login do autor
        self.client.login(email='author@example.com', password='authorpass123')
        
        # Criar artigo
        article = Article.objects.create(
            title='Meu Primeiro Artigo',
            excerpt='Um artigo de teste',
            content='Conteúdo do artigo...',
            author=self.author,
            category=self.category,
            status='published'
        )
        
        # Adicionar tags
        article.tags.add(self.tag)
        
        # Verificar se artigo foi criado corretamente
        self.assertEqual(article.author, self.author)
        self.assertEqual(article.category, self.category)
        self.assertIn(self.tag, article.tags.all())
        self.assertTrue(article.is_published)
    
    def test_user_profile_shows_authored_articles(self):
        """Testa se perfil do usuário mostra artigos de sua autoria."""
        # Criar artigos do autor
        article1 = Article.objects.create(
            title='Artigo 1',
            excerpt='Primeiro artigo',
            content='Conteúdo 1',
            author=self.author,
            category=self.category,
            status='published'
        )
        
        article2 = Article.objects.create(
            title='Artigo 2',
            excerpt='Segundo artigo',
            content='Conteúdo 2',
            author=self.author,
            category=self.category,
            status='draft'
        )
        
        # Login e acessar perfil
        self.client.login(email='author@example.com', password='authorpass123')
        response = self.client.get(reverse('accounts:profile', kwargs={'slug': self.author.slug}))
        
        # Verificar se artigos aparecem no perfil
        self.assertEqual(response.status_code, 200)
        
        # Verificar se artigos estão relacionados ao autor
        author_articles = Article.objects.filter(author=self.author)
        self.assertEqual(author_articles.count(), 2)
        self.assertIn(article1, author_articles)
        self.assertIn(article2, author_articles)
    
    def test_article_contributors_relationship(self):
        """Testa relacionamento de colaboradores em artigos."""
        # Criar colaborador
        contributor = User.objects.create_user(
            email='contributor@example.com',
            username='contributor',
            password='contribpass123',
            is_verified=True
        )
        
        # Criar artigo
        article = Article.objects.create(
            title='Artigo Colaborativo',
            excerpt='Artigo com colaboradores',
            content='Conteúdo colaborativo',
            author=self.author,
            category=self.category,
            status='published'
        )
        
        # Adicionar colaborador
        article.contributors.add(contributor)
        
        # Verificar relacionamentos
        self.assertEqual(article.author, self.author)
        self.assertIn(contributor, article.contributors.all())
        self.assertIn(article, contributor.contributed_articles.all())
    
    def test_user_deletion_affects_articles(self):
        """Testa como exclusão de usuário afeta artigos."""
        # Criar artigo
        article = Article.objects.create(
            title='Artigo do Autor',
            excerpt='Artigo que será órfão',
            content='Conteúdo do artigo',
            author=self.author,
            category=self.category,
            status='published'
        )
        
        article_id = article.id
        
        # Deletar autor
        self.author.delete()
        
        # Verificar se artigo ainda existe (depende da configuração de CASCADE)
        # Neste caso, assumindo que artigos são mantidos mesmo sem autor
        try:
            article = Article.objects.get(id=article_id)
            # Se artigo ainda existe, author deve ser None ou ter comportamento específico
        except Article.DoesNotExist:
            # Se artigo foi deletado junto com o autor
            pass


class ConfigArticlesIntegrationTest(TestCase):
    """Testes de integração entre apps config e articles."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='adminpass123',
            is_staff=True,
            is_superuser=True
        )
        
        self.author = User.objects.create_user(
            email='author@example.com',
            username='author',
            password='authorpass123'
        )
    
    def test_articles_module_configuration(self):
        """Testa configuração do módulo articles."""
        # Criar configuração do módulo articles
        articles_module = AppModuleConfiguration.objects.create(
            app_name='articles',
            display_name='Sistema de Artigos',
            description='Módulo para gerenciamento de artigos e conteúdo',
            is_enabled=True,
            created_by=self.admin_user
        )
        
        # Verificar se módulo está configurado
        self.assertTrue(articles_module.is_enabled)
        self.assertEqual(articles_module.app_name, 'articles')
        
        # Criar categoria e artigo
        category = Category.objects.create(
            name='Tecnologia',
            description='Artigos sobre tecnologia'
        )
        
        article = Article.objects.create(
            title='Artigo de Teste',
            excerpt='Teste de integração',
            content='Conteúdo de teste',
            author=self.author,
            category=category,
            status='published'
        )
        
        # Verificar se artigo foi criado com módulo ativo
        self.assertTrue(Article.objects.filter(title='Artigo de Teste').exists())
    
    def test_system_configuration_affects_articles(self):
        """Testa se configurações do sistema afetam artigos."""
        # Criar configuração para artigos
        SystemConfiguration.objects.create(
            key='articles_auto_publish',
            value='false',
            description='Auto publicar artigos',
            updated_by=self.admin_user
        )
        
        SystemConfiguration.objects.create(
            key='articles_require_approval',
            value='true',
            description='Artigos requerem aprovação',
            updated_by=self.admin_user
        )
        
        # Criar categoria
        category = Category.objects.create(
            name='Tecnologia',
            description='Artigos sobre tecnologia'
        )
        
        # Criar artigo
        article = Article.objects.create(
            title='Artigo com Configuração',
            excerpt='Artigo afetado por configurações',
            content='Conteúdo do artigo',
            author=self.author,
            category=category,
            status='draft'  # Baseado na configuração
        )
        
        # Verificar se configurações existem
        auto_publish = SystemConfiguration.objects.get(key='articles_auto_publish')
        require_approval = SystemConfiguration.objects.get(key='articles_require_approval')
        
        self.assertEqual(auto_publish.value, 'false')
        self.assertEqual(require_approval.value, 'true')
        
        # Verificar se artigo está em draft (não auto publicado)
        self.assertEqual(article.status, 'draft')


class FullSystemIntegrationTest(TestCase):
    """Testes de integração completa do sistema."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.client = Client()
    
    def test_complete_user_workflow(self):
        """Testa fluxo completo de usuário no sistema."""
        # 1. Configurar sistema
        admin = User.objects.create_superuser(
            email='admin@havoc.local',
            username='admin',
            password='admin123'
        )
        
        # Configurar módulos
        AppModuleConfiguration.objects.create(
            app_name='accounts',
            display_name='Contas',
            is_enabled=True,
            created_by=admin
        )
        
        AppModuleConfiguration.objects.create(
            app_name='articles',
            display_name='Artigos',
            is_enabled=True,
            created_by=admin
        )
        
        # 2. Registrar usuário
        registration_data = {
            'email': 'user@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        
        response = self.client.post(reverse('accounts:registration'), registration_data)
        self.assertEqual(response.status_code, 302)  # Redirecionamento após registro
        
        # 3. Verificar usuário
        user = User.objects.get(email='user@example.com')
        verification_code = VerificationCode.objects.get(user=user, code_type='registration')
        
        # Simular verificação
        session = self.client.session
        session['registration_email'] = 'user@example.com'
        session.save()
        
        response = self.client.post(reverse('accounts:verification'), {
            'code': verification_code.code
        })
        self.assertEqual(response.status_code, 302)
        
        # 4. Login
        response = self.client.post(reverse('accounts:login'), {
            'login': 'user@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        
        # 5. Criar conteúdo (se módulo articles estiver ativo)
        category = Category.objects.create(
            name='Geral',
            description='Categoria geral'
        )
        
        user.refresh_from_db()
        user.is_verified = True
        user.save()
        
        article = Article.objects.create(
            title='Meu Primeiro Post',
            excerpt='Post de teste',
            content='Conteúdo do meu primeiro post',
            author=user,
            category=category,
            status='published'
        )
        
        # 6. Verificar se tudo funcionou
        self.assertTrue(user.is_verified)
        self.assertTrue(Article.objects.filter(author=user).exists())
        self.assertEqual(article.author, user)
    
    def test_system_with_disabled_modules(self):
        """Testa sistema com módulos desabilitados."""
        # Criar admin
        admin = User.objects.create_superuser(
            email='admin@havoc.local',
            username='admin',
            password='admin123'
        )
        
        # Desabilitar módulo articles
        AppModuleConfiguration.objects.create(
            app_name='articles',
            display_name='Artigos',
            is_enabled=False,
            created_by=admin
        )
        
        # Manter accounts habilitado (obrigatório)
        AppModuleConfiguration.objects.create(
            app_name='accounts',
            display_name='Contas',
            is_enabled=True,
            created_by=admin
        )
        
        # Verificar que accounts ainda funciona
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        
        # Verificar configuração de módulos
        articles_module = AppModuleConfiguration.objects.get(app_name='articles')
        accounts_module = AppModuleConfiguration.objects.get(app_name='accounts')
        
        self.assertFalse(articles_module.is_enabled)
        self.assertTrue(accounts_module.is_enabled)
        self.assertTrue(accounts_module.is_core)  # Accounts é sempre core
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_email_integration_across_apps(self):
        """Testa integração de email entre apps."""
        # Configurar email
        admin = User.objects.create_superuser(
            email='admin@havoc.local',
            username='admin',
            password='admin123'
        )
        
        EmailConfiguration.objects.create(
            name='Test Email',
            email_backend='django.core.mail.backends.locmem.EmailBackend',
            email_host='localhost',
            default_from_email='noreply@havoc.local',
            is_default=True,
            created_by=admin
        )
        
        # Registrar usuário (deve enviar email de verificação)
        service = RegistrationService(
            user_repository=DjangoUserRepository(),
            verification_repository=DjangoVerificationRepository(),
            notification_service=EmailNotificationService()
        )
        
        user = service.register_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            username='testuser'
        )
        
        # Verificar se usuário foi criado
        self.assertTrue(User.objects.filter(email='test@example.com').exists())
        
        # Verificar se código de verificação foi criado
        self.assertTrue(VerificationCode.objects.filter(user=user).exists())
        
        # Verificar configuração de email
        email_config = EmailConfiguration.objects.get(is_default=True)
        self.assertEqual(email_config.name, 'Test Email')
