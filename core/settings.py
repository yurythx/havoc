"""
Django settings for Havoc CMS.

Configurações otimizadas para desenvolvimento e produção.
Utiliza variáveis de ambiente para máxima flexibilidade e segurança.

Documentação: https://docs.djangoproject.com/en/5.2/topics/settings/
"""

from pathlib import Path
import os
import logging
import sys
from typing import List, Dict, Any

# Importações condicionais
try:
    from dotenv import load_dotenv
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False

try:
    import dj_database_url
    HAS_DJ_DATABASE_URL = True
except ImportError:
    HAS_DJ_DATABASE_URL = False

# =============================================================================
# CONFIGURAÇÕES DE DIRETÓRIO E AMBIENTE
# =============================================================================

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file (apenas se disponível)
if HAS_DOTENV:
    env_file = BASE_DIR / '.env'
    if env_file.exists():
        load_dotenv(env_file)

# Detectar ambiente automaticamente
def get_environment() -> str:
    """Detecta o ambiente baseado em variáveis e contexto"""
    if 'pytest' in sys.modules or 'test' in sys.argv:
        return 'testing'

    env = os.environ.get('ENVIRONMENT', '').lower()
    if env in ['production', 'prod']:
        return 'production'
    elif env in ['staging', 'stage']:
        return 'staging'
    elif env in ['development', 'dev']:
        return 'development'

    # Auto-detectar baseado em outras variáveis
    if os.environ.get('DYNO') or os.environ.get('HEROKU_APP_NAME'):
        return 'production'  # Heroku
    elif os.environ.get('KUBERNETES_SERVICE_HOST'):
        return 'production'  # Kubernetes
    elif os.environ.get('DOCKER_CONTAINER'):
        return 'production'  # Docker em produção

    return 'development'  # Padrão

ENVIRONMENT = get_environment()


# =============================================================================
# CONFIGURAÇÕES BÁSICAS DO DJANGO
# =============================================================================

def get_secret_key() -> str:
    """Gera ou obtém a SECRET_KEY de forma segura"""
    secret_key = os.environ.get('DJANGO_SECRET_KEY')

    if not secret_key:
        if ENVIRONMENT == 'production':
            raise ValueError(
                "DJANGO_SECRET_KEY é obrigatória em produção! "
                "Configure a variável de ambiente."
            )
        # Gerar chave temporária para desenvolvimento
        import secrets
        secret_key = secrets.token_urlsafe(50)
        print(f"⚠️  Usando SECRET_KEY temporária para desenvolvimento")

    return secret_key

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_secret_key()

# SECURITY WARNING: don't run with debug turned on in production!
def get_debug_setting() -> bool:
    """Determina DEBUG baseado no ambiente"""
    if ENVIRONMENT == 'production':
        return False
    elif ENVIRONMENT == 'testing':
        return False

    # Para desenvolvimento, permitir override via variável
    return os.environ.get('DEBUG', 'True').lower() == 'true'

DEBUG = get_debug_setting()

# Hosts permitidos com validação
def get_allowed_hosts() -> List[str]:
    """Configura ALLOWED_HOSTS baseado no ambiente"""
    hosts_env = os.environ.get('ALLOWED_HOSTS', '')

    if ENVIRONMENT == 'production':
        if not hosts_env or hosts_env == '*':
            raise ValueError(
                "ALLOWED_HOSTS deve ser configurado especificamente em produção! "
                "Não use '*' em produção."
            )
        return [host.strip() for host in hosts_env.split(',') if host.strip()]

    # Desenvolvimento: hosts padrão + configurados
    default_hosts = ['localhost', '127.0.0.1', 'testserver']
    if hosts_env:
        configured_hosts = [host.strip() for host in hosts_env.split(',') if host.strip()]
        return list(set(default_hosts + configured_hosts))

    return default_hosts

ALLOWED_HOSTS = get_allowed_hosts()


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'crispy_forms',
    'crispy_bootstrap5',
    'tinymce',

    # Local apps
    'apps.accounts',
    'apps.config',
    'apps.pages',
    'apps.articles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.accounts.middleware.RateLimitMiddleware',
    'apps.accounts.middleware.AccessControlMiddleware',
    'apps.accounts.middleware.SmartRedirectMiddleware',
    'apps.config.middleware.module_middleware.ModuleAccessMiddleware',
    'apps.config.middleware.module_middleware.ModuleContextMiddleware',
]

# Adicionar WhiteNoise apenas em produção E apenas se não for DEBUG
if not DEBUG and ENVIRONMENT == 'production':
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# Configurações de Autenticação
AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Backends de Autenticação
AUTHENTICATION_BACKENDS = [
    'apps.accounts.backends.EmailOrUsernameModelBackend',  # Backend principal
    'django.contrib.auth.backends.ModelBackend',  # Backend padrão como fallback
]

# =============================================================================
# CONFIGURAÇÕES DE EMAIL
# =============================================================================

# Configurações dinâmicas de email baseadas em variáveis de ambiente
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_TIMEOUT = int(os.environ.get('EMAIL_TIMEOUT', '30'))
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@havoc.com')
CONTACT_EMAIL = os.environ.get('CONTACT_EMAIL', 'contato@havoc.com')

WSGI_APPLICATION = 'core.wsgi.application'


# =============================================================================
# CONFIGURAÇÕES DE BANCO DE DADOS
# =============================================================================

def get_database_config() -> Dict[str, Any]:
    """Configura banco de dados baseado em variáveis de ambiente"""

    # Debug opcional para troubleshooting
    debug_db = os.environ.get('DEBUG_DATABASE', 'False').lower() == 'true'
    if debug_db:
        print(f"🔍 DEBUG: Todas as variáveis DATABASE:")
        for key, value in os.environ.items():
            if 'DATABASE' in key.upper():
                print(f"   {key}: {value}")
        print(f"🔍 HAS_DJ_DATABASE_URL: {HAS_DJ_DATABASE_URL}")

    # Tentar usar DATABASE_URL primeiro (padrão para deploy)
    database_url = os.environ.get('DATABASE_URL', '').strip()

    if debug_db:
        print(f"🔍 DATABASE_URL: '{database_url}' (length: {len(database_url)})")

    if database_url and database_url != '' and HAS_DJ_DATABASE_URL:
        try:
            if debug_db:
                print(f"🔄 Tentando parsear DATABASE_URL...")

            config = dj_database_url.parse(database_url)

            # Adicionar configurações extras para PostgreSQL
            if 'postgresql' in config.get('ENGINE', ''):
                config.update({
                    'CONN_MAX_AGE': int(os.environ.get('DB_CONN_MAX_AGE', '60')),
                    'OPTIONS': {
                        'connect_timeout': 10,
                        'options': '-c default_transaction_isolation=read_committed'
                    }
                })

            if debug_db:
                print(f"✅ Usando DATABASE_URL: {config.get('ENGINE', 'unknown')}")

            return {'default': config}
        except Exception as e:
            if debug_db:
                print(f"❌ Erro ao parsear DATABASE_URL: {e}")
            # Continuar para configuração manual

    # Configuração manual baseada em ENGINE
    engine = os.environ.get('DATABASE_ENGINE', 'sqlite').lower().strip()

    if debug_db:
        print(f"✅ Usando configuração manual: {engine}")

    if engine == 'postgresql':
        config = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.environ.get('DATABASE_NAME', 'havoc'),
                'USER': os.environ.get('DATABASE_USER', 'havoc_user'),
                'PASSWORD': os.environ.get('DATABASE_PASSWORD', ''),
                'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
                'PORT': os.environ.get('DATABASE_PORT', '5432'),
                'CONN_MAX_AGE': int(os.environ.get('DB_CONN_MAX_AGE', '60')),
                'OPTIONS': {
                    'connect_timeout': 10,
                    'options': '-c default_transaction_isolation=read_committed'
                },
                'TEST': {
                    'NAME': f"test_{os.environ.get('DATABASE_NAME', 'havoc')}",
                }
            }
        }
        if debug_db:
            print(f"✅ PostgreSQL configurado")
        return config

    elif engine == 'mysql':
        config = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': os.environ.get('DATABASE_NAME', 'havoc'),
                'USER': os.environ.get('DATABASE_USER', 'havoc_user'),
                'PASSWORD': os.environ.get('DATABASE_PASSWORD', ''),
                'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
                'PORT': os.environ.get('DATABASE_PORT', '3306'),
                'CONN_MAX_AGE': int(os.environ.get('DB_CONN_MAX_AGE', '60')),
                'OPTIONS': {
                    'charset': 'utf8mb4',
                    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                },
                'TEST': {
                    'NAME': f"test_{os.environ.get('DATABASE_NAME', 'havoc')}",
                    'CHARSET': 'utf8mb4',
                }
            }
        }
        if debug_db:
            print(f"✅ MySQL configurado")
        return config

    else:  # SQLite (padrão para desenvolvimento)
        db_name = os.environ.get('DATABASE_NAME', 'db.sqlite3')
        db_path = BASE_DIR / db_name

        config = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': db_path,
                'OPTIONS': {
                    'timeout': 20,
                    'check_same_thread': False,
                },
                'TEST': {
                    'NAME': ':memory:' if ENVIRONMENT == 'testing' else None,
                }
            }
        }
        if debug_db:
            print(f"✅ SQLite configurado: {db_path}")
        return config

# Configuração dinâmica de banco de dados
DATABASES = get_database_config()





# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Static files finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# WhiteNoise configuration (apenas em produção)
if not DEBUG and ENVIRONMENT == 'production':
    WHITENOISE_USE_FINDERS = True
    WHITENOISE_AUTOREFRESH = False

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Storage Configuration (Django 4.2+)
# SEMPRE usar storage simples em desenvolvimento
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Use WhiteNoise storage apenas em produção E apenas se não for DEBUG
if not DEBUG and ENVIRONMENT == 'production':
    STORAGES["staticfiles"]["BACKEND"] = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# CONFIGURAÇÕES DE SEGURANÇA
# =============================================================================

def get_security_settings() -> Dict[str, Any]:
    """Configura settings de segurança baseado no ambiente"""

    # Configurações básicas sempre ativas
    settings = {
        'SECURE_BROWSER_XSS_FILTER': True,
        'SECURE_CONTENT_TYPE_NOSNIFF': True,
        'X_FRAME_OPTIONS': 'DENY',
        'SECURE_REFERRER_POLICY': 'strict-origin-when-cross-origin',
        'SECURE_CROSS_ORIGIN_OPENER_POLICY': 'same-origin',
    }

    # Configurações específicas por ambiente
    if ENVIRONMENT == 'production':
        settings.update({
            'SECURE_SSL_REDIRECT': True,
            'SECURE_HSTS_SECONDS': 31536000,  # 1 ano
            'SECURE_HSTS_INCLUDE_SUBDOMAINS': True,
            'SECURE_HSTS_PRELOAD': True,
            'SECURE_PROXY_SSL_HEADER': ('HTTP_X_FORWARDED_PROTO', 'https'),
            'SESSION_COOKIE_SECURE': True,
            'CSRF_COOKIE_SECURE': True,
        })
    else:
        # Desenvolvimento: permitir override via variáveis
        settings.update({
            'SECURE_SSL_REDIRECT': os.environ.get('SECURE_SSL_REDIRECT', 'False').lower() == 'true',
            'SECURE_HSTS_SECONDS': int(os.environ.get('SECURE_HSTS_SECONDS', '0')),
            'SECURE_HSTS_INCLUDE_SUBDOMAINS': os.environ.get('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'False').lower() == 'true',
            'SECURE_HSTS_PRELOAD': os.environ.get('SECURE_HSTS_PRELOAD', 'False').lower() == 'true',
            'SESSION_COOKIE_SECURE': os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true',
            'CSRF_COOKIE_SECURE': os.environ.get('CSRF_COOKIE_SECURE', 'False').lower() == 'true',
        })

    return settings

# Aplicar configurações de segurança
security_settings = get_security_settings()
for key, value in security_settings.items():
    globals()[key] = value

# Configurações de Sessão e Cookies
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = int(os.environ.get('SESSION_COOKIE_AGE', '86400'))  # 24 horas padrão
SESSION_EXPIRE_AT_BROWSER_CLOSE = os.environ.get('SESSION_EXPIRE_AT_BROWSER_CLOSE', 'False').lower() == 'true'
SESSION_SAVE_EVERY_REQUEST = False
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

# CSRF Settings
CSRF_COOKIE_AGE = 31449600  # 1 ano
CSRF_USE_SESSIONS = False

def get_csrf_trusted_origins() -> List[str]:
    """Configura CSRF_TRUSTED_ORIGINS baseado no ambiente"""
    origins_env = os.environ.get('CSRF_TRUSTED_ORIGINS', '')

    if not origins_env:
        if ENVIRONMENT == 'production':
            return []  # Deve ser configurado explicitamente em produção
        else:
            return ['http://127.0.0.1:8000', 'http://localhost:8000']

    return [origin.strip() for origin in origins_env.split(',') if origin.strip()]

CSRF_TRUSTED_ORIGINS = get_csrf_trusted_origins()

# Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# =============================================================================
# CONFIGURAÇÕES DE CACHE E PERFORMANCE
# =============================================================================

# Configuração dinâmica de cache
CACHE_BACKEND = os.environ.get('CACHE_BACKEND', 'django.core.cache.backends.locmem.LocMemCache')
CACHE_LOCATION = os.environ.get('CACHE_LOCATION', 'unique-snowflake')

if 'redis' in CACHE_BACKEND.lower():
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': CACHE_BACKEND,
            'LOCATION': CACHE_LOCATION,
        }
    }

# Configurações de Rate Limiting
RATELIMIT_ENABLE = os.environ.get('RATELIMIT_ENABLE', 'True').lower() == 'true'
RATELIMIT_USE_CACHE = os.environ.get('RATELIMIT_USE_CACHE', 'default')



# Crispy Forms Configuration
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Form rendering
CRISPY_FAIL_SILENTLY = not DEBUG

# =============================================================================
# CONFIGURAÇÕES DE LOGGING
# =============================================================================

# Nível de log baseado em variável de ambiente
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG' if DEBUG else 'INFO')
LOG_FILE = os.environ.get('LOG_FILE', '')

# Configuração de logging
# Configuração dinâmica de handlers baseada em variáveis de ambiente
handlers = {
    'console': {
        'level': LOG_LEVEL,
        'class': 'logging.StreamHandler',
        'formatter': 'simple',
    },
}

# Adiciona handler de arquivo se especificado
if LOG_FILE:
    handlers['file'] = {
        'level': LOG_LEVEL,
        'class': 'logging.FileHandler',
        'filename': LOG_FILE,
        'formatter': 'verbose',
    }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': handlers,
    'root': {
        'handlers': list(handlers.keys()),
    },
    'loggers': {
        'django': {
            'handlers': list(handlers.keys()),
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': list(handlers.keys()),
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
}

# =============================================================================
# CONFIGURAÇÕES DE ARQUIVOS E MÍDIA
# =============================================================================

# Configurações de upload baseadas em variáveis de ambiente
def get_upload_size() -> int:
    """Parse seguro do tamanho máximo de upload"""
    size_str = os.environ.get('MAX_UPLOAD_SIZE', '5242880')
    # Remove comentários e espaços
    size_str = size_str.split('#')[0].strip()
    try:
        return int(size_str)
    except ValueError:
        return 5242880  # 5MB padrão

MAX_UPLOAD_SIZE = get_upload_size()
FILE_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_SIZE
DATA_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_SIZE
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# Extensões permitidas (baseadas em variáveis de ambiente)
def get_allowed_extensions(env_var: str, default: str) -> List[str]:
    """Parse seguro de extensões permitidas"""
    extensions_str = os.environ.get(env_var, default)
    # Remove comentários e espaços
    extensions_str = extensions_str.split('#')[0].strip()
    return [ext.strip() for ext in extensions_str.split(',') if ext.strip()]

ALLOWED_IMAGE_EXTENSIONS = get_allowed_extensions('ALLOWED_IMAGE_EXTENSIONS', '.jpg,.jpeg,.png,.gif,.webp')
ALLOWED_DOCUMENT_EXTENSIONS = get_allowed_extensions('ALLOWED_DOCUMENT_EXTENSIONS', '.pdf,.doc,.docx,.txt')

# =============================================================================
# CONFIGURAÇÕES DO SITE E PAGINAÇÃO
# =============================================================================

# Configurações de paginação baseadas em variáveis de ambiente
PAGINATE_BY = int(os.environ.get('PAGINATE_BY', '12'))
ARTICLES_PER_PAGE = int(os.environ.get('ARTICLES_PER_PAGE', '12'))
USERS_PER_PAGE = int(os.environ.get('USERS_PER_PAGE', '20'))

# Informações do site
SITE_NAME = os.environ.get('SITE_NAME', 'Havoc')
SITE_DESCRIPTION = os.environ.get('SITE_DESCRIPTION', 'Sistema de gerenciamento de conteúdo moderno')
SITE_URL = os.environ.get('SITE_URL', 'http://127.0.0.1:8000')

# =============================================================================
# REDES SOCIAIS E ANALYTICS
# =============================================================================

# Redes sociais
SOCIAL_MEDIA = {
    'facebook': os.environ.get('FACEBOOK_URL', ''),
    'twitter': os.environ.get('TWITTER_URL', ''),
    'linkedin': os.environ.get('LINKEDIN_URL', ''),
    'github': os.environ.get('GITHUB_URL', ''),
}

# Analytics e tracking
GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID', '')
GOOGLE_TAG_MANAGER_ID = os.environ.get('GOOGLE_TAG_MANAGER_ID', '')
FACEBOOK_PIXEL_ID = os.environ.get('FACEBOOK_PIXEL_ID', '')

# =============================================================================
# CONFIGURAÇÕES PERSONALIZADAS DO HAVOC
# =============================================================================

# Módulos ativos do sistema
ACTIVE_MODULES = os.environ.get('ACTIVE_MODULES', 'accounts,config,pages,articles').split(',')

# Configurações de tema e localização
DEFAULT_THEME = os.environ.get('DEFAULT_THEME', 'light')
DEFAULT_LANGUAGE = os.environ.get('DEFAULT_LANGUAGE', 'pt-br')
DEFAULT_TIMEZONE = os.environ.get('DEFAULT_TIMEZONE', 'America/Sao_Paulo')

# Configurações de backup
BACKUP_DIR = os.environ.get('BACKUP_DIR', 'backups')
BACKUP_RETENTION_DAYS = int(os.environ.get('BACKUP_RETENTION_DAYS', '30'))

# Configurações de monitoramento
SENTRY_DSN = os.environ.get('SENTRY_DSN', '')
HEALTH_CHECK_ENABLED = os.environ.get('HEALTH_CHECK_ENABLED', 'True').lower() == 'true'

# Configurações de desenvolvimento
DJANGO_DEBUG_TOOLBAR = os.environ.get('DJANGO_DEBUG_TOOLBAR', 'False').lower() == 'true'
SHOW_SQL_QUERIES = os.environ.get('SHOW_SQL_QUERIES', 'False').lower() == 'true'

# =============================================================================
# CONFIGURAÇÕES CONDICIONAIS BASEADAS NO AMBIENTE
# =============================================================================

# Configurações específicas para produção
if ENVIRONMENT == 'production':
    # Força HTTPS em produção
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 ano
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Cookies seguros em produção
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Log level mais restritivo em produção
    if not os.environ.get('LOG_LEVEL'):
        LOG_LEVEL = 'WARNING'

# Configurações específicas para desenvolvimento
elif ENVIRONMENT == 'development':
    # Debug toolbar se habilitado
    if DJANGO_DEBUG_TOOLBAR:
        INSTALLED_APPS.append('debug_toolbar')
        MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
        INTERNAL_IPS = ['127.0.0.1', 'localhost']

    # Mostrar queries SQL se habilitado
    if SHOW_SQL_QUERIES:
        LOGGING['loggers']['django.db.backends'] = {
            'level': 'DEBUG',
            'handlers': list(handlers.keys()),
            'propagate': False,
        }

# Configuração do Sentry para monitoramento de erros
if SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration

        sentry_logging = LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR
        )

        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[DjangoIntegration(), sentry_logging],
            traces_sample_rate=0.1,
            send_default_pii=True,
            environment=ENVIRONMENT,
        )
    except ImportError:
        pass  # Sentry não instalado

# =============================================================================
# CONFIGURAÇÕES DO TINYMCE
# =============================================================================

TINYMCE_DEFAULT_CONFIG = {
    'height': 500,
    'width': '100%',
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 20,
    'theme': 'silver',
    'plugins': '''
        advlist autolink lists link image charmap preview anchor
        searchreplace visualblocks code insertdatetime media
        table wordcount emoticons nonbreaking directionality
    ''',
    'toolbar1': '''
        undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect |
        alignleft aligncenter alignright alignjustify | outdent indent | numlist bullist |
        forecolor backcolor removeformat | charmap emoticons
    ''',
    'toolbar2': '''
        visualblocks visualchars | nonbreaking anchor | link unlink | image media |
        table | code | customfullscreen | preview | help
    ''',
    'menubar': True,
    'statusbar': True,
    'branding': False,
    'promotion': False,
    'content_css': '/static/css/tinymce-content.css',
    'contextmenu': 'link image table',
    'directionality': 'ltr',
    'language': 'pt_BR',
    'paste_data_images': True,
    'paste_as_text': False,
    'paste_auto_cleanup_on_paste': True,
    'paste_remove_styles': False,
    'paste_remove_styles_if_webkit': False,
    'paste_strip_class_attributes': 'none',
    'fullscreen_native': True,
    'resize': False,
    'elementpath': False,
    'toolbar_mode': 'sliding',
    'toolbar_sticky': True,
}

# Configurações específicas para diferentes campos
TINYMCE_CONFIGS = {
    'default': TINYMCE_DEFAULT_CONFIG,
    'simple': {
        'height': 200,
        'width': '100%',
        'plugins': 'link lists textcolor',
        'toolbar': 'bold italic underline | bullist numlist | link | forecolor',
        'menubar': False,
        'statusbar': False,
        'branding': False,
        'promotion': False,
    },
    'advanced': {
        'height': 600,
        'width': '100%',
        'plugins': '''
            advlist autolink lists link image charmap preview anchor
            searchreplace visualblocks code insertdatetime media
            table wordcount emoticons nonbreaking directionality codesample
        ''',
        'toolbar1': '''
            undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect |
            alignleft aligncenter alignright alignjustify | outdent indent | numlist bullist |
            forecolor backcolor removeformat | charmap emoticons
        ''',
        'toolbar2': '''
            visualblocks visualchars | nonbreaking anchor | link unlink | image media |
            table | codesample code | customfullscreen | preview | help
        ''',
        'menubar': True,
        'statusbar': True,
        'branding': False,
        'promotion': False,
        'content_css': '/static/css/tinymce-content.css',
        'contextmenu': 'link image table',
        'directionality': 'ltr',
        'language': 'pt_BR',
        'paste_data_images': True,
        'fullscreen_native': True,
        'resize': False,
        'elementpath': False,
        'toolbar_mode': 'sliding',
        'toolbar_sticky': True,
        'codesample_languages': [
            {'text': 'HTML/XML', 'value': 'markup'},
            {'text': 'JavaScript', 'value': 'javascript'},
            {'text': 'CSS', 'value': 'css'},
            {'text': 'PHP', 'value': 'php'},
            {'text': 'Python', 'value': 'python'},
            {'text': 'Java', 'value': 'java'},
            {'text': 'C', 'value': 'c'},
            {'text': 'C#', 'value': 'csharp'},
            {'text': 'C++', 'value': 'cpp'},
        ],
    }
}
