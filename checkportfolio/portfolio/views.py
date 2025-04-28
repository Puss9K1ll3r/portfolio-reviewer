from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from .forms import LoginForm
from .models import Subject, Teacher
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
import subprocess
import os
from django.conf import settings

def index(request):
    return render(request, 'portfolio/index.html', {'title': 'Welcome'})

def upload(request):
    result = None
    
    if request.method == 'POST':
        # Получаем данные из формы
        student_name = request.POST.get('student_name', '')
        student_group = request.POST.get('student_group', '')
        subject_abbr = request.POST.get('subject_abbr', '')
        works_count = request.POST.get('works_count', '0')
        archive_file = request.FILES.get('archive_file', None)
        
        # Проверяем обязательные поля
        if not all([student_name, student_group, subject_abbr, archive_file]):
            result = {
                'success': False,
                'errors': ['Пожалуйста, заполните все обязательные поля.']
            }
        else:
            try:
                # Создаем временный файл для хранения данных
                temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_uploads')
                os.makedirs(temp_dir, exist_ok=True)
                
                temp_file_path = os.path.join(temp_dir, 'form_data.txt')
                with open(temp_file_path, 'w', encoding='utf-8') as f:
                    f.write(f"ФИО: {student_name}\n")
                    f.write(f"Группа: {student_group}\n")
                    f.write(f"Предмет: {subject_abbr}\n")
                    f.write(f"Количество работ: {works_count}\n")
                    f.write(f"Имя файла: {archive_file.name}\n")
                
                # Сохраняем загруженный файл
                archive_path = os.path.join(temp_dir, archive_file.name)
                with open(archive_path, 'wb+') as destination:
                    for chunk in archive_file.chunks():
                        destination.write(chunk)
                
                # Запускаем Python-скрипт для обработки данных
                script_path = os.path.join(settings.BASE_DIR, 'portfolio', 'process_portfolio.py')
                process = subprocess.Popen(
                    ['python', script_path, temp_file_path, archive_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    result = {
                        'success': True,
                        'message': f"Данные успешно обработаны:\n{stdout}"
                    }
                else:
                    result = {
                        'success': False,
                        'errors': [f"Ошибка при обработке данных: {stderr}"]
                    }
                
            except Exception as e:
                result = {
                    'success': False,
                    'errors': [f"Произошла ошибка: {str(e)}"]
                }
            finally:
                # Удаляем временные файлы (можно закомментировать для отладки)
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                if os.path.exists(archive_path):
                    os.remove(archive_path)
    
    return render(request, 'portfolio/upload.html', {
        'title': 'Upload',
        'result': result
    })

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
    # Получаем все предметы
    subjects = Subject.objects.all().order_by('title')
    
    # Получаем связанного преподавателя (если есть)
    teacher_name = None
    try:
        teacher = Teacher.objects.get(user=request.user)
        teacher_name = teacher.name
    except Teacher.DoesNotExist:
        pass
    
    return render(request, 'portfolio/teacher_action.html', {
        'title': 'Личный кабинет',
        'teacher_name': teacher_name,
        'subjects': subjects
    })

@login_required
@require_POST
def add_subject(request):
    try:
        teacher = Teacher.objects.get(user=request.user)

        subject = Subject(
            title=request.POST.get('title'),
            abbr=request.POST.get('abbr'),
            files_count=request.POST.get('files_count'),
            review_params=request.POST.get('review_params', ''),
            changer=teacher
        )
        subject.save()
        
        return JsonResponse({'success': True, 'id': subject.id})
    except Teacher.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Только преподаватели могут добавлять предметы'}, status=403)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_POST
def update_subject(request, subject_id):
    try:
        teacher = Teacher.objects.get(user=request.user)

        subject = Subject.objects.get(id=subject_id)
        
        subject.title = request.POST.get('title')
        subject.abbr = request.POST.get('abbr')
        subject.files_count = request.POST.get('files_count')
        subject.review_params = request.POST.get('review_params', '')
        subject.changer = teacher
        subject.save()
        
        return JsonResponse({'success': True})
    except Teacher.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Только преподаватели могут редактировать предметы'}, status=403)
    except Subject.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Предмет не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    

@login_required
@require_POST
def delete_subject(request, subject_id):
    try:
        Teacher.objects.get(user=request.user)
        
        subject = Subject.objects.get(id=subject_id)
        subject.delete()
        
        return JsonResponse({'success': True})
    except Teacher.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Только преподаватели могут удалять предметы'}, status=403)
    except Subject.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Предмет не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)