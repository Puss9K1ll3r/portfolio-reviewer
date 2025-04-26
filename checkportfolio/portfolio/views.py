from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'portfolio/index.html', {'title': 'Welcome'})

def upload(request):
    return render(request, 'portfolio/upload.html', {'title': 'Upload'})

def teacherLogin(request):
    return render(request, 'portfolio/auth.html', {'title': 'Log In'})

def pageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")