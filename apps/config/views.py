from django.shortcuts import render


def index_config(request):

    return render(request, 'base_config.html')
