"""
Formulários para configuração de banco de dados
"""

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import re

from apps.config.models.configuration_models import DatabaseConfiguration


class DatabaseConfigurationForm(forms.ModelForm):
    """Formulário para configuração de banco de dados"""
    
    # Campo para senha com widget de password
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a senha do banco de dados'
        }),
        required=False,
        help_text='Deixe em branco para manter a senha atual'
    )
    
    class Meta:
        model = DatabaseConfiguration
        fields = [
            'name', 'engine', 'host', 'port', 'database_name', 
            'username', 'password', 'options', 'is_default', 'is_active'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da configuração (ex: Produção, Desenvolvimento)'
            }),
            'engine': forms.Select(attrs={
                'class': 'form-select',
                'onchange': 'updateDatabaseFields(this.value)'
            }),
            'host': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'localhost ou IP do servidor'
            }),
            'port': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Porta do banco (ex: 5432, 3306)'
            }),
            'database_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do banco de dados'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Usuário do banco de dados'
            }),
            'options': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Opções adicionais em JSON (opcional)'
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        
        labels = {
            'name': 'Nome da Configuração',
            'engine': 'Tipo de Banco',
            'host': 'Servidor',
            'port': 'Porta',
            'database_name': 'Nome do Banco',
            'username': 'Usuário',
            'password': 'Senha',
            'options': 'Opções Adicionais',
            'is_default': 'Configuração Padrão',
            'is_active': 'Ativo',
        }
        
        help_texts = {
            'name': 'Nome identificador para esta configuração',
            'engine': 'Tipo do sistema de banco de dados',
            'host': 'Endereço do servidor do banco de dados',
            'port': 'Porta de conexão do banco de dados',
            'database_name': 'Nome do banco de dados a ser usado',
            'username': 'Nome de usuário para autenticação',
            'options': 'Configurações adicionais em formato JSON',
            'is_default': 'Marque para usar como configuração padrão do sistema',
            'is_active': 'Marque para ativar esta configuração',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Se estamos editando, não mostrar a senha atual
        if self.instance.pk:
            self.fields['password'].required = False
            self.fields['password'].help_text = 'Deixe em branco para manter a senha atual'
        else:
            self.fields['password'].required = True
            self.fields['password'].help_text = 'Senha para conectar ao banco de dados'

    def clean_name(self):
        """Validação do nome"""
        name = self.cleaned_data.get('name')
        if name:
            # Verificar se já existe outro com o mesmo nome
            existing = DatabaseConfiguration.objects.filter(name__iexact=name)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError('Já existe uma configuração com este nome.')
        
        return name

    def clean_port(self):
        """Validação da porta"""
        port = self.cleaned_data.get('port')
        if port:
            if port < 1 or port > 65535:
                raise ValidationError('A porta deve estar entre 1 e 65535.')
        return port

    def clean_options(self):
        """Validação das opções JSON"""
        options = self.cleaned_data.get('options')
        if options:
            try:
                import json
                json.loads(options)
            except json.JSONDecodeError:
                raise ValidationError('Opções devem estar em formato JSON válido.')
        return options

    def clean(self):
        """Validações gerais"""
        cleaned_data = super().clean()
        engine = cleaned_data.get('engine')
        host = cleaned_data.get('host')
        database_name = cleaned_data.get('database_name')
        
        # Validações específicas por tipo de banco
        if engine == 'django.db.backends.sqlite3':
            if not database_name:
                raise ValidationError('Nome do banco é obrigatório para SQLite.')
        else:
            if not host:
                raise ValidationError('Servidor é obrigatório para este tipo de banco.')
            if not database_name:
                raise ValidationError('Nome do banco é obrigatório.')
        
        return cleaned_data

    def save(self, commit=True):
        """Salvar com tratamento especial para senha"""
        instance = super().save(commit=False)
        
        # Se senha foi fornecida, atualizar
        password = self.cleaned_data.get('password')
        if password:
            instance.password = password
        elif not instance.pk:
            # Nova instância sem senha
            instance.password = ''
        
        if commit:
            instance.save()
        
        return instance


class DatabaseTestForm(forms.Form):
    """Formulário para testar conexão com banco de dados"""
    
    configuration_id = forms.IntegerField(
        widget=forms.HiddenInput()
    )
    
    def __init__(self, *args, **kwargs):
        self.configuration = kwargs.pop('configuration', None)
        super().__init__(*args, **kwargs)
        
        if self.configuration:
            self.fields['configuration_id'].initial = self.configuration.pk

    def test_connection(self):
        """Testa a conexão com o banco"""
        if not self.configuration:
            return False, 'Configuração não encontrada.'
        
        return self.configuration.test_connection()


class DatabaseSelectionForm(forms.Form):
    """Formulário para seleção de banco padrão"""
    
    database_config = forms.ModelChoiceField(
        queryset=DatabaseConfiguration.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Configuração de Banco',
        help_text='Selecione a configuração de banco que será usada como padrão'
    )
    
    update_env = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Atualizar arquivo .env',
        help_text='Marque para atualizar as variáveis de ambiente no arquivo .env'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Marcar a configuração padrão atual
        try:
            current_default = DatabaseConfiguration.objects.get(is_default=True)
            self.fields['database_config'].initial = current_default
        except DatabaseConfiguration.DoesNotExist:
            pass

    def save(self):
        """Aplicar a configuração selecionada"""
        config = self.cleaned_data['database_config']
        update_env = self.cleaned_data['update_env']
        
        # Remover padrão atual
        DatabaseConfiguration.objects.filter(is_default=True).update(is_default=False)
        
        # Definir novo padrão
        config.is_default = True
        config.save()
        
        # Atualizar .env se solicitado
        if update_env:
            config.update_env_file()
        
        return config
