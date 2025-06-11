from django.urls import path
from apps.config.views import (
    ConfigDashboardView,
    UserListView,
    UserCreateView,
    UserDetailView,
    UserUpdateView,
    UserDeleteView,
    SystemConfigView,
)
from apps.config.views.advanced_config_views import (
    EnvironmentVariablesView,
)
from apps.config.views.email_views import (
    EmailConfigView,
    EmailTestView,
    EmailTemplatesView,
    EmailStatsView,
    send_test_email_ajax,
    test_email_connection_ajax,
)
from apps.config.views.module_views import (
    ModuleListView,
    ModuleDetailView,
    ModuleUpdateView,
    ModuleToggleView,
    ModuleStatsAPIView,
    ModuleDependencyCheckView,
)



app_name = 'config'

urlpatterns = [
    # Dashboard
    path('', ConfigDashboardView.as_view(), name='dashboard'),
    
    # Usuários
    path('usuarios/', UserListView.as_view(), name='user_list'),
    path('usuarios/criar/', UserCreateView.as_view(), name='user_create'),
    path('usuarios/<slug:slug>/', UserDetailView.as_view(), name='user_detail'),
    path('usuarios/<slug:slug>/editar/', UserUpdateView.as_view(), name='user_update'),
    path('usuarios/<slug:slug>/deletar/', UserDeleteView.as_view(), name='user_delete'),
    
    # Grupos (TODO)
    # path('grupos/', GroupListView.as_view(), name='group_list'),
    # path('grupos/criar/', GroupCreateView.as_view(), name='group_create'),
    # path('grupos/<int:group_id>/', GroupDetailView.as_view(), name='group_detail'),
    # path('grupos/<int:group_id>/editar/', GroupUpdateView.as_view(), name='group_update'),
    # path('grupos/<int:group_id>/deletar/', GroupDeleteView.as_view(), name='group_delete'),
    
    # Email
    path('email/', EmailConfigView.as_view(), name='email_config'),
    path('email/teste/', EmailTestView.as_view(), name='email_test'),
    path('email/templates/', EmailTemplatesView.as_view(), name='email_templates'),
    path('email/estatisticas/', EmailStatsView.as_view(), name='email_stats'),

    # AJAX Email
    path('ajax/test-email-connection/', test_email_connection_ajax, name='test_email_connection'),
    path('ajax/send-test-email/', send_test_email_ajax, name='send_test_email_ajax'),

    # Configurações do Sistema
    path('sistema/', SystemConfigView.as_view(), name='system_config'),

    # Módulos do Sistema
    path('modulos/', ModuleListView.as_view(), name='module_list'),
    path('modulos/<str:app_name>/', ModuleDetailView.as_view(), name='module_detail'),
    path('modulos/<str:app_name>/editar/', ModuleUpdateView.as_view(), name='module_update'),
    path('modulos/<str:app_name>/toggle/', ModuleToggleView.as_view(), name='module_toggle'),

    # APIs dos Módulos
    path('api/modulos/stats/', ModuleStatsAPIView.as_view(), name='module_stats_api'),
    path('api/modulos/<str:app_name>/dependencies/', ModuleDependencyCheckView.as_view(), name='module_dependency_check'),

    # Configurações Avançadas
    path('sistema/variaveis-ambiente/', EnvironmentVariablesView.as_view(), name='environment_variables'),

    # Backup & Manutenção (TODO)
    path('backup/', SystemConfigView.as_view(), name='backup_config'),
    path('cache/', SystemConfigView.as_view(), name='cache_management'),
    path('logs/', SystemConfigView.as_view(), name='system_logs'),
    
    # Logs de Auditoria (TODO)
    # path('logs/', AuditLogListView.as_view(), name='audit_log_list'),
    # path('logs/usuario/<int:user_id>/', UserAuditLogView.as_view(), name='user_audit_logs'),
]
