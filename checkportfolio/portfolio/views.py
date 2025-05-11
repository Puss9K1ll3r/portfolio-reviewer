import re
import zipfile
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import LoginForm
from .models import Subject, Teacher
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
import os
from django.conf import settings

def index(request):
    return render(request, 'portfolio/index.html', {'title': 'Welcome'})

def decode_archive_name(name):
    """Пытается декодировать имя файла из различных кодировок"""
    encodings = ['cp437', 'cp866', 'iso-8859-1', 'utf-8']
    
    for encoding in encodings:
        try:
            return name.encode(encoding).decode('cp866')
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
    
    # Если ни одна кодировка не подошла, возвращаем как есть
    return name

WORK_TYPES = {
    'ЛР': r'ЛР\d+(?:-\d+)?',  # Лабораторная работа (ЛР1, ЛР1-2)
    'ПР': r'ПР\d+(?:-\d+)?',  # Практическая работа
    'КП': r'КП',              # Курсовой проект
    'КР': r'КР',              # Курсовая работа
    'УП': r'УП\d*',           # Учебная практика
}

def validate_filename(filename, group, student_name, subject_abbr):
    """Проверяет соответствие имени файла требованиям"""
    # Проверяем основной формат: группа_Фамилия ИО_аббревиатура_тип_и_номер.pdf
    pattern = re.compile(
        r'^' + re.escape(group) + r'_' + 
        r'([А-ЯЁ][а-яё]+ [А-ЯЁ]{2})_' + 
        re.escape(subject_abbr) + r'_(' + 
        '|'.join(WORK_TYPES.values()) + r')\.pdf$',
        re.IGNORECASE
    )
    
    match = pattern.match(filename)
    if not match:
        return False
    
    file_surname_io = match.group(1)
    if file_surname_io != student_name:
        return False
    
    return True

def validate_portfolio_structure(zip_path, group, student_name, subject_abbr, expected_count):
    """Проверяет структуру портфолио с учетом различных кодировок"""
    errors = []
    found_files = []

    if not re.match(r'^[А-ЯЁ][а-яё]+ [А-ЯЁ]{2}$', student_name):
        errors.append("Неверный формат имени студента. Требуется: Фамилия ИО (например, 'Иванов ИИ')")
        return False, errors
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            decoded_group = decode_archive_name(group)
            decoded_name = decode_archive_name(student_name)
            decoded_subject = decode_archive_name(subject_abbr)
            
            # Проверяем структуру папок
            required_folders = [
                f"{group}/",
                f"{group}/{student_name}/",
                f"{group}/{student_name}/{subject_abbr}/"
            ]
            
            # Проверяем наличие всех обязательных папок
            found_required = [False] * len(required_folders)
            
            for zip_name in zip_ref.namelist():
                decoded_zip_name = decode_archive_name(zip_name)
                
                for i, folder in enumerate(required_folders):
                    if (zip_name.startswith(folder)) or (decoded_zip_name.startswith(decode_archive_name(folder))):
                        found_required[i] = True
            
            for i, folder in enumerate(required_folders):
                if not found_required[i]:
                    errors.append(f"Не найдена обязательная папка: {folder}")
            
            # Проверяем файлы в целевой папке
            target_files = []
            target_folder = f"{group}/{student_name}/{subject_abbr}/"
            decoded_target_folder = f"{decoded_group}/{decoded_name}/{decoded_subject}/"
            
            for zip_name in zip_ref.namelist():
                decoded_zip_name = decode_archive_name(zip_name)
                
                if ((zip_name.startswith(target_folder)) or 
                    decoded_zip_name.startswith(decoded_target_folder)) and not zip_name.endswith('/'):
                    target_files.append(zip_name)
            
            # Проверка количества файлов
            if len(target_files) != expected_count:
                errors.append(
                    f"Неверное количество файлов. Ожидалось: {expected_count}, найдено: {len(target_files)}"
                )
            
            # Проверка имен файлов
            valid_files = 0
            for file_path in target_files:
                filename = decode_archive_name(os.path.basename(file_path))
                if validate_filename(filename, group, student_name, subject_abbr):
                    valid_files += 1
                else:
                    # Формируем пример правильного имени
                    example_name = f"{group}_{student_name}_{subject_abbr}_ЛР1.pdf"
                    errors.append(
                        f"Неверный формат имени файла: {filename}\n"
                        f"Ожидается: {example_name}\n"
                    )
            
            if valid_files != expected_count:
                errors.append(f"Только {valid_files} из {expected_count} файлов имеют правильное имя")
    
    except Exception as e:
        errors.append(f"Ошибка при обработке архива: {str(e)}")
    
    return len(errors) == 0, errors

def save_portfolio(student_name, group, subject, archive_file):
    """Сохраняет портфолио с нормализованными именами"""
    # Нормализуем имена для сохранения
    normalized_name = re.sub(r'[^\w\-\.]', '_', student_name)
    normalized_group = re.sub(r'[^\w\-\.]', '_', group)
    normalized_subject = re.sub(r'[^\w\-\.]', '_', subject)
    
    save_path = os.path.join(
        'portfolios',
        normalized_group,
        normalized_name,
        # normalized_subject,
        archive_file.name
    )
    
    return default_storage.save(save_path, archive_file)

def upload(request):
    subjects = Subject.objects.all()
    result = None
    
    if request.method == 'POST':
        try:
            # Получаем и проверяем данные формы
            student_name = request.POST.get('student_name', '').strip()
            student_group = request.POST.get('student_group', '').strip()
            subject_id = request.POST.get('subject', '').strip()
            subject_abbr = request.POST.get('subject_abbr', '').strip()
            works_count = int(request.POST.get('works_count', '0'))
            archive_file = request.FILES.get('archive_file', None)
            
            # Базовые проверки
            if not all([student_name, student_group, subject_id, subject_abbr, works_count, archive_file]):
                raise ValueError('Пожалуйста, заполните все обязательные поля.')
            
            # Проверяем соответствие предмета в БД
            subject = Subject.objects.get(id=subject_id)
            if subject.abbr != subject_abbr or subject.files_count != works_count:
                raise ValueError('Несоответствие данных предмета')
            
            # Сохраняем временный файл
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_uploads')
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, archive_file.name)
            
            with open(temp_path, 'wb+') as destination:
                for chunk in archive_file.chunks():
                    destination.write(chunk)
            
            # Проверяем структуру портфолио
            is_valid, errors = validate_portfolio_structure(
                temp_path,
                student_group,
                student_name,
                subject_abbr,
                works_count
            )
            
            if not is_valid:
                raise ValueError('\n'.join(errors))
            
            # Сохраняем портфолио
            saved_path = save_portfolio(student_name, student_group, subject.title, archive_file)
            
            result = {
                'success': True,
                'message': f"Портфолио успешно принято и сохранено: {saved_path}"
            }
            
        except Subject.DoesNotExist:
            result = {
                'success': False,
                'errors': ['Выбранный предмет не найден']
            }
        except Exception as e:
            result = {
                'success': False,
                'errors': [str(e)]
            }
        finally:
            # Удаляем временный файл
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
    
    return render(request, 'portfolio/upload.html', {
        'title': 'Upload',
        'result': result,
        'subjects': subjects,
        'form_data': request.POST if request.method == 'POST' else None
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
    subjects = Subject.objects.all().order_by('title')
    
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