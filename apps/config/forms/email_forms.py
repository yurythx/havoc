"""
Formulários para configurações de email.
"""

from django import forms
from django.core.validators import validate_email


class EmailConfigForm(forms.Form):
    """Formulário para configurações de email."""
    
    email_host = forms.CharField(
        label='Servidor SMTP',
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'smtp.gmail.com'
        }),
        help_text='Endereço do servidor SMTP'
    )
    
    email_port = forms.IntegerField(
        label='Porta',
        required=True,
        initial=587,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '587'
        }),
        help_text='Porta do servidor SMTP (587 para TLS, 465 para SSL)'
    )
    
    email_host_user = forms.EmailField(
        label='Usuário',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu-email@gmail.com'
        }),
        help_text='Email usado para autenticação no servidor SMTP'
    )
    
    email_host_password = forms.CharField(
        label='Senha',
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Sua senha ou app password'
        }),
        help_text='Senha ou app password para autenticação'
    )
    
    email_use_tls = forms.BooleanField(
        label='Usar TLS',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Ativar criptografia TLS (recomendado para porta 587)'
    )
    
    email_use_ssl = forms.BooleanField(
        label='Usar SSL',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Ativar criptografia SSL (para porta 465)'
    )
    
    default_from_email = forms.EmailField(
        label='Email Padrão (From)',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'noreply@seudominio.com'
        }),
        help_text='Email que aparecerá como remetente'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        use_tls = cleaned_data.get('email_use_tls')
        use_ssl = cleaned_data.get('email_use_ssl')
        port = cleaned_data.get('email_port')
        
        # Validar que TLS e SSL não estão ambos ativos
        if use_tls and use_ssl:
            raise forms.ValidationError(
                'TLS e SSL não podem estar ativos simultaneamente. Escolha apenas um.'
            )
        
        # Sugerir porta baseada na configuração
        if use_ssl and port != 465:
            self.add_error('email_port', 'Para SSL, a porta recomendada é 465.')
        elif use_tls and port != 587:
            self.add_error('email_port', 'Para TLS, a porta recomendada é 587.')
        
        return cleaned_data


class EmailTestForm(forms.Form):
    """Formulário para teste de email."""
    
    recipient = forms.EmailField(
        label='Destinatário',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'teste@exemplo.com'
        }),
        help_text='Email que receberá o teste'
    )
    
    subject = forms.CharField(
        label='Assunto',
        max_length=255,
        required=False,
        initial='Teste de Email - Havoc',
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        }),
        help_text='Assunto do email de teste'
    )
    
    message = forms.CharField(
        label='Mensagem',
        required=False,
        initial='Este é um email de teste do sistema Havoc. Se você recebeu esta mensagem, a configuração está funcionando corretamente!',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4
        }),
        help_text='Conteúdo do email de teste'
    )
