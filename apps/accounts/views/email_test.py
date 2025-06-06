from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from apps.accounts.services.email_service import EmailService
import json
import logging

logger = logging.getLogger(__name__)


class EmailDiagnosticView(LoginRequiredMixin, View):
    """View para diagnóstico e teste de configurações de email"""
    template_name = 'accounts/email_diagnostic.html'
    
    def get(self, request):
        """Exibe página de diagnóstico de email"""
        email_service = EmailService()
        
        # Obter status das configurações
        config_status = email_service.get_config_status()
        
        # Testar conexão se configurado
        connection_status = None
        if config_status['configured'] and config_status['can_send']:
            try:
                success, message = email_service.test_connection()
                connection_status = {
                    'success': success,
                    'message': message
                }
            except Exception as e:
                connection_status = {
                    'success': False,
                    'message': f'Erro ao testar conexão: {str(e)}'
                }
        
        context = {
            'config_status': config_status,
            'connection_status': connection_status,
            'email_config': email_service.config,
            'user_email': request.user.email,
        }
        
        return render(request, self.template_name, context)


@method_decorator(csrf_exempt, name='dispatch')
class TestEmailSendView(LoginRequiredMixin, View):
    """View para enviar email de teste"""
    
    def post(self, request):
        """Envia email de teste"""
        try:
            data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
            recipient_email = data.get('email', request.user.email)
            
            if not recipient_email:
                return JsonResponse({
                    'success': False,
                    'message': 'Email do destinatário é obrigatório'
                })
            
            email_service = EmailService()
            
            # Verificar se email está configurado
            config_status = email_service.get_config_status()
            if not config_status['can_send']:
                return JsonResponse({
                    'success': False,
                    'message': 'Email não está configurado corretamente. Problemas: ' + ', '.join(config_status['issues'])
                })
            
            # Enviar email de teste
            success, message = email_service.send_test_email(
                recipient_email=recipient_email,
                user_name=request.user.get_full_name() or request.user.username
            )
            
            if success:
                logger.info(f'Email de teste enviado por {request.user.username} para {recipient_email}')
            
            return JsonResponse({
                'success': success,
                'message': message
            })
            
        except Exception as e:
            logger.error(f'Erro ao enviar email de teste: {e}', exc_info=True)
            return JsonResponse({
                'success': False,
                'message': f'Erro interno: {str(e)}'
            })


@method_decorator(csrf_exempt, name='dispatch')
class TestConnectionView(LoginRequiredMixin, View):
    """View para testar conexão SMTP"""
    
    def post(self, request):
        """Testa conexão SMTP"""
        try:
            email_service = EmailService()
            success, message = email_service.test_connection()
            
            return JsonResponse({
                'success': success,
                'message': message
            })
            
        except Exception as e:
            logger.error(f'Erro ao testar conexão SMTP: {e}', exc_info=True)
            return JsonResponse({
                'success': False,
                'message': f'Erro ao testar conexão: {str(e)}'
            })


class QuickEmailSetupView(LoginRequiredMixin, View):
    """View para configuração rápida de email"""
    template_name = 'accounts/quick_email_setup.html'
    
    def get(self, request):
        """Exibe formulário de configuração rápida"""
        email_service = EmailService()
        config_status = email_service.get_config_status()
        
        context = {
            'config_status': config_status,
            'current_config': email_service.config,
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        """Processa configuração rápida"""
        try:
            # Obter dados do formulário
            email_host = request.POST.get('email_host', '').strip()
            email_port = request.POST.get('email_port', '587')
            email_user = request.POST.get('email_user', '').strip()
            email_password = request.POST.get('email_password', '').strip()
            use_tls = request.POST.get('use_tls') == 'on'
            use_ssl = request.POST.get('use_ssl') == 'on'
            from_email = request.POST.get('from_email', '').strip()
            
            # Validações básicas
            if not all([email_host, email_user, email_password, from_email]):
                messages.error(request, 'Todos os campos obrigatórios devem ser preenchidos.')
                return redirect('accounts:quick_email_setup')
            
            try:
                email_port = int(email_port)
            except ValueError:
                messages.error(request, 'Porta deve ser um número válido.')
                return redirect('accounts:quick_email_setup')
            
            # Criar configuração
            email_config = {
                'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
                'EMAIL_HOST': email_host,
                'EMAIL_PORT': email_port,
                'EMAIL_HOST_USER': email_user,
                'EMAIL_HOST_PASSWORD': email_password,
                'EMAIL_USE_TLS': use_tls,
                'EMAIL_USE_SSL': use_ssl,
                'DEFAULT_FROM_EMAIL': from_email,
                'EMAIL_TIMEOUT': 30,
            }
            
            # Salvar configuração
            try:
                from apps.config.services.system_config_service import SystemConfigService
                from apps.config.repositories.config_repository import DjangoSystemConfigRepository
                
                config_service = SystemConfigService(
                    DjangoSystemConfigRepository(),
                    None
                )
                
                success = config_service.set_config(
                    key='email_settings',
                    value=email_config,
                    description='Configuração rápida de email SMTP',
                    updated_by=request.user
                )
                
                if success:
                    messages.success(request, '✅ Configurações de email salvas com sucesso!')
                    
                    # Testar configuração
                    if 'test_after_save' in request.POST:
                        email_service = EmailService()
                        test_success, test_message = email_service.test_connection()
                        
                        if test_success:
                            messages.success(request, f'🧪 Teste de conexão: {test_message}')
                            
                            # Enviar email de teste se solicitado
                            if 'send_test_email' in request.POST:
                                email_success, email_message = email_service.send_test_email(
                                    recipient_email=request.user.email,
                                    user_name=request.user.get_full_name() or request.user.username
                                )
                                
                                if email_success:
                                    messages.success(request, f'📧 {email_message}')
                                else:
                                    messages.warning(request, f'⚠️ Conexão OK, mas erro no envio: {email_message}')
                        else:
                            messages.warning(request, f'⚠️ Configuração salva, mas teste falhou: {test_message}')
                    
                    return redirect('accounts:email_diagnostic')
                else:
                    messages.error(request, 'Erro ao salvar configurações.')
                    
            except Exception as e:
                logger.error(f'Erro ao salvar configurações de email: {e}', exc_info=True)
                messages.error(request, f'Erro ao salvar configurações: {str(e)}')
            
        except Exception as e:
            logger.error(f'Erro na configuração rápida de email: {e}', exc_info=True)
            messages.error(request, f'Erro interno: {str(e)}')
        
        return redirect('accounts:quick_email_setup')


class PasswordResetTestView(LoginRequiredMixin, View):
    """View para testar envio de código de redefinição de senha"""
    
    def post(self, request):
        """Testa envio de código de redefinição"""
        try:
            test_email = request.POST.get('test_email', request.user.email)
            
            if not test_email:
                return JsonResponse({
                    'success': False,
                    'message': 'Email é obrigatório'
                })
            
            # Gerar código de teste
            import random
            import string
            test_code = ''.join(random.choices(string.digits, k=6))
            
            # Enviar usando o serviço de email
            email_service = EmailService()
            success = email_service.send_password_reset_code(test_email, test_code)
            
            if success:
                message = f'Código de teste {test_code} enviado para {test_email}'
                logger.info(f'Teste de redefinição de senha enviado por {request.user.username} para {test_email}')
            else:
                message = 'Falha ao enviar código de teste'
            
            return JsonResponse({
                'success': success,
                'message': message,
                'test_code': test_code if success else None
            })
            
        except Exception as e:
            logger.error(f'Erro ao testar redefinição de senha: {e}', exc_info=True)
            return JsonResponse({
                'success': False,
                'message': f'Erro: {str(e)}'
            })
