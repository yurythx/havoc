from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
import json

User = get_user_model()


class EmailConfiguration(models.Model):
    """Modelo para múltiplas configurações de email"""
    
    name = models.CharField(
        max_length=100,
        verbose_name='Nome da Configuração',
        help_text='Nome identificador para esta configuração (ex: Gmail Principal, Outlook Backup)'
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='Descrição',
        help_text='Descrição detalhada desta configuração'
    )
    
    # Configurações SMTP
    email_backend = models.CharField(
        max_length=200,
        default='django.core.mail.backends.smtp.EmailBackend',
        verbose_name='Backend de Email'
    )
    
    email_host = models.CharField(
        max_length=200,
        verbose_name='Servidor SMTP',
        help_text='Ex: smtp.gmail.com'
    )
    
    email_port = models.IntegerField(
        default=587,
        verbose_name='Porta SMTP',
        help_text='Geralmente 587 (TLS) ou 465 (SSL)'
    )
    
    email_host_user = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Usuário SMTP',
        help_text='Email ou username para autenticação'
    )

    email_host_password = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Senha SMTP',
        help_text='Senha ou senha de app'
    )
    
    email_use_tls = models.BooleanField(
        default=True,
        verbose_name='Usar TLS',
        help_text='Recomendado para a maioria dos servidores'
    )
    
    email_use_ssl = models.BooleanField(
        default=False,
        verbose_name='Usar SSL',
        help_text='Alternativa ao TLS'
    )
    
    default_from_email = models.EmailField(
        verbose_name='Email Remetente',
        help_text='Email que aparecerá como remetente'
    )
    
    email_timeout = models.IntegerField(
        default=30,
        verbose_name='Timeout (segundos)',
        help_text='Tempo limite para conexão'
    )
    
    # Configurações de controle
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo',
        help_text='Se esta configuração está disponível para uso'
    )
    
    is_default = models.BooleanField(
        default=False,
        verbose_name='Padrão',
        help_text='Se esta é a configuração padrão do sistema'
    )
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_configs_created'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_configs_updated'
    )
    
    # Estatísticas de uso
    last_tested_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Último Teste'
    )
    
    last_test_result = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Resultado do Último Teste'
    )
    
    emails_sent_count = models.IntegerField(
        default=0,
        verbose_name='Emails Enviados',
        help_text='Contador de emails enviados com esta configuração'
    )
    
    class Meta:
        verbose_name = 'Configuração de Email'
        verbose_name_plural = 'Configurações de Email'
        ordering = ['-is_default', '-is_active', 'name']
    
    def __str__(self):
        status = "🟢" if self.is_active else "🔴"
        default = " (Padrão)" if self.is_default else ""
        return f"{status} {self.name}{default}"
    
    def clean(self):
        """Validações customizadas"""
        # Validar que apenas uma configuração pode ser padrão
        if self.is_default:
            existing_default = EmailConfiguration.objects.filter(
                is_default=True
            ).exclude(pk=self.pk)
            
            if existing_default.exists():
                raise ValidationError(
                    'Já existe uma configuração padrão. '
                    'Desative a atual antes de definir uma nova.'
                )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_config_dict(self):
        """Retorna configuração como dicionário para uso no EmailService"""
        return {
            'EMAIL_BACKEND': self.email_backend,
            'EMAIL_HOST': self.email_host,
            'EMAIL_PORT': self.email_port,
            'EMAIL_HOST_USER': self.email_host_user,
            'EMAIL_HOST_PASSWORD': self.email_host_password,
            'EMAIL_USE_TLS': self.email_use_tls,
            'EMAIL_USE_SSL': self.email_use_ssl,
            'DEFAULT_FROM_EMAIL': self.default_from_email,
            'EMAIL_TIMEOUT': self.email_timeout,
        }
    
    def test_connection(self):
        """Testa a conexão com esta configuração"""
        from apps.accounts.services.email_service import EmailService
        
        # Criar EmailService temporário com esta configuração
        email_service = EmailService()
        email_service.config = self.get_config_dict()
        
        try:
            success, message = email_service.test_connection()
            
            # Salvar resultado do teste
            self.last_tested_at = timezone.now()
            self.last_test_result = {
                'success': success,
                'message': message,
                'tested_at': self.last_tested_at.isoformat()
            }
            self.save(update_fields=['last_tested_at', 'last_test_result'])

            return success, message

        except Exception as e:
            error_message = f'Erro no teste: {str(e)}'
            self.last_tested_at = timezone.now()
            self.last_test_result = {
                'success': False,
                'message': error_message,
                'tested_at': self.last_tested_at.isoformat()
            }
            self.save(update_fields=['last_tested_at', 'last_test_result'])
            
            return False, error_message
    
    def send_test_email(self, recipient_email, user_name=None):
        """Envia email de teste usando esta configuração"""
        from apps.accounts.services.email_service import EmailService
        
        email_service = EmailService()
        email_service.config = self.get_config_dict()
        
        try:
            success, message = email_service.send_test_email(recipient_email, user_name)
            
            if success:
                self.emails_sent_count += 1
                self.save(update_fields=['emails_sent_count'])
            
            return success, message
            
        except Exception as e:
            return False, f'Erro ao enviar email: {str(e)}'
    
    @classmethod
    def get_default(cls):
        """Retorna a configuração padrão"""
        try:
            return cls.objects.filter(is_default=True, is_active=True).first()
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_active_configs(cls):
        """Retorna todas as configurações ativas"""
        return cls.objects.filter(is_active=True)


class DatabaseConfiguration(models.Model):
    """Modelo para múltiplas configurações de banco de dados"""
    
    name = models.CharField(
        max_length=100,
        verbose_name='Nome da Configuração',
        help_text='Nome identificador (ex: PostgreSQL Principal, MySQL Backup)'
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='Descrição'
    )
    
    # Configurações do banco
    engine = models.CharField(
        max_length=200,
        verbose_name='Engine do Banco',
        choices=[
            ('django.db.backends.postgresql', 'PostgreSQL'),
            ('django.db.backends.mysql', 'MySQL'),
            ('django.db.backends.sqlite3', 'SQLite'),
            ('django.db.backends.oracle', 'Oracle'),
        ],
        default='django.db.backends.postgresql'
    )
    
    name_db = models.CharField(
        max_length=200,
        verbose_name='Nome do Banco',
        help_text='Nome da base de dados'
    )
    
    user = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Usuário',
        help_text='Usuário para conexão (não necessário para SQLite)'
    )
    
    password = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Senha',
        help_text='Senha do usuário'
    )
    
    host = models.CharField(
        max_length=200,
        blank=True,
        default='localhost',
        verbose_name='Host',
        help_text='Endereço do servidor'
    )
    
    port = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='Porta',
        help_text='Porta de conexão (deixe vazio para padrão)'
    )
    
    # Opções adicionais
    options = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Opções Adicionais',
        help_text='Configurações extras em formato JSON'
    )
    
    # Configurações de controle
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )
    
    is_default = models.BooleanField(
        default=False,
        verbose_name='Padrão'
    )
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='db_configs_created'
    )
    
    # Estatísticas
    last_tested_at = models.DateTimeField(null=True, blank=True)
    last_test_result = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = 'Configuração de Banco de Dados'
        verbose_name_plural = 'Configurações de Banco de Dados'
        ordering = ['-is_default', '-is_active', 'name']
    
    def __str__(self):
        status = "🟢" if self.is_active else "🔴"
        default = " (Padrão)" if self.is_default else ""
        return f"{status} {self.name}{default}"
    
    def clean(self):
        """Validações customizadas"""
        if self.is_default:
            existing_default = DatabaseConfiguration.objects.filter(
                is_default=True
            ).exclude(pk=self.pk)
            
            if existing_default.exists():
                raise ValidationError(
                    'Já existe uma configuração padrão de banco de dados.'
                )
    
    def get_config_dict(self):
        """Retorna configuração como dicionário Django"""
        config = {
            'ENGINE': self.engine,
            'NAME': self.name_db,
        }
        
        if self.user:
            config['USER'] = self.user
        if self.password:
            config['PASSWORD'] = self.password
        if self.host:
            config['HOST'] = self.host
        if self.port:
            config['PORT'] = self.port
        if self.options:
            config['OPTIONS'] = self.options
        
        return config
    
    def test_connection(self):
        """Testa a conexão com este banco"""
        from django.db.utils import DatabaseError
        import tempfile
        
        try:
            # Para SQLite, criar arquivo temporário se necessário
            if self.engine == 'django.db.backends.sqlite3':
                if not self.name_db or self.name_db == ':memory:':
                    # Usar arquivo temporário para teste
                    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
                        test_config = self.get_config_dict()
                        test_config['NAME'] = tmp.name
                else:
                    test_config = self.get_config_dict()
            else:
                test_config = self.get_config_dict()
            
            # Criar conexão temporária
            from django.db.backends.utils import load_backend

            backend = load_backend(test_config['ENGINE'])
            test_connection = backend.DatabaseWrapper(test_config, 'test_alias')

            # Tentar conectar
            test_connection.ensure_connection()

            # Testar uma query simples
            with test_connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()  # Apenas para verificar se funciona
            
            test_connection.close()
            
            success_message = f'Conexão bem-sucedida com {self.get_engine_display()}'
            
            # Salvar resultado
            self.last_tested_at = timezone.now()
            self.last_test_result = {
                'success': True,
                'message': success_message,
                'tested_at': self.last_tested_at.isoformat()
            }
            self.save(update_fields=['last_tested_at', 'last_test_result'])

            return True, success_message

        except DatabaseError as e:
            error_message = f'Erro de banco: {str(e)}'
        except Exception as e:
            error_message = f'Erro na conexão: {str(e)}'

        # Salvar erro
        self.last_tested_at = timezone.now()
        self.last_test_result = {
            'success': False,
            'message': error_message,
            'tested_at': self.last_tested_at.isoformat()
        }
        self.save(update_fields=['last_tested_at', 'last_test_result'])
        
        return False, error_message
    
    @classmethod
    def get_default(cls):
        """Retorna a configuração padrão"""
        return cls.objects.filter(is_default=True, is_active=True).first()
    
    @classmethod
    def get_active_configs(cls):
        """Retorna todas as configurações ativas"""
        return cls.objects.filter(is_active=True)
