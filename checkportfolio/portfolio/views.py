from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import LoginForm
# Create your views here.

def index(request):
    
    return render(request, 'portfolio/index.html', {'title': 'Welcome'})

def upload(request):
    return render(request, 'portfolio/upload.html', {'title': 'Upload'})

def teacherLogin(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('teacher-action')
    else:
        form = LoginForm()
    
    return render(request, 'portfolio/auth.html', {
        'title': 'Log In',
        'form': form
    })

@login_required
def teacherAction(request):
    teacher_name = None
    if hasattr(request.user, 'teacher_profile'):
        teacher_name = request.user.teacher_profile.name
    
    return render(request, 'portfolio/teacher_action.html', {
        'title': 'Личный кабинет',
        'teacher_name': teacher_name
    })

