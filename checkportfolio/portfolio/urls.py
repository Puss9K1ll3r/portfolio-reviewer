from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('upload/', views.upload, name='upload'),
    path('teacher-login/', views.teacherLogin, name='teacher-login'),
    path('teacher-action/', views.teacherAction, name='teacher-action'),
    
    # API endpoints
    path('api/add-subject/', views.add_subject, name='add-subject'),
    path('api/update-subject/<int:subject_id>/', views.update_subject, name='update-subject'),
    path('api/delete-subject/<int:subject_id>/', views.delete_subject, name='delete-subject'),
]