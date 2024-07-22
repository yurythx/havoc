from django.urls import path 
from base import views

urlpatterns = [
    path('', views.index_base, name='base'), 
]


