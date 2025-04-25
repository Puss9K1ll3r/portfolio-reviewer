from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'portfolio/index.html', {'title': 'Welcome'})

def upload(request):
    return HttpResponse("Страница для отправки")

def teacherLogin(request):
    return HttpResponse("Страница для преподавателя")

def pageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")