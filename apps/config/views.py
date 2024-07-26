from django.shortcuts import render

def index_config(request):

    return render(request, 'index_config.html')




















# UI seccion

def ui_buttons(request):

    return render(request, 'ui/ui-buttons.html')

def ui_cards(request):

    return render(request, 'ui/ui-cards.html')

def ui_colors(request):

    return render(request, 'ui/ui-colors.html')

def ui_form_components(request):

    return render(request, 'ui/ui-form-components.html')

def ui_icons(request):

    return render(request, 'ui/ui-icons.html')

def ui_typography(request):

    return render(request, 'ui/ui-typography.html')

def ui_tables(request):

    return render(request, 'ui/ui-tables.html')

def ui_components(request):

    return render(request, 'ui/ui-components.html')

def forms_config(request):

    return render(request, 'forms.html')


def maps_config(request):

    return render(request, 'maps.html')

def charts_config(request):

    return render(request, 'charts.html')

