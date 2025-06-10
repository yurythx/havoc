# Importa views da pasta views
from .views.home import HomeView
from .views.static_pages import AboutView, ContactView, PrivacyView, TermsView
from .views.page_views import PageDetailView, PageListView, PageSearchView

__all__ = [
    'HomeView',
    'AboutView',
    'ContactView',
    'PrivacyView',
    'TermsView',
    'PageDetailView',
    'PageListView',
    'PageSearchView',
]
