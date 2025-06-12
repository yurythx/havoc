"""
Views para gerenciamento de configurações de banco de dados
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
import json

from apps.config.models.configuration_models import DatabaseConfiguration
from apps.config.forms.database_forms import (
    DatabaseConfigurationForm, 
    DatabaseTestForm, 
    DatabaseSelectionForm
)
from apps.config.mixins import ConfigPermissionMixin


def is_admin_user(user):
    """Verifica se o usuário é admin"""
    return user.is_authenticated and user.is_staff


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin_user), name='dispatch')
class DatabaseConfigListView(ConfigPermissionMixin, ListView):
    """Lista de configurações de banco de dados"""
    model = DatabaseConfiguration
    template_name = 'config/database/list.html'
    context_object_name = 'configurations'
    paginate_by = 10
    
    def get_queryset(self):
        return DatabaseConfiguration.objects.all().order_by('-is_default', 'name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Configurações de Banco de Dados',
            'breadcrumbs': [
                {'name': 'Configurações', 'url': '/config/'},
                {'name': 'Banco de Dados', 'url': None}
            ]
        })
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin_user), name='dispatch')
class DatabaseConfigCreateView(ConfigPermissionMixin, CreateView):
    """Criar nova configuração de banco"""
    model = DatabaseConfiguration
    form_class = DatabaseConfigurationForm
    template_name = 'config/database/form.html'
    success_url = reverse_lazy('config:database_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Nova Configuração de Banco',
            'form_title': 'Adicionar Configuração de Banco de Dados',
            'breadcrumbs': [
                {'name': 'Configurações', 'url': '/config/'},
                {'name': 'Banco de Dados', 'url': reverse_lazy('config:database_list')},
                {'name': 'Nova Configuração', 'url': None}
            ]
        })
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Configuração de banco criada com sucesso!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin_user), name='dispatch')
class DatabaseConfigUpdateView(ConfigPermissionMixin, UpdateView):
    """Editar configuração de banco"""
    model = DatabaseConfiguration
    form_class = DatabaseConfigurationForm
    template_name = 'config/database/form.html'
    success_url = reverse_lazy('config:database_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': f'Editar {self.object.name}',
            'form_title': f'Editar Configuração: {self.object.name}',
            'breadcrumbs': [
                {'name': 'Configurações', 'url': '/config/'},
                {'name': 'Banco de Dados', 'url': reverse_lazy('config:database_list')},
                {'name': 'Editar', 'url': None}
            ]
        })
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Configuração de banco atualizada com sucesso!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin_user), name='dispatch')
class DatabaseConfigDeleteView(ConfigPermissionMixin, DeleteView):
    """Deletar configuração de banco"""
    model = DatabaseConfiguration
    template_name = 'config/database/delete.html'
    success_url = reverse_lazy('config:database_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': f'Excluir {self.object.name}',
            'breadcrumbs': [
                {'name': 'Configurações', 'url': '/config/'},
                {'name': 'Banco de Dados', 'url': reverse_lazy('config:database_list')},
                {'name': 'Excluir', 'url': None}
            ]
        })
        return context
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Não permitir deletar configuração padrão
        if self.object.is_default:
            messages.error(request, 'Não é possível excluir a configuração padrão.')
            return redirect('config:database_list')
        
        messages.success(request, f'Configuração "{self.object.name}" excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


@login_required
@user_passes_test(is_admin_user)
def database_test_connection(request, pk):
    """Testar conexão com banco de dados"""
    config = get_object_or_404(DatabaseConfiguration, pk=pk)
    
    if request.method == 'POST':
        success, message = config.test_connection()
        
        return JsonResponse({
            'success': success,
            'message': message,
            'last_tested': config.last_tested_at.isoformat() if config.last_tested_at else None
        })
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
@user_passes_test(is_admin_user)
def database_selection(request):
    """Seleção de banco padrão"""
    if request.method == 'POST':
        form = DatabaseSelectionForm(request.POST)
        if form.is_valid():
            try:
                config = form.save()
                messages.success(
                    request, 
                    f'Configuração "{config.name}" definida como padrão com sucesso!'
                )
                
                if form.cleaned_data['update_env']:
                    messages.info(
                        request,
                        'Arquivo .env atualizado. Reinicie o servidor para aplicar as mudanças.'
                    )
                
                return redirect('config:database_list')
            except Exception as e:
                messages.error(request, f'Erro ao aplicar configuração: {str(e)}')
    else:
        form = DatabaseSelectionForm()
    
    context = {
        'form': form,
        'page_title': 'Selecionar Banco Padrão',
        'breadcrumbs': [
            {'name': 'Configurações', 'url': '/config/'},
            {'name': 'Banco de Dados', 'url': reverse_lazy('config:database_list')},
            {'name': 'Selecionar Padrão', 'url': None}
        ]
    }
    
    return render(request, 'config/database/selection.html', context)


@login_required
@user_passes_test(is_admin_user)
def database_quick_setup(request):
    """Setup rápido de banco de dados"""
    if request.method == 'POST':
        db_type = request.POST.get('db_type')
        
        # Configurações pré-definidas
        presets = {
            'sqlite': {
                'name': 'SQLite Local',
                'engine': 'django.db.backends.sqlite3',
                'database_name': 'db.sqlite3',
                'host': '',
                'port': None,
                'username': '',
                'password': '',
            },
            'postgresql': {
                'name': 'PostgreSQL Local',
                'engine': 'django.db.backends.postgresql',
                'database_name': 'havoc_db',
                'host': 'localhost',
                'port': 5432,
                'username': 'postgres',
                'password': '',
            },
            'mysql': {
                'name': 'MySQL Local',
                'engine': 'django.db.backends.mysql',
                'database_name': 'havoc_db',
                'host': 'localhost',
                'port': 3306,
                'username': 'root',
                'password': '',
            }
        }
        
        if db_type in presets:
            preset = presets[db_type]
            
            # Criar configuração
            config = DatabaseConfiguration.objects.create(**preset)
            
            messages.success(
                request,
                f'Configuração "{config.name}" criada com sucesso! '
                f'Edite-a para ajustar os detalhes da conexão.'
            )
            
            return redirect('config:database_edit', pk=config.pk)
    
    context = {
        'page_title': 'Setup Rápido de Banco',
        'breadcrumbs': [
            {'name': 'Configurações', 'url': '/config/'},
            {'name': 'Banco de Dados', 'url': reverse_lazy('config:database_list')},
            {'name': 'Setup Rápido', 'url': None}
        ]
    }
    
    return render(request, 'config/database/quick_setup.html', context)
