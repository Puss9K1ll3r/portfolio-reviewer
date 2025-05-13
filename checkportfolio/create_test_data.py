import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'checkportfolio.settings')
django.setup()

from portfolio.models import TeacherData, Teacher, Subject
from django.contrib.auth.hashers import make_password

def create_test_data():
    # 1. Создаем тестового пользователя (учителя)
    teacher_user = TeacherData.objects.create(
        username='teacher_2',
        password=make_password('teacher123'),
        is_staff=True,
        is_active=True
    )
    
    # 2. Создаем запись в Teacher
    teacher = Teacher.objects.create(
        user=teacher_user,
        name="Иванов Иван Иванович"
    )
    
    # # 3. Создаем несколько тестовых предметов
    # subjects = [
    #     {
    #         'subject_id': 1,
    #         'title': 'Математика',
    #         'abbr': 'Мат',
    #         'files_count': 10,
    #         'review_params': 'Точность вычислений, логичность рассуждений',
    #         'changer': teacher
    #     },
    #     {
    #         'subject_id': 2,
    #         'title': 'Физика',
    #         'abbr': 'Физ',
    #         'files_count': 8,
    #         'review_params': 'Правильность формул, единицы измерения',
    #         'changer': teacher
    #     },
    #     {
    #         'subject_id': 3,
    #         'title': 'Информатика',
    #         'abbr': 'Инф',
    #         'files_count': 15,
    #         'review_params': 'Корректность кода, комментарии',
    #         'changer': teacher
    #     }
    # ]
    
    # for subj in subjects:
    #     Subject.objects.create(**subj)
    
    print("Тестовые данные созданы успешно!")
    # print(f"Логин: test_teacher, Пароль: teacher123")

if __name__ == '__main__':
    create_test_data()