import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'checkportfolio.settings')
django.setup()

from portfolio.models import Teacher, TeacherData

teacher = Teacher.objects.create(name="Иванов Иван Иванович")

user = TeacherData.objects.create_user(
    username='ivanov',
    password='password123'
)
user.teacher_profile = teacher
user.save()

print(f"Создан пользователь {user.username} с привязкой к преподавателю {teacher.name}")