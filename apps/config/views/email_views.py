"""
Views para gerenciamento de configurações de email.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, FormView
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone

from apps.config.mixins import ConfigPermissionMixin
from apps.config.forms import EmailConfigForm, EmailTestForm


class EmailConfigView(ConfigPermissionMixin, TemplateView):
    """View para configurações de email."""
    template_name = 'config/email/config.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Configurações atuais do email
        context.update({
            'email_host': getattr(settings, 'EMAIL_HOST', ''),
            'email_port': getattr(settings, 'EMAIL_PORT', 587),
            'email_host_user': getattr(settings, 'EMAIL_HOST_USER', ''),
            'email_use_tls': getattr(settings, 'EMAIL_USE_TLS', True),
            'email_use_ssl': getattr(settings, 'EMAIL_USE_SSL', False),
            'default_from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', ''),
            'email_backend': getattr(settings, 'EMAIL_BACKEND', ''),
        })
        
        return context


class EmailTestView(ConfigPermissionMixin, FormView):
    """View para teste de email."""
    template_name = 'config/email/test.html'
    form_class = EmailTestForm
    
    def form_valid(self, form):
        try:
            # Dados do formulário
            recipient = form.cleaned_data['recipient']
            subject = form.cleaned_data.get('subject', 'Teste de Email - Havoc')
            message = form.cleaned_data.get('message', 'Este é um email de teste do sistema Havoc.')
            
            # Enviar email de teste
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@havoc.com'),
                recipient_list=[recipient],
                fail_silently=False,
            )
            
            messages.success(
                self.request, 
                f'Email de teste enviado com sucesso para {recipient}!'
            )
            
        except Exception as e:
            messages.error(
                self.request, 
                f'Erro ao enviar email: {str(e)}'
            )
        
        return redirect('config:email_test')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Status da configuração de email
        context.update({
            'email_configured': bool(getattr(settings, 'EMAIL_HOST', '')),
            'email_host': getattr(settings, 'EMAIL_HOST', 'Não configurado'),
            'email_port': getattr(settings, 'EMAIL_PORT', 'N/A'),
            'default_from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'Não configurado'),
        })
        
        return context


class EmailTemplatesView(ConfigPermissionMixin, TemplateView):
    """View para gerenciamento de templates de email."""
    template_name = 'config/email/templates.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Lista de templates de email disponíveis
        email_templates = [
            {
                'name': 'Confirmação de Registro',
                'file': 'accounts/emails/registration_confirmation.html',
                'description': 'Email enviado após o registro de um novo usuário',
                'status': 'Ativo'
            },
            {
                'name': 'Reset de Senha',
                'file': 'accounts/emails/password_reset.html',
                'description': 'Email para redefinição de senha',
                'status': 'Ativo'
            },
            {
                'name': 'Alteração de Email',
                'file': 'accounts/emails/email_change.html',
                'description': 'Email de confirmação para mudança de endereço',
                'status': 'Ativo'
            },
        ]
        
        context['email_templates'] = email_templates
        
        return context


class EmailStatsView(ConfigPermissionMixin, TemplateView):
    """View para estatísticas de email."""
    template_name = 'config/email/stats.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estatísticas de email (simuladas - implementar com modelo real)
        context.update({
            'emails_sent_today': 0,
            'emails_sent_week': 0,
            'emails_sent_month': 0,
            'emails_failed': 0,
            'email_queue_size': 0,
        })
        
        return context


def test_email_connection(request):
    """AJAX endpoint para testar conexão de email."""
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    try:
        from django.core.mail import get_connection
        
        # Testar conexão
        connection = get_connection()
        connection.open()
        connection.close()
        
        return JsonResponse({
            'success': True,
            'message': 'Conexão com servidor de email estabelecida com sucesso!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro na conexão: {str(e)}'
        })


def send_test_email_ajax(request):
    """AJAX endpoint para envio de email de teste."""
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        recipient = request.POST.get('recipient')
        
        # Validar email
        if not recipient:
            return JsonResponse({'error': 'Email do destinatário é obrigatório'})
        
        validate_email(recipient)
        
        # Enviar email
        send_mail(
            subject='Teste de Email - Havoc Admin',
            message=f'Este é um email de teste enviado em {timezone.now().strftime("%d/%m/%Y às %H:%M")}.\n\nSe você recebeu este email, a configuração está funcionando corretamente!',
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@havoc.com'),
            recipient_list=[recipient],
            fail_silently=False,
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Email de teste enviado com sucesso para {recipient}!'
        })
        
    except ValidationError:
        return JsonResponse({'error': 'Email inválido'})
    except Exception as e:
        return JsonResponse({'error': f'Erro ao enviar email: {str(e)}'})
