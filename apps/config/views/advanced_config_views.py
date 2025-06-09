from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from apps.config.forms.advanced_config_forms import (
    EnvironmentVariablesForm
)
from apps.config.services.system_config_service import SystemConfigService, AuditLogService
from apps.config.repositories.config_repository import DjangoSystemConfigRepository, DjangoAuditLogRepository
from apps.config.mixins import SuperuserRequiredMixin, PermissionHelperMixin
import json





class EnvironmentVariablesView(SuperuserRequiredMixin, PermissionHelperMixin, View):
    """View para configurações de variáveis de ambiente - Apenas superusuários"""
    template_name = 'config/environment_variables.html'

    def get(self, request):
        """Exibe formulário de variáveis de ambiente"""
        form = EnvironmentVariablesForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """Processa variáveis de ambiente"""
        form = EnvironmentVariablesForm(request.POST)
        
        if 'generate_key' in request.POST:
            # Gera nova SECRET_KEY
            new_key = form.generate_secret_key()
            form.data = form.data.copy()
            form.data['secret_key'] = new_key
            messages.info(request, 'Nova SECRET_KEY gerada. Salve o formulário para aplicar.')
            
        elif form.is_valid():
            try:
                success = form.save(user=request.user)
                
                if success:
                    messages.success(request, 'Variáveis de ambiente salvas com sucesso!')
                    messages.warning(request, 'IMPORTANTE: Reinicie o servidor para aplicar as alterações.')
                    
                    # Log de auditoria para alteração crítica
                    audit_service = AuditLogService(DjangoAuditLogRepository())
                    audit_service.log_user_action(
                        user=request.user,
                        action='UPDATE_ENVIRONMENT',
                        description='Variáveis de ambiente atualizadas'
                    )
                    
                    return redirect('config:system_config')
                else:
                    messages.error(request, 'Erro ao salvar variáveis de ambiente.')
                    
            except Exception as e:
                messages.error(request, f'Erro ao salvar variáveis: {str(e)}')

        return render(request, self.template_name, {'form': form})





class ExportConfigView(SuperuserRequiredMixin, PermissionHelperMixin, View):
    """View para exportar configurações - Apenas superusuários"""

    def get(self, request):
        """Exporta configurações do sistema"""
        try:
            config_service = SystemConfigService(
                DjangoSystemConfigRepository(),
                None
            )
            
            # Obtém todas as configurações
            configs = {}
            
            # Configurações de banco
            try:
                db_config = config_service.get_config('database_settings')
                if db_config:
                    # Remove senha por segurança
                    db_config_safe = db_config.copy()
                    if 'PASSWORD' in db_config_safe:
                        db_config_safe['PASSWORD'] = '***HIDDEN***'
                    configs['database_settings'] = db_config_safe
            except:
                pass
            
            # Configurações de email
            try:
                email_config = config_service.get_config('email_settings')
                if email_config:
                    # Remove senha por segurança
                    email_config_safe = email_config.copy()
                    if 'EMAIL_HOST_PASSWORD' in email_config_safe:
                        email_config_safe['EMAIL_HOST_PASSWORD'] = '***HIDDEN***'
                    configs['email_settings'] = email_config_safe
            except:
                pass
            
            # Configurações de ambiente
            try:
                env_config = config_service.get_config('environment_variables')
                if env_config:
                    # Remove chave secreta por segurança
                    env_config_safe = env_config.copy()
                    if 'SECRET_KEY' in env_config_safe:
                        env_config_safe['SECRET_KEY'] = '***HIDDEN***'
                    configs['environment_variables'] = env_config_safe
            except:
                pass
            
            # Log da ação
            audit_service = AuditLogService(DjangoAuditLogRepository())
            audit_service.log_user_action(
                user=request.user,
                action='EXPORT_CONFIG',
                description='Configurações do sistema exportadas'
            )
            
            from django.http import HttpResponse
            import json
            
            response = HttpResponse(
                json.dumps(configs, indent=2, ensure_ascii=False),
                content_type='application/json'
            )
            response['Content-Disposition'] = 'attachment; filename="system_config_export.json"'
            
            return response
            
        except Exception as e:
            messages.error(request, f'Erro ao exportar configurações: {str(e)}')
            return redirect('config:system_config')


class ImportConfigView(SuperuserRequiredMixin, PermissionHelperMixin, View):
    """View para importar configurações - Apenas superusuários"""

    def post(self, request):
        """Importa configurações do sistema"""
        try:
            if 'config_file' not in request.FILES:
                messages.error(request, 'Nenhum arquivo selecionado.')
                return redirect('config:system_config')
            
            config_file = request.FILES['config_file']
            
            # Lê e valida o arquivo JSON
            try:
                content = config_file.read().decode('utf-8')
                configs = json.loads(content)
            except (UnicodeDecodeError, json.JSONDecodeError) as e:
                messages.error(request, f'Arquivo JSON inválido: {str(e)}')
                return redirect('config:system_config')
            
            config_service = SystemConfigService(
                DjangoSystemConfigRepository(),
                AuditLogService(DjangoAuditLogRepository())
            )
            
            imported_count = 0
            
            # Importa cada configuração
            for key, value in configs.items():
                try:
                    success = config_service.set_config(
                        key=key,
                        value=value,
                        description=f'Importado de arquivo em {request.user.date_joined.strftime("%d/%m/%Y %H:%M")}',
                        updated_by=request.user
                    )
                    if success:
                        imported_count += 1
                except Exception as e:
                    messages.warning(request, f'Erro ao importar {key}: {str(e)}')
            
            if imported_count > 0:
                messages.success(request, f'{imported_count} configurações importadas com sucesso!')
                
                # Log da ação
                audit_service = AuditLogService(DjangoAuditLogRepository())
                audit_service.log_user_action(
                    user=request.user,
                    action='IMPORT_CONFIG',
                    description=f'{imported_count} configurações importadas de arquivo'
                )
            else:
                messages.warning(request, 'Nenhuma configuração foi importada.')
            
            return redirect('config:system_config')
            
        except Exception as e:
            messages.error(request, f'Erro ao importar configurações: {str(e)}')
            return redirect('config:system_config')
