from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, UpdateView
from django.views import View
from django.http import JsonResponse
from django.db import transaction
from apps.config.models.app_module_config import AppModuleConfiguration
from apps.config.services.module_service import ModuleService
from apps.config.forms.module_forms import ModuleConfigurationForm, ModuleToggleForm
import json


class ModuleListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Lista todos os módulos do sistema"""
    model = AppModuleConfiguration
    template_name = 'config/modules/list.html'
    context_object_name = 'modules'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        return AppModuleConfiguration.objects.all().order_by('menu_order', 'display_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        module_service = ModuleService()
        
        context.update({
            'module_stats': module_service.get_module_statistics(),
            'page_title': 'Gerenciamento de Módulos',
            'page_description': 'Configure quais módulos estão disponíveis no sistema',
        })
        return context


class ModuleDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Detalhes de um módulo específico"""
    model = AppModuleConfiguration
    template_name = 'config/modules/detail.html'
    context_object_name = 'module'
    slug_field = 'app_name'
    slug_url_kwarg = 'app_name'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        module_service = ModuleService()
        
        # Valida dependências
        dependencies_info = module_service.validate_module_dependencies(
            self.object.app_name
        )
        
        # Busca módulos dependentes
        dependent_modules = self.object.get_dependent_modules()
        
        context.update({
            'dependencies_info': dependencies_info,
            'dependent_modules': dependent_modules,
            'page_title': f'Módulo: {self.object.display_name}',
        })
        return context


class ModuleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Edita configurações de um módulo"""
    model = AppModuleConfiguration
    form_class = ModuleConfigurationForm
    template_name = 'config/modules/update.html'
    slug_field = 'app_name'
    slug_url_kwarg = 'app_name'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(
            self.request,
            f'Módulo "{form.instance.display_name}" atualizado com sucesso!'
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        from django.urls import reverse
        return reverse('config:module_detail', kwargs={'app_name': self.object.app_name})


class ModuleToggleView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Habilita/desabilita um módulo"""
    
    def test_func(self):
        return self.request.user.is_staff
    
    def post(self, request, app_name):
        module_service = ModuleService()
        module = get_object_or_404(AppModuleConfiguration, app_name=app_name)
        
        # Não permite desabilitar módulos principais
        if module.is_core and not module.is_enabled:
            messages.error(
                request,
                f'O módulo "{module.display_name}" é principal e não pode ser desabilitado.'
            )
            return redirect('config:module_list')
        
        action = request.POST.get('action')
        success = False
        
        if action == 'enable':
            success = module_service.enable_module(app_name, request.user)
            action_text = 'habilitado'
        elif action == 'disable':
            success = module_service.disable_module(app_name, request.user)
            action_text = 'desabilitado'
        else:
            messages.error(request, 'Ação inválida.')
            return redirect('config:module_list')
        
        if success:
            messages.success(
                request,
                f'Módulo "{module.display_name}" {action_text} com sucesso!'
            )
        else:
            messages.error(
                request,
                f'Erro ao {action_text.replace("o", "ar")} o módulo "{module.display_name}".'
            )
        
        return redirect('config:module_list')


class ModuleSyncView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Sincroniza módulos com apps instalados"""
    
    def test_func(self):
        return self.request.user.is_staff
    
    def post(self, request):
        module_service = ModuleService()
        
        try:
            sync_result = module_service.sync_with_installed_apps(request.user)
            
            if sync_result['created']:
                messages.success(
                    request,
                    f'Sincronização concluída! Módulos criados: {", ".join(sync_result["created"])}'
                )
            else:
                messages.info(request, 'Sincronização concluída. Nenhum novo módulo encontrado.')
            
            if sync_result['missing']:
                messages.warning(
                    request,
                    f'Módulos sem app correspondente: {", ".join(sync_result["missing"])}'
                )
        
        except Exception as e:
            messages.error(request, f'Erro na sincronização: {str(e)}')
        
        return redirect('config:module_list')


class ModuleStatsAPIView(LoginRequiredMixin, UserPassesTestMixin, View):
    """API para estatísticas dos módulos"""
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get(self, request):
        module_service = ModuleService()
        stats = module_service.get_module_statistics()
        
        # Adiciona informações detalhadas
        modules_by_type = {}
        for module in AppModuleConfiguration.objects.all():
            module_type = module.get_module_type_display()
            if module_type not in modules_by_type:
                modules_by_type[module_type] = {'total': 0, 'enabled': 0}
            
            modules_by_type[module_type]['total'] += 1
            if module.is_enabled:
                modules_by_type[module_type]['enabled'] += 1
        
        stats['by_type'] = modules_by_type
        
        return JsonResponse(stats)


class ModuleDependencyCheckView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Verifica dependências de um módulo"""

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, app_name):
        module_service = ModuleService()
        dependencies_info = module_service.validate_module_dependencies(app_name)

        return JsonResponse(dependencies_info)
