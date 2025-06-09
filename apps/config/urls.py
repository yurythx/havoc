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
    ExportConfigView,
    ImportConfigView,
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

    # Configurações Avançadas
    path('sistema/variaveis-ambiente/', EnvironmentVariablesView.as_view(), name='environment_variables'),

    # Import/Export
    path('sistema/export/', ExportConfigView.as_view(), name='export_config'),
    path('sistema/import/', ImportConfigView.as_view(), name='import_config'),
    
    # Logs de Auditoria (TODO)
    # path('logs/', AuditLogListView.as_view(), name='audit_log_list'),
    # path('logs/usuario/<int:user_id>/', UserAuditLogView.as_view(), name='user_audit_logs'),
]
