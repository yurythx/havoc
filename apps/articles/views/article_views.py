from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from apps.articles.services.article_service import ArticleService
from apps.articles.repositories.article_repository import DjangoArticleRepository
from apps.articles.models.article import Article
from apps.articles.models.category import Category
from apps.articles.models.tag import Tag
from apps.articles.forms import ArticleForm

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


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin para verificar se o usuário é admin ou superuser"""

    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.is_superuser or
            self.request.user.is_staff
        )

    def handle_no_permission(self):
        messages.error(
            self.request,
            '🚫 Acesso negado! Apenas administradores podem realizar esta ação.'
        )
        return redirect('articles:article_list')


class ArticleCreateView(AdminRequiredMixin, CreateView):
    """View para criar novos artigos"""
    model = Article
    form_class = ArticleForm
    template_name = 'articles/article_form.html'

    def form_valid(self, form):
        """Define o autor como o usuário atual"""
        form.instance.author = self.request.user
        messages.success(
            self.request,
            f'✅ Artigo "{form.instance.title}" criado com sucesso!'
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Criar Novo Artigo',
            'submit_text': 'Criar Artigo',
            'categories': Category.objects.all(),
            'tags': Tag.objects.all(),
        })
        return context


class ArticleUpdateView(AdminRequiredMixin, UpdateView):
    """View para editar artigos"""
    model = Article
    form_class = ArticleForm
    template_name = 'articles/article_form.html'

    def form_valid(self, form):
        messages.success(
            self.request,
            f'✅ Artigo "{form.instance.title}" atualizado com sucesso!'
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': f'Editar: {self.object.title}',
            'submit_text': 'Salvar Alterações',
            'categories': Category.objects.all(),
            'tags': Tag.objects.all(),
        })
        return context


class ArticleDeleteView(AdminRequiredMixin, DeleteView):
    """View para deletar artigos"""
    model = Article
    template_name = 'articles/article_confirm_delete.html'
    success_url = reverse_lazy('articles:article_list')

    def delete(self, request, *args, **kwargs):
        article = self.get_object()
        messages.success(
            request,
            f'🗑️ Artigo "{article.title}" deletado com sucesso!'
        )
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Deletar: {self.object.title}'
        return context
