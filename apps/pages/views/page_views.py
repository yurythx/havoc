from django.shortcuts import render, get_object_or_404
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Q
from apps.pages.services.page_service import PageService
from apps.pages.repositories.page_repository import DjangoPageRepository
from apps.pages.models import Page

class PageDetailView(View):
    """View para exibir detalhes de uma página"""
    
    def get(self, request, slug):
        """Exibe uma página específica"""
        # Inicializa service
        page_service = PageService(DjangoPageRepository())
        
        try:
            # Obtém a página
            page = page_service.get_page_by_slug(slug)
            
            # Incrementa contador de visualizações
            page_service.increment_page_views(page.id)
            
            # Obtém breadcrumbs
            breadcrumbs = page_service.get_breadcrumbs(page)
            
            # Obtém páginas filhas se existirem
            children = page.get_children()
            
            # Obtém páginas relacionadas (mesmo nível hierárquico)
            related_pages = []
            if page.parent:
                related_pages = page.parent.get_children().exclude(id=page.id)[:3]
            
            context = {
                'page': page,
                'breadcrumbs': breadcrumbs,
                'children': children,
                'related_pages': related_pages,
                'meta_title': page.seo_title,
                'meta_description': page.seo_description,
                'meta_keywords': page.meta_keywords,
            }
            
            # Usa template personalizado se definido
            template = page.template if page.template else 'pages/page_detail.html'
            
            return render(request, template, context)
            
        except Exception as e:
            # Página não encontrada
            context = {
                'error': 'Página não encontrada',
                'slug': slug,
                'meta_title': 'Página não encontrada',
                'meta_description': 'A página solicitada não foi encontrada',
            }
            return render(request, 'pages/404.html', context, status=404)


class PageListView(View):
    """View para listar páginas"""
    template_name = 'pages/page_list.html'
    
    def get(self, request):
        """Lista páginas com busca e paginação"""
        # Inicializa service
        page_service = PageService(DjangoPageRepository())
        
        # Obtém parâmetros de busca
        query = request.GET.get('q', '').strip()
        
        # Busca ou lista todas as páginas
        if query:
            pages = page_service.search_pages(query)
        else:
            pages = page_service.get_published_pages()
        
        # Paginação
        paginator = Paginator(pages, 12)  # 12 páginas por página
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Obtém páginas populares para sidebar
        popular_pages = page_service.get_popular_pages(limit=5)
        
        context = {
            'page_obj': page_obj,
            'pages': page_obj.object_list,
            'query': query,
            'popular_pages': popular_pages,
            'meta_title': f'Páginas{" - " + query if query else ""}',
            'meta_description': 'Lista de páginas do site',
        }
        
        return render(request, self.template_name, context)


class PageSearchView(View):
    """View para busca de páginas"""
    template_name = 'pages/search_results.html'
    
    def get(self, request):
        """Busca páginas"""
        query = request.GET.get('q', '').strip()
        
        if not query:
            context = {
                'query': '',
                'pages': [],
                'total_results': 0,
                'meta_title': 'Busca',
                'meta_description': 'Busque por páginas no site',
            }
            return render(request, self.template_name, context)
        
        # Inicializa service
        page_service = PageService(DjangoPageRepository())
        
        # Busca páginas
        pages = page_service.search_pages(query)
        
        # Paginação
        paginator = Paginator(pages, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'query': query,
            'page_obj': page_obj,
            'pages': page_obj.object_list,
            'total_results': paginator.count,
            'meta_title': f'Busca por "{query}"',
            'meta_description': f'Resultados da busca por "{query}"',
        }
        
        return render(request, self.template_name, context)
