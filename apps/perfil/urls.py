from django.urls import path 
from perfil import views

urlpatterns = [
    path('', views.index_perfil, name='perfil'), 
]


