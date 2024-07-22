from django.shortcuts import render

def index_blog(request):

    return render(request, 'index_blog.html')