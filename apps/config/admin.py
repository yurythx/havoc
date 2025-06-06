from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from apps.config.models import SystemConfiguration, UserActivityLog

User = get_user_model()

@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    """Admin para configurações do sistema"""
    list_display = ('key', 'description', 'is_active', 'updated_by', 'updated_at')
    list_filter = ('is_active', 'updated_at', 'created_at')
    search_fields = ('key', 'description', 'value')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('key',)

    fieldsets = (
        (None, {
            'fields': ('key', 'value', 'description', 'is_active')
        }),
        ('Metadados', {
            'fields': ('updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Salva o modelo definindo o usuário que fez a alteração"""
        if not change or not obj.updated_by:
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    """Admin para logs de atividade"""
    list_display = ('user', 'action', 'target_user', 'description', 'ip_address', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('user__email', 'target_user__email', 'description', 'ip_address')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    fieldsets = (
        (None, {
            'fields': ('user', 'action', 'target_user', 'description')
        }),
        ('Detalhes Técnicos', {
            'fields': ('ip_address', 'user_agent', 'extra_data'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        """Não permite adicionar logs manualmente"""
        return False

    def has_change_permission(self, request, obj=None):
        """Não permite editar logs"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Permite deletar logs apenas para superusuários"""
        return request.user.is_superuser


# Customização do UserAdmin para incluir campos do modelo personalizado
class CustomUserAdmin(BaseUserAdmin):
    """Admin customizado para o modelo User"""

    # Adiciona campos personalizados às listas
    list_display = BaseUserAdmin.list_display + ('is_verified',)
    list_filter = BaseUserAdmin.list_filter + ('is_verified',)

    # Adiciona campos personalizados aos fieldsets
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Campos Personalizados', {
            'fields': ('is_verified', 'slug'),
        }),
    )

    # Adiciona campos personalizados ao formulário de criação
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Campos Personalizados', {
            'fields': ('email', 'is_verified'),
        }),
    )

# Re-registra o modelo User com o admin customizado
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
