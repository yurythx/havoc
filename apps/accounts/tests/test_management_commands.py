"""
Testes para os management commands do app accounts.
"""
from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from django.core import mail
from io import StringIO
import sys

User = get_user_model()


class CreateTestUsersCommandTest(TestCase):
    """Testes para o comando create_test_users."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.stdout = StringIO()
        self.stderr = StringIO()
    
    def test_create_test_users_default_behavior(self):
        """Testa comportamento padrão do comando."""
        # Executar comando
        call_command('create_test_users', stdout=self.stdout, stderr=self.stderr)
        
        # Verificar se usuários foram criados
        self.assertTrue(User.objects.filter(email='admin@havoc.local').exists())
        self.assertTrue(User.objects.filter(email='user@havoc.local').exists())
        self.assertTrue(User.objects.filter(email='editor@havoc.local').exists())
        
        # Verificar se admin é superusuário
        admin = User.objects.get(email='admin@havoc.local')
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)
        
        # Verificar se usuários comuns não são superusuários
        user = User.objects.get(email='user@havoc.local')
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        
        # Verificar output
        output = self.stdout.getvalue()
        self.assertIn('Usuários de teste criados com sucesso', output)
        self.assertIn('admin@havoc.local', output)
        self.assertIn('user@havoc.local', output)
        self.assertIn('editor@havoc.local', output)
    
    def test_create_test_users_with_custom_count(self):
        """Testa comando com número customizado de usuários."""
        # Executar comando com 5 usuários
        call_command('create_test_users', '--count', '5', stdout=self.stdout, stderr=self.stderr)
        
        # Verificar se 5 usuários foram criados (além dos padrão)
        total_users = User.objects.count()
        self.assertEqual(total_users, 8)  # 3 padrão + 5 customizados
        
        # Verificar se usuários customizados foram criados
        self.assertTrue(User.objects.filter(email='user1@havoc.local').exists())
        self.assertTrue(User.objects.filter(email='user5@havoc.local').exists())
    
    def test_create_test_users_with_custom_domain(self):
        """Testa comando com domínio customizado."""
        # Executar comando com domínio customizado
        call_command('create_test_users', '--domain', 'test.com', stdout=self.stdout, stderr=self.stderr)
        
        # Verificar se usuários foram criados com domínio correto
        self.assertTrue(User.objects.filter(email='admin@test.com').exists())
        self.assertTrue(User.objects.filter(email='user@test.com').exists())
        self.assertTrue(User.objects.filter(email='editor@test.com').exists())
    
    def test_create_test_users_skip_existing(self):
        """Testa se comando pula usuários existentes."""
        # Criar usuário admin primeiro
        User.objects.create_user(
            email='admin@havoc.local',
            username='admin',
            password='admin123'
        )
        
        # Executar comando
        call_command('create_test_users', stdout=self.stdout, stderr=self.stderr)
        
        # Verificar que apenas um admin existe
        admin_count = User.objects.filter(email='admin@havoc.local').count()
        self.assertEqual(admin_count, 1)
        
        # Verificar output
        output = self.stdout.getvalue()
        self.assertIn('já existe', output)
    
    def test_create_test_users_with_verified_flag(self):
        """Testa comando com flag de verificação."""
        # Executar comando com usuários verificados
        call_command('create_test_users', '--verified', stdout=self.stdout, stderr=self.stderr)
        
        # Verificar se usuários estão verificados
        admin = User.objects.get(email='admin@havoc.local')
        user = User.objects.get(email='user@havoc.local')
        
        self.assertTrue(admin.is_verified)
        self.assertTrue(user.is_verified)
    
    def test_create_test_users_without_verified_flag(self):
        """Testa comando sem flag de verificação."""
        # Executar comando sem verificação
        call_command('create_test_users', stdout=self.stdout, stderr=self.stderr)
        
        # Verificar se usuários não estão verificados
        admin = User.objects.get(email='admin@havoc.local')
        user = User.objects.get(email='user@havoc.local')
        
        self.assertFalse(admin.is_verified)
        self.assertFalse(user.is_verified)
    
    def test_create_test_users_invalid_count(self):
        """Testa comando com count inválido."""
        # Tentar executar com count negativo
        with self.assertRaises(CommandError):
            call_command('create_test_users', '--count', '-1', stdout=self.stdout, stderr=self.stderr)
        
        # Tentar executar com count muito alto
        with self.assertRaises(CommandError):
            call_command('create_test_users', '--count', '1000', stdout=self.stdout, stderr=self.stderr)
    
    def test_create_test_users_invalid_domain(self):
        """Testa comando com domínio inválido."""
        # Tentar executar com domínio inválido
        with self.assertRaises(CommandError):
            call_command('create_test_users', '--domain', 'invalid-domain', stdout=self.stdout, stderr=self.stderr)


class TestEmailCommandTest(TestCase):
    """Testes para o comando test_email."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.stdout = StringIO()
        self.stderr = StringIO()
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_test_email_default_behavior(self):
        """Testa comportamento padrão do comando de teste de email."""
        # Executar comando
        call_command('test_email', stdout=self.stdout, stderr=self.stderr)
        
        # Verificar se email foi enviado
        self.assertEqual(len(mail.outbox), 1)
        
        # Verificar conteúdo do email
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'Teste de Email - Sistema Havoc')
        self.assertIn('Este é um email de teste', email.body)
        self.assertEqual(email.to, ['admin@havoc.local'])
        
        # Verificar output
        output = self.stdout.getvalue()
        self.assertIn('Email de teste enviado com sucesso', output)
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_test_email_with_custom_recipient(self):
        """Testa comando com destinatário customizado."""
        # Executar comando com destinatário customizado
        call_command('test_email', '--to', 'custom@example.com', stdout=self.stdout, stderr=self.stderr)
        
        # Verificar se email foi enviado para destinatário correto
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ['custom@example.com'])
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_test_email_with_custom_subject(self):
        """Testa comando com assunto customizado."""
        # Executar comando com assunto customizado
        call_command('test_email', '--subject', 'Assunto Customizado', stdout=self.stdout, stderr=self.stderr)
        
        # Verificar se email foi enviado com assunto correto
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'Assunto Customizado')
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_test_email_with_html_flag(self):
        """Testa comando com flag HTML."""
        # Executar comando com HTML
        call_command('test_email', '--html', stdout=self.stdout, stderr=self.stderr)
        
        # Verificar se email foi enviado
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        
        # Verificar se tem conteúdo HTML
        self.assertIn('<html>', email.body)
        self.assertIn('<h1>', email.body)
        self.assertIn('<p>', email.body)
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_test_email_multiple_recipients(self):
        """Testa comando com múltiplos destinatários."""
        # Executar comando com múltiplos destinatários
        call_command(
            'test_email', 
            '--to', 'user1@example.com', 
            '--to', 'user2@example.com',
            stdout=self.stdout, 
            stderr=self.stderr
        )
        
        # Verificar se emails foram enviados
        self.assertEqual(len(mail.outbox), 2)
        
        recipients = [email.to[0] for email in mail.outbox]
        self.assertIn('user1@example.com', recipients)
        self.assertIn('user2@example.com', recipients)
    
    def test_test_email_invalid_recipient(self):
        """Testa comando com destinatário inválido."""
        # Tentar executar com email inválido
        with self.assertRaises(CommandError):
            call_command('test_email', '--to', 'invalid-email', stdout=self.stdout, stderr=self.stderr)
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.dummy.EmailBackend')
    def test_test_email_with_dummy_backend(self):
        """Testa comando com backend dummy."""
        # Executar comando
        call_command('test_email', stdout=self.stdout, stderr=self.stderr)
        
        # Verificar output (não deve haver erro)
        output = self.stdout.getvalue()
        self.assertIn('Email de teste enviado', output)
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend')
    def test_test_email_with_console_backend(self):
        """Testa comando com backend console."""
        # Capturar stdout original
        original_stdout = sys.stdout
        
        try:
            # Redirecionar stdout para capturar output do console backend
            sys.stdout = StringIO()
            
            # Executar comando
            call_command('test_email', stdout=self.stdout, stderr=self.stderr)
            
            # Verificar se email foi "enviado" para console
            console_output = sys.stdout.getvalue()
            self.assertIn('Content-Type: text/plain', console_output)
            self.assertIn('Subject: Teste de Email', console_output)
            
        finally:
            # Restaurar stdout original
            sys.stdout = original_stdout
    
    def test_test_email_with_connection_error(self):
        """Testa comando com erro de conexão."""
        # Configurar backend que vai falhar
        with override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend',
                             EMAIL_HOST='invalid-host',
                             EMAIL_PORT=587):
            
            # Executar comando (deve capturar erro)
            call_command('test_email', stdout=self.stdout, stderr=self.stderr)
            
            # Verificar se erro foi reportado
            error_output = self.stderr.getvalue()
            self.assertIn('Erro ao enviar email', error_output)


class CommandIntegrationTest(TestCase):
    """Testes de integração para management commands."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.stdout = StringIO()
        self.stderr = StringIO()
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_create_users_and_test_email_integration(self):
        """Testa integração entre criação de usuários e teste de email."""
        # Criar usuários de teste
        call_command('create_test_users', '--verified', stdout=self.stdout, stderr=self.stderr)
        
        # Verificar se admin foi criado
        admin = User.objects.get(email='admin@havoc.local')
        self.assertTrue(admin.is_verified)
        
        # Testar envio de email para admin
        call_command('test_email', '--to', 'admin@havoc.local', stdout=self.stdout, stderr=self.stderr)
        
        # Verificar se email foi enviado
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ['admin@havoc.local'])
    
    def test_commands_work_with_existing_data(self):
        """Testa se comandos funcionam com dados existentes."""
        # Criar alguns usuários manualmente
        User.objects.create_user(
            email='existing@example.com',
            username='existing',
            password='pass123'
        )
        
        # Executar comando de criação de usuários
        call_command('create_test_users', stdout=self.stdout, stderr=self.stderr)
        
        # Verificar que usuários de teste foram criados sem conflito
        self.assertTrue(User.objects.filter(email='admin@havoc.local').exists())
        self.assertTrue(User.objects.filter(email='existing@example.com').exists())
    
    def test_commands_handle_database_constraints(self):
        """Testa se comandos lidam com constraints de banco."""
        # Criar usuário com username que pode conflitar
        User.objects.create_user(
            email='different@example.com',
            username='admin',  # Mesmo username que será usado pelo comando
            password='pass123'
        )
        
        # Executar comando (deve lidar com conflito graciosamente)
        call_command('create_test_users', stdout=self.stdout, stderr=self.stderr)
        
        # Verificar que comando não falhou
        output = self.stdout.getvalue()
        self.assertIn('Usuários de teste criados', output)


class CommandHelpTest(TestCase):
    """Testes para help dos commands."""
    
    def test_create_test_users_help(self):
        """Testa help do comando create_test_users."""
        stdout = StringIO()
        
        # Executar comando com --help
        call_command('create_test_users', '--help', stdout=stdout)
        
        # Verificar se help contém informações importantes
        help_output = stdout.getvalue()
        self.assertIn('Cria usuários de teste', help_output)
        self.assertIn('--count', help_output)
        self.assertIn('--domain', help_output)
        self.assertIn('--verified', help_output)
    
    def test_test_email_help(self):
        """Testa help do comando test_email."""
        stdout = StringIO()
        
        # Executar comando com --help
        call_command('test_email', '--help', stdout=stdout)
        
        # Verificar se help contém informações importantes
        help_output = stdout.getvalue()
        self.assertIn('Envia um email de teste', help_output)
        self.assertIn('--to', help_output)
        self.assertIn('--subject', help_output)
        self.assertIn('--html', help_output)
