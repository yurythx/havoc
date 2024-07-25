

from django.urls import path 
from config import views

urlpatterns = [
    path('', views.index_config, name='index-config'), 
]


