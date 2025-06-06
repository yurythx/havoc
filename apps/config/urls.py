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
    DatabaseConfigView,
    EmailConfigView,
    EnvironmentVariablesView,
    TestEmailView,
    SendTestEmailView,
    ExportConfigView,
    ImportConfigView,
)
from apps.config.views.multi_config_views import (
    EmailConfigListView,
    EmailConfigCreateView,
    EmailConfigUpdateView,
    EmailConfigDeleteView,
    EmailConfigTestView,
    EmailConfigSetDefaultView,
    DatabaseConfigListView,
    DatabaseConfigCreateView,
    DatabaseConfigUpdateView,
    DatabaseConfigDeleteView,
    DatabaseConfigTestView,
    DatabaseConfigSetDefaultView,
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
    
    # Configurações do Sistema
    path('sistema/', SystemConfigView.as_view(), name='system_config'),

    # Configurações Avançadas (Antigas - Manter compatibilidade)
    path('sistema/banco-dados/', DatabaseConfigView.as_view(), name='database_config'),
    path('sistema/email/', EmailConfigView.as_view(), name='email_config'),
    path('sistema/variaveis-ambiente/', EnvironmentVariablesView.as_view(), name='environment_variables'),

    # Múltiplas Configurações de Email
    path('emails/', EmailConfigListView.as_view(), name='email_configs'),
    path('emails/criar/', EmailConfigCreateView.as_view(), name='email_config_create'),
    path('emails/<int:pk>/editar/', EmailConfigUpdateView.as_view(), name='email_config_update'),
    path('emails/<int:pk>/deletar/', EmailConfigDeleteView.as_view(), name='email_config_delete'),
    path('emails/<int:pk>/testar/', EmailConfigTestView.as_view(), name='email_config_test'),
    path('emails/<int:pk>/definir-padrao/', EmailConfigSetDefaultView.as_view(), name='email_config_set_default'),

    # Múltiplas Configurações de Banco
    path('bancos/', DatabaseConfigListView.as_view(), name='database_configs'),
    path('bancos/criar/', DatabaseConfigCreateView.as_view(), name='database_config_create'),
    path('bancos/<int:pk>/editar/', DatabaseConfigUpdateView.as_view(), name='database_config_update'),
    path('bancos/<int:pk>/deletar/', DatabaseConfigDeleteView.as_view(), name='database_config_delete'),
    path('bancos/<int:pk>/testar/', DatabaseConfigTestView.as_view(), name='database_config_test'),
    path('bancos/<int:pk>/definir-padrao/', DatabaseConfigSetDefaultView.as_view(), name='database_config_set_default'),

    # APIs de Teste
    path('sistema/test-email/', TestEmailView.as_view(), name='test_email'),
    path('sistema/send-test-email/', SendTestEmailView.as_view(), name='send_test_email'),

    # Import/Export
    path('sistema/export/', ExportConfigView.as_view(), name='export_config'),
    path('sistema/import/', ImportConfigView.as_view(), name='import_config'),
    
    # Logs de Auditoria (TODO)
    # path('logs/', AuditLogListView.as_view(), name='audit_log_list'),
    # path('logs/usuario/<int:user_id>/', UserAuditLogView.as_view(), name='user_audit_logs'),
]
