from django.urls import path
from apps.articles.views import (
    ArticleListView,
    ArticleDetailView,
    ArticleSearchView,
    # CategoryDetailView,
    # CategoryListView,
    # TagDetailView,
    # TagListView,
)

app_name = 'articles'

urlpatterns = [
    # Artigos
    path('', ArticleListView.as_view(), name='article_list'),
    path('busca/', ArticleSearchView.as_view(), name='search'),
    path('<slug:slug>/', ArticleDetailView.as_view(), name='article_detail'),
    
    # Categorias (implementar depois)
    # path('categoria/', CategoryListView.as_view(), name='category_list'),
    # path('categoria/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    
    # Tags (implementar depois)
    # path('tag/', TagListView.as_view(), name='tag_list'),
    # path('tag/<slug:slug>/', TagDetailView.as_view(), name='tag_detail'),
]
