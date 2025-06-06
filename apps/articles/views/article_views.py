from django.shortcuts import render
from django.views import View
from django.core.paginator import Paginator
from apps.articles.services.article_service import ArticleService
from apps.articles.repositories.article_repository import DjangoArticleRepository

class ArticleListView(View):
    """View para listar artigos"""
    template_name = 'articles/article_list.html'
    
    def get(self, request):
        """Lista artigos com paginação"""
        # Inicializa service
        article_service = ArticleService(DjangoArticleRepository())
        
        # Obtém artigos publicados
        articles = article_service.get_published_articles()
        
        # Paginação
        paginator = Paginator(articles, 12)  # 12 artigos por página
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Obtém artigos em destaque para sidebar
        featured_articles = article_service.get_featured_articles(limit=3)
        
        context = {
            'page_obj': page_obj,
            'articles': page_obj.object_list,
            'featured_articles': featured_articles,
            'meta_title': 'Artigos',
            'meta_description': 'Todos os artigos do blog',
        }
        
        return render(request, self.template_name, context)


class ArticleDetailView(View):
    """View para exibir detalhes de um artigo"""
    
    def get(self, request, slug):
        """Exibe um artigo específico"""
        # Inicializa service
        article_service = ArticleService(DjangoArticleRepository())
        
        try:
            # Obtém o artigo
            article = article_service.get_article_by_slug(slug)
            
            # Incrementa contador de visualizações
            article_service.increment_article_views(article.id)
            
            # Obtém artigos relacionados
            related_articles = article_service.get_related_articles(article, limit=3)
            
            # Obtém comentários (se implementado)
            # comments = comment_service.get_article_comments(article.id)
            
            context = {
                'article': article,
                'related_articles': related_articles,
                # 'comments': comments,
                'meta_title': article.seo_title,
                'meta_description': article.seo_description,
                'meta_keywords': article.meta_keywords,
            }
            
            # Usa template personalizado se definido
            template = 'articles/article_detail.html'
            
            return render(request, template, context)
            
        except Exception as e:
            # Artigo não encontrado
            context = {
                'error': 'Artigo não encontrado',
                'slug': slug,
                'meta_title': 'Artigo não encontrado',
                'meta_description': 'O artigo solicitado não foi encontrado',
            }
            return render(request, 'articles/404.html', context, status=404)


class ArticleSearchView(View):
    """View para busca de artigos"""
    template_name = 'articles/search_results.html'
    
    def get(self, request):
        """Busca artigos"""
        query = request.GET.get('q', '').strip()
        
        if not query:
            context = {
                'query': '',
                'articles': [],
                'total_results': 0,
                'meta_title': 'Busca de Artigos',
                'meta_description': 'Busque por artigos no blog',
            }
            return render(request, self.template_name, context)
        
        # Inicializa service
        article_service = ArticleService(DjangoArticleRepository())
        
        # Busca artigos
        articles = article_service.search_articles(query)
        
        # Paginação
        paginator = Paginator(articles, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'query': query,
            'page_obj': page_obj,
            'articles': page_obj.object_list,
            'total_results': paginator.count,
            'meta_title': f'Busca por "{query}"',
            'meta_description': f'Resultados da busca por "{query}"',
        }
        
        return render(request, self.template_name, context)
