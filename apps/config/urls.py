

from django.urls import path 
from config import views

urlpatterns = [
    path('', views.index_config, name='index-config'),
    


    # UI seccion
    path('ui-buttons/', views.ui_buttons, name='ui-buttons'), 
    path('ui-cards/', views.ui_cards, name='ui-cards'), 
    path('ui-colors/', views.ui_colors, name='ui-colors'), 
    path('ui-form-components/', views.ui_form_components, name='ui-form-components'), 
    path('ui-icons/', views.ui_icons, name='ui-icons'), 
    path('ui-typography/', views.ui_typography, name='ui-typography'), 
    path('ui-tables/', views.ui_tables, name='ui-tables'), 
    path('ui-components/', views.ui_components, name='ui-components'), 
    path('forms_config/', views.forms_config, name='forms_config'), 
    path('maps_config/', views.maps_config, name='maps_config'),
    path('charts_config/', views.charts_config, name='charts_config'),    



]


