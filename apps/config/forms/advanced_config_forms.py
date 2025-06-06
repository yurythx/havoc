from django import forms
from django.core.validators import MinLengthValidator
from django.conf import settings
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, Reset, HTML, Div
from crispy_forms.bootstrap import FormActions
from apps.config.models import SystemConfiguration
from apps.config.services.system_config_service import SystemConfigService
from apps.config.repositories.config_repository import DjangoSystemConfigRepository, DjangoAuditLogRepository
import json
import os


class DatabaseConfigForm(forms.Form):
    """Formulário para configurações de banco de dados"""
    
    # Configurações principais
    engine = forms.ChoiceField(
        label='Engine do Banco',
        choices=[
            ('django.db.backends.postgresql', 'PostgreSQL'),
            ('django.db.backends.mysql', 'MySQL'),
            ('django.db.backends.sqlite3', 'SQLite'),
            ('django.db.backends.oracle', 'Oracle'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    name = forms.CharField(
        label='Nome do Banco',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'nome_do_banco'
        })
    )
    
    user = forms.CharField(
        label='Usuário',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'usuario_db'
        })
    )
    
    password = forms.CharField(
        label='Senha',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••'
        })
    )
    
    host = forms.CharField(
        label='Host',
        max_length=100,
        required=False,
        initial='localhost',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'localhost'
        })
    )
    
    port = forms.CharField(
        label='Porta',
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '5432'
        })
    )
    
    # Opções avançadas
    conn_max_age = forms.IntegerField(
        label='Tempo de Vida da Conexão (segundos)',
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0'
        })
    )
    
    atomic_requests = forms.BooleanField(
        label='Requisições Atômicas',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    autocommit = forms.BooleanField(
        label='Auto Commit',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Carrega configurações atuais
        self.load_current_config()
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.attrs = {'novalidate': ''}
        
        self.helper.layout = Layout(
            Fieldset(
                'Configurações Principais do Banco de Dados',
                Row(
                    Column('engine', css_class='col-md-6'),
                    Column('name', css_class='col-md-6'),
                ),
                Row(
                    Column('user', css_class='col-md-6'),
                    Column('password', css_class='col-md-6'),
                ),
                Row(
                    Column('host', css_class='col-md-6'),
                    Column('port', css_class='col-md-6'),
                ),
                css_class='mb-4'
            ),
            
            Fieldset(
                'Configurações Avançadas',
                Row(
                    Column('conn_max_age', css_class='col-md-4'),
                    Column('atomic_requests', css_class='col-md-4'),
                    Column('autocommit', css_class='col-md-4'),
                ),
                css_class='mb-4'
            ),
            
            HTML('''
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Atenção:</strong> Alterar as configurações do banco de dados pode afetar o funcionamento do sistema. 
                    Certifique-se de que as configurações estão corretas antes de salvar.
                </div>
            '''),
            
            FormActions(
                Submit('submit', 'Salvar Configurações', css_class='btn btn-primary btn-lg'),
                Reset('reset', 'Restaurar', css_class='btn btn-outline-secondary btn-lg'),
                HTML('<a href="{% url \'config:system_config\' %}" class="btn btn-outline-danger btn-lg">Cancelar</a>'),
                css_class='d-flex justify-content-between'
            )
        )

    def load_current_config(self):
        """Carrega configurações atuais do banco"""
        try:
            from apps.config.services.system_config_service import AuditLogService
            config_service = SystemConfigService(
                DjangoSystemConfigRepository(),
                AuditLogService(DjangoAuditLogRepository())
            )
            
            db_config = config_service.get_config('database_settings')
            if db_config and isinstance(db_config, dict):
                for field_name, value in db_config.items():
                    if field_name in self.fields:
                        self.fields[field_name].initial = value
        except:
            # Se não existir configuração, usa valores padrão
            pass

    def save(self, user=None):
        """Salva as configurações do banco de dados"""
        if not self.is_valid():
            return False

        try:
            from apps.config.services.system_config_service import AuditLogService
            config_service = SystemConfigService(
                DjangoSystemConfigRepository(),
                AuditLogService(DjangoAuditLogRepository())
            )
            
            db_config = {
                'ENGINE': self.cleaned_data['engine'],
                'NAME': self.cleaned_data['name'],
                'USER': self.cleaned_data.get('user', ''),
                'PASSWORD': self.cleaned_data.get('password', ''),
                'HOST': self.cleaned_data.get('host', 'localhost'),
                'PORT': self.cleaned_data.get('port', ''),
                'OPTIONS': {
                    'CONN_MAX_AGE': self.cleaned_data.get('conn_max_age', 0),
                    'ATOMIC_REQUESTS': self.cleaned_data.get('atomic_requests', False),
                    'AUTOCOMMIT': self.cleaned_data.get('autocommit', True),
                }
            }
            
            return config_service.set_config(
                key='database_settings',
                value=db_config,
                description='Configurações do banco de dados',
                updated_by=user
            )
        except Exception as e:
            self.add_error(None, f'Erro ao salvar configurações: {str(e)}')
            return False


class EmailConfigForm(forms.Form):
    """Formulário para configurações de email"""
    
    # Configurações SMTP
    email_backend = forms.ChoiceField(
        label='Backend de Email',
        choices=[
            ('django.core.mail.backends.smtp.EmailBackend', 'SMTP'),
            ('django.core.mail.backends.console.EmailBackend', 'Console (Debug)'),
            ('django.core.mail.backends.filebased.EmailBackend', 'Arquivo'),
            ('django.core.mail.backends.locmem.EmailBackend', 'Memória (Teste)'),
            ('django.core.mail.backends.dummy.EmailBackend', 'Dummy (Desabilitado)'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    email_host = forms.CharField(
        label='Servidor SMTP',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'smtp.gmail.com'
        })
    )
    
    email_port = forms.IntegerField(
        label='Porta SMTP',
        initial=587,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '65535'
        })
    )
    
    email_host_user = forms.CharField(
        label='Usuário SMTP',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu-email@gmail.com'
        })
    )
    
    email_host_password = forms.CharField(
        label='Senha SMTP',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••'
        })
    )
    
    email_use_tls = forms.BooleanField(
        label='Usar TLS',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    email_use_ssl = forms.BooleanField(
        label='Usar SSL',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Configurações de envio
    default_from_email = forms.EmailField(
        label='Email Padrão de Envio',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'noreply@seusite.com'
        })
    )
    
    server_email = forms.EmailField(
        label='Email do Servidor',
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'admin@seusite.com'
        })
    )
    
    email_timeout = forms.IntegerField(
        label='Timeout (segundos)',
        required=False,
        initial=30,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Carrega configurações atuais
        self.load_current_config()
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.attrs = {'novalidate': ''}
        
        self.helper.layout = Layout(
            Fieldset(
                'Configurações do Servidor SMTP',
                'email_backend',
                Row(
                    Column('email_host', css_class='col-md-8'),
                    Column('email_port', css_class='col-md-4'),
                ),
                Row(
                    Column('email_host_user', css_class='col-md-6'),
                    Column('email_host_password', css_class='col-md-6'),
                ),
                Row(
                    Column('email_use_tls', css_class='col-md-4'),
                    Column('email_use_ssl', css_class='col-md-4'),
                    Column('email_timeout', css_class='col-md-4'),
                ),
                css_class='mb-4'
            ),
            
            Fieldset(
                'Configurações de Envio',
                Row(
                    Column('default_from_email', css_class='col-md-6'),
                    Column('server_email', css_class='col-md-6'),
                ),
                css_class='mb-4'
            ),
            
            HTML('''
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    <strong>Dica:</strong> Para Gmail, use smtp.gmail.com na porta 587 com TLS ativado. 
                    Você pode precisar gerar uma senha de app específica.
                </div>
            '''),
            
            FormActions(
                Submit('submit', 'Salvar Configurações', css_class='btn btn-primary btn-lg'),
                Submit('test', 'Testar Configurações', css_class='btn btn-outline-info btn-lg'),
                Reset('reset', 'Restaurar', css_class='btn btn-outline-secondary btn-lg'),
                css_class='d-flex justify-content-between'
            )
        )

    def load_current_config(self):
        """Carrega configurações atuais de email"""
        try:
            from apps.config.services.system_config_service import AuditLogService
            config_service = SystemConfigService(
                DjangoSystemConfigRepository(),
                AuditLogService(DjangoAuditLogRepository())
            )
            
            email_config = config_service.get_config('email_settings')
            if email_config and isinstance(email_config, dict):
                for field_name, value in email_config.items():
                    if field_name in self.fields:
                        self.fields[field_name].initial = value
        except:
            pass

    def save(self, user=None):
        """Salva as configurações de email"""
        if not self.is_valid():
            return False

        try:
            from apps.config.services.system_config_service import AuditLogService
            config_service = SystemConfigService(
                DjangoSystemConfigRepository(),
                AuditLogService(DjangoAuditLogRepository())
            )
            
            email_config = {
                'EMAIL_BACKEND': self.cleaned_data['email_backend'],
                'EMAIL_HOST': self.cleaned_data['email_host'],
                'EMAIL_PORT': self.cleaned_data['email_port'],
                'EMAIL_HOST_USER': self.cleaned_data['email_host_user'],
                'EMAIL_HOST_PASSWORD': self.cleaned_data['email_host_password'],
                'EMAIL_USE_TLS': self.cleaned_data['email_use_tls'],
                'EMAIL_USE_SSL': self.cleaned_data['email_use_ssl'],
                'DEFAULT_FROM_EMAIL': self.cleaned_data['default_from_email'],
                'SERVER_EMAIL': self.cleaned_data.get('server_email', ''),
                'EMAIL_TIMEOUT': self.cleaned_data.get('email_timeout', 30),
            }
            
            return config_service.set_config(
                key='email_settings',
                value=email_config,
                description='Configurações de email SMTP',
                updated_by=user
            )
        except Exception as e:
            self.add_error(None, f'Erro ao salvar configurações: {str(e)}')
            return False

    def test_connection(self):
        """Testa a conexão SMTP"""
        if not self.is_valid():
            return False, "Formulário inválido"
            
        try:
            from django.core.mail import get_connection
            from django.core.mail import EmailMessage
            
            # Cria conexão temporária com as configurações
            connection = get_connection(
                backend=self.cleaned_data['email_backend'],
                host=self.cleaned_data['email_host'],
                port=self.cleaned_data['email_port'],
                username=self.cleaned_data['email_host_user'],
                password=self.cleaned_data['email_host_password'],
                use_tls=self.cleaned_data['email_use_tls'],
                use_ssl=self.cleaned_data['email_use_ssl'],
                timeout=self.cleaned_data.get('email_timeout', 30),
            )
            
            # Testa a conexão
            connection.open()
            connection.close()
            
            return True, "Conexão SMTP testada com sucesso!"
            
        except Exception as e:
            return False, f"Erro na conexão SMTP: {str(e)}"


class EnvironmentVariablesForm(forms.Form):
    """Formulário para gerenciar variáveis de ambiente"""

    # Variáveis principais do Django
    secret_key = forms.CharField(
        label='SECRET_KEY',
        max_length=255,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Chave secreta do Django'
        })
    )

    debug = forms.BooleanField(
        label='DEBUG',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    allowed_hosts = forms.CharField(
        label='ALLOWED_HOSTS',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'localhost,127.0.0.1,seudominio.com (um por linha)'
        })
    )

    # Configurações de segurança
    secure_ssl_redirect = forms.BooleanField(
        label='SECURE_SSL_REDIRECT',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    secure_hsts_seconds = forms.IntegerField(
        label='SECURE_HSTS_SECONDS',
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0'
        })
    )

    session_cookie_secure = forms.BooleanField(
        label='SESSION_COOKIE_SECURE',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    csrf_cookie_secure = forms.BooleanField(
        label='CSRF_COOKIE_SECURE',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    # Configurações de cache
    cache_backend = forms.ChoiceField(
        label='CACHE_BACKEND',
        choices=[
            ('django.core.cache.backends.dummy.DummyCache', 'Dummy (Desabilitado)'),
            ('django.core.cache.backends.locmem.LocMemCache', 'Memória Local'),
            ('django.core.cache.backends.filebased.FileBasedCache', 'Arquivo'),
            ('django.core.cache.backends.redis.RedisCache', 'Redis'),
            ('django.core.cache.backends.memcached.PyMemcacheCache', 'Memcached'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    cache_location = forms.CharField(
        label='CACHE_LOCATION',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'redis://127.0.0.1:6379/1'
        })
    )

    # Configurações de logging
    log_level = forms.ChoiceField(
        label='LOG_LEVEL',
        choices=[
            ('DEBUG', 'DEBUG'),
            ('INFO', 'INFO'),
            ('WARNING', 'WARNING'),
            ('ERROR', 'ERROR'),
            ('CRITICAL', 'CRITICAL'),
        ],
        initial='INFO',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # Variáveis customizadas
    custom_variables = forms.CharField(
        label='Variáveis Customizadas',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 8,
            'placeholder': 'VARIAVEL_1=valor1\nVARIAVEL_2=valor2\n# Comentários começam com #'
        }),
        help_text='Uma variável por linha no formato NOME=valor'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Carrega configurações atuais
        self.load_current_config()

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.attrs = {'novalidate': ''}

        self.helper.layout = Layout(
            Fieldset(
                'Configurações Principais do Django',
                'secret_key',
                Row(
                    Column('debug', css_class='col-md-6'),
                    Column('log_level', css_class='col-md-6'),
                ),
                'allowed_hosts',
                css_class='mb-4'
            ),

            Fieldset(
                'Configurações de Segurança',
                Row(
                    Column('secure_ssl_redirect', css_class='col-md-6'),
                    Column('secure_hsts_seconds', css_class='col-md-6'),
                ),
                Row(
                    Column('session_cookie_secure', css_class='col-md-6'),
                    Column('csrf_cookie_secure', css_class='col-md-6'),
                ),
                css_class='mb-4'
            ),

            Fieldset(
                'Configurações de Cache',
                Row(
                    Column('cache_backend', css_class='col-md-6'),
                    Column('cache_location', css_class='col-md-6'),
                ),
                css_class='mb-4'
            ),

            Fieldset(
                'Variáveis Customizadas',
                'custom_variables',
                HTML('''
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i>
                        <strong>Formato:</strong> Uma variável por linha no formato NOME=valor.
                        Linhas começando com # são comentários.
                    </div>
                '''),
                css_class='mb-4'
            ),

            HTML('''
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Atenção:</strong> Alterar variáveis de ambiente pode afetar gravemente o funcionamento do sistema.
                    Faça backup antes de alterar e teste em ambiente de desenvolvimento primeiro.
                </div>
            '''),

            FormActions(
                Submit('submit', 'Salvar Variáveis', css_class='btn btn-primary btn-lg'),
                Submit('generate_key', 'Gerar Nova SECRET_KEY', css_class='btn btn-outline-warning btn-lg'),
                Reset('reset', 'Restaurar', css_class='btn btn-outline-secondary btn-lg'),
                css_class='d-flex justify-content-between'
            )
        )

    def load_current_config(self):
        """Carrega configurações atuais das variáveis de ambiente"""
        try:
            from apps.config.services.system_config_service import AuditLogService
            config_service = SystemConfigService(
                DjangoSystemConfigRepository(),
                AuditLogService(DjangoAuditLogRepository())
            )

            env_config = config_service.get_config('environment_variables')
            if env_config and isinstance(env_config, dict):
                for field_name, value in env_config.items():
                    if field_name in self.fields:
                        if field_name == 'allowed_hosts' and isinstance(value, list):
                            self.fields[field_name].initial = '\n'.join(value)
                        elif field_name == 'custom_variables' and isinstance(value, dict):
                            custom_vars = []
                            for k, v in value.items():
                                custom_vars.append(f'{k}={v}')
                            self.fields[field_name].initial = '\n'.join(custom_vars)
                        else:
                            self.fields[field_name].initial = value
        except:
            # Carrega valores atuais do settings se não existir configuração
            self.fields['secret_key'].initial = getattr(settings, 'SECRET_KEY', '')[:10] + '...'
            self.fields['debug'].initial = getattr(settings, 'DEBUG', False)
            self.fields['allowed_hosts'].initial = '\n'.join(getattr(settings, 'ALLOWED_HOSTS', []))

    def clean_custom_variables(self):
        """Valida variáveis customizadas"""
        custom_vars = self.cleaned_data.get('custom_variables', '')

        if not custom_vars:
            return {}

        variables = {}
        lines = custom_vars.strip().split('\n')

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if '=' not in line:
                raise forms.ValidationError(f'Linha {i}: Formato inválido. Use NOME=valor')

            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()

            if not key:
                raise forms.ValidationError(f'Linha {i}: Nome da variável não pode estar vazio')

            variables[key] = value

        return variables

    def clean_allowed_hosts(self):
        """Valida hosts permitidos"""
        hosts = self.cleaned_data.get('allowed_hosts', '')

        if not hosts:
            return []

        host_list = []
        for host in hosts.split('\n'):
            host = host.strip()
            if host:
                host_list.append(host)

        return host_list

    def save(self, user=None):
        """Salva as variáveis de ambiente"""
        if not self.is_valid():
            return False

        try:
            from apps.config.services.system_config_service import AuditLogService
            config_service = SystemConfigService(
                DjangoSystemConfigRepository(),
                AuditLogService(DjangoAuditLogRepository())
            )

            env_config = {
                'SECRET_KEY': self.cleaned_data['secret_key'],
                'DEBUG': self.cleaned_data['debug'],
                'ALLOWED_HOSTS': self.cleaned_data['allowed_hosts'],
                'SECURE_SSL_REDIRECT': self.cleaned_data['secure_ssl_redirect'],
                'SECURE_HSTS_SECONDS': self.cleaned_data['secure_hsts_seconds'],
                'SESSION_COOKIE_SECURE': self.cleaned_data['session_cookie_secure'],
                'CSRF_COOKIE_SECURE': self.cleaned_data['csrf_cookie_secure'],
                'CACHE_BACKEND': self.cleaned_data.get('cache_backend', ''),
                'CACHE_LOCATION': self.cleaned_data.get('cache_location', ''),
                'LOG_LEVEL': self.cleaned_data['log_level'],
                'custom_variables': self.cleaned_data['custom_variables'],
            }

            return config_service.set_config(
                key='environment_variables',
                value=env_config,
                description='Variáveis de ambiente do sistema',
                updated_by=user
            )
        except Exception as e:
            self.add_error(None, f'Erro ao salvar variáveis: {str(e)}')
            return False

    def generate_secret_key(self):
        """Gera uma nova SECRET_KEY"""
        from django.core.management.utils import get_random_secret_key
        return get_random_secret_key()
