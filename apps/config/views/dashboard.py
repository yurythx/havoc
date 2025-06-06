from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.views import View
from apps.config.services.system_config_service import AuditLogService
from apps.config.repositories.config_repository import DjangoAuditLogRepository
from apps.config.mixins import ConfigPermissionMixin, PermissionHelperMixin

User = get_user_model()

class ConfigDashboardView(ConfigPermissionMixin, PermissionHelperMixin, View):
    """Dashboard principal do módulo de configuração"""
    template_name = 'config/dashboard.html'

    def get(self, request):
        """Exibe o dashboard"""
        # Estatísticas básicas
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        total_groups = Group.objects.count()

        # Atividades recentes
        audit_service = AuditLogService(DjangoAuditLogRepository())
        recent_activities = audit_service.get_system_activity_logs(limit=10)

        context = {
            'total_users': total_users,
            'active_users': active_users,
            'staff_users': staff_users,
            'total_groups': total_groups,
            'recent_activities': recent_activities,
        }

        return render(request, self.template_name, context)
