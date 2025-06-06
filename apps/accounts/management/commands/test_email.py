from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.services.email_service import EmailService
import random
import string

User = get_user_model()


class Command(BaseCommand):
    help = 'Testa o envio de emails do sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email de destino para o teste',
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['test', 'password_reset', 'registration'],
            default='test',
            help='Tipo de email para testar',
        )
        parser.add_argument(
            '--check-config',
            action='store_true',
            help='Apenas verificar configurações sem enviar email',
        )

    def handle(self, *args, **options):
        email_service = EmailService()
        
        self.stdout.write(self.style.SUCCESS('=== TESTE DE EMAIL HAVOC ===\n'))
        
        # Verificar configurações
        self.stdout.write('📋 Verificando configurações...')
        config_status = email_service.get_config_status()
        
        self.stdout.write(f'Backend: {config_status["backend"]}')
        self.stdout.write(f'Configurado: {"✅ Sim" if config_status["configured"] else "❌ Não"}')
        self.stdout.write(f'Pode enviar: {"✅ Sim" if config_status["can_send"] else "❌ Não"}')
        
        if config_status['issues']:
            self.stdout.write(self.style.WARNING('\n⚠️  Problemas encontrados:'))
            for issue in config_status['issues']:
                self.stdout.write(f'   • {issue}')
        
        # Se apenas verificar configurações
        if options['check_config']:
            return
        
        if not config_status['can_send']:
            self.stdout.write(self.style.ERROR('\n❌ Não é possível enviar emails. Configure primeiro.'))
            self.stdout.write('\nPara configurar:')
            self.stdout.write('1. Acesse /accounts/email/configuracao-rapida/')
            self.stdout.write('2. Ou use o painel de configurações em /config/email/')
            return
        
        # Testar conexão
        self.stdout.write('\n🔌 Testando conexão SMTP...')
        try:
            success, message = email_service.test_connection()
            if success:
                self.stdout.write(self.style.SUCCESS(f'✅ {message}'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ {message}'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro na conexão: {e}'))
            return
        
        # Determinar email de destino
        test_email = options.get('email')
        if not test_email:
            # Tentar usar email do primeiro superusuário
            try:
                superuser = User.objects.filter(is_superuser=True).first()
                if superuser and superuser.email:
                    test_email = superuser.email
                    self.stdout.write(f'📧 Usando email do superusuário: {test_email}')
                else:
                    self.stdout.write(self.style.ERROR('❌ Nenhum email especificado e nenhum superusuário com email encontrado.'))
                    self.stdout.write('Use: python manage.py test_email --email seu@email.com')
                    return
            except Exception:
                self.stdout.write(self.style.ERROR('❌ Especifique um email: python manage.py test_email --email seu@email.com'))
                return
        
        # Enviar email baseado no tipo
        email_type = options['type']
        self.stdout.write(f'\n📤 Enviando email de teste ({email_type}) para: {test_email}')
        
        try:
            if email_type == 'test':
                success, message = email_service.send_test_email(test_email, 'Usuário Teste')
                
            elif email_type == 'password_reset':
                # Gerar código de teste
                test_code = ''.join(random.choices(string.digits, k=6))
                self.stdout.write(f'🔑 Código gerado: {test_code}')
                success = email_service.send_password_reset_code(test_email, test_code)
                message = f'Código de redefinição enviado: {test_code}' if success else 'Falha ao enviar código'
                
            elif email_type == 'registration':
                # Gerar código de teste
                test_code = ''.join(random.choices(string.digits, k=6))
                self.stdout.write(f'🔑 Código gerado: {test_code}')
                success = email_service.send_registration_confirmation(test_email, test_code)
                message = f'Código de confirmação enviado: {test_code}' if success else 'Falha ao enviar código'
            
            if success:
                self.stdout.write(self.style.SUCCESS(f'✅ {message}'))
                self.stdout.write('\n📬 Verifique sua caixa de entrada!')
                
                # Mostrar informações adicionais
                if email_service.config['EMAIL_BACKEND'] == 'django.core.mail.backends.console.EmailBackend':
                    self.stdout.write(self.style.WARNING('\n⚠️  Backend de console ativo - email aparecerá no terminal do servidor'))
                
            else:
                self.stdout.write(self.style.ERROR(f'❌ {message}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao enviar email: {e}'))
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write('💡 Dicas:')
        self.stdout.write('• Para configurar email: /accounts/email/configuracao-rapida/')
        self.stdout.write('• Para diagnóstico completo: /accounts/email/diagnostico/')
        self.stdout.write('• Para testar redefinição de senha: python manage.py test_email --type password_reset')
        self.stdout.write('• Para verificar apenas config: python manage.py test_email --check-config')
