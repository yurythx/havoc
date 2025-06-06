from django.urls import path
from apps.pages.views import (
    HomeView,
    AboutView,
    ContactView,
    PrivacyView,
    TermsView,
    PageDetailView,
    PageListView,
    PageSearchView,
)

app_name = 'pages'

urlpatterns = [
    # Página inicial
    path('', HomeView.as_view(), name='home'),
    
    # Páginas estáticas
    path('sobre/', AboutView.as_view(), name='about'),
    path('contato/', ContactView.as_view(), name='contact'),
    path('privacidade/', PrivacyView.as_view(), name='privacy'),
    path('termos/', TermsView.as_view(), name='terms'),
    
    # Páginas dinâmicas
    path('paginas/', PageListView.as_view(), name='page_list'),
    path('busca/', PageSearchView.as_view(), name='search'),
    path('<slug:slug>/', PageDetailView.as_view(), name='page_detail'),
]
