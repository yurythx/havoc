from django.shortcuts import render
from django.views import View
from django.http import Http404
from apps.pages.services.page_service import PageService
from apps.pages.repositories.page_repository import DjangoPageRepository

class HomeView(View):
    """View para a página inicial"""
    
    def get(self, request):
        """Exibe a página inicial"""
        # Inicializa service
        page_service = PageService(DjangoPageRepository())
        
        try:
            # Obtém a homepage
            homepage = page_service.get_homepage()
            
            if not homepage:
                # Se não há homepage, renderiza template padrão
                context = {
                    'page': None,
                    'is_homepage': True,
                    'meta_title': 'Bem-vindo ao Havoc',
                    'meta_description': 'Sistema de gerenciamento de conteúdo',
                }
                return render(request, 'pages/home_default.html', context)
            
            # Incrementa contador de visualizações
            page_service.increment_page_views(homepage.id)
            
            # Obtém páginas populares para exibir na home
            popular_pages = page_service.get_popular_pages(limit=5)
            
            # Obtém páginas recentes
            recent_pages = page_service.get_published_pages()[:5]
            
            context = {
                'page': homepage,
                'is_homepage': True,
                'popular_pages': popular_pages,
                'recent_pages': recent_pages,
                'meta_title': homepage.seo_title,
                'meta_description': homepage.seo_description,
                'meta_keywords': homepage.meta_keywords,
            }
            
            # Usa template personalizado se definido
            template = homepage.template if homepage.template else 'pages/home.html'
            
            return render(request, template, context)
            
        except Exception as e:
            # Em caso de erro, renderiza página padrão
            context = {
                'page': None,
                'is_homepage': True,
                'error': str(e),
                'meta_title': 'Havoc - Sistema de Gerenciamento',
                'meta_description': 'Sistema de gerenciamento de conteúdo',
            }
            return render(request, 'pages/home_default.html', context)
