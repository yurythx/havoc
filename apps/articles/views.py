# Importa views da pasta views
from .views.article_views import (
    ArticleListView,
    ArticleDetailView,
    ArticleSearchView,
    ArticleCreateView,
    ArticleUpdateView,
    ArticleDeleteView
)

__all__ = [
    'ArticleListView',
    'ArticleDetailView',
    'ArticleSearchView',
    'ArticleCreateView',
    'ArticleUpdateView',
    'ArticleDeleteView',
]
