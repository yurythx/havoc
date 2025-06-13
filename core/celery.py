"""
Configuração do Celery para o projeto Havoc
"""

import os
from celery import Celery
from django.conf import settings

# Definir configurações padrão do Django para o programa 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('havoc')

# Usar string aqui significa que o worker não precisa serializar
# o objeto de configuração para processos filhos.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Carregar módulos de tarefas de todas as apps Django registradas
app.autodiscover_tasks()

# Configurações específicas do Celery
app.conf.update(
    # Configurações de broker
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    
    # Configurações de resultado
    result_expires=3600,  # 1 hora
    
    # Configurações de worker
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # Configurações de roteamento
    task_routes={
        'apps.articles.tasks.*': {'queue': 'articles'},
        'apps.accounts.tasks.*': {'queue': 'accounts'},
        'apps.config.tasks.*': {'queue': 'config'},
    },
    
    # Configurações de agendamento
    beat_schedule={
        'cleanup-expired-sessions': {
            'task': 'apps.accounts.tasks.cleanup_expired_sessions',
            'schedule': 3600.0,  # A cada hora
        },
        'generate-sitemap': {
            'task': 'apps.articles.tasks.generate_sitemap',
            'schedule': 86400.0,  # Diariamente
        },
        'backup-database': {
            'task': 'apps.config.tasks.backup_database',
            'schedule': 86400.0,  # Diariamente às 2h
            'options': {'eta': '02:00'}
        },
    },
    
    # Configurações de timezone
    timezone=settings.TIME_ZONE,
    enable_utc=True,
)

@app.task(bind=True)
def debug_task(self):
    """Tarefa de debug para testar o Celery"""
    print(f'Request: {self.request!r}')
