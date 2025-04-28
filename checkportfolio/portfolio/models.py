from enum import Enum
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class TeacherData(AbstractUser):
    teacher_profile = models.OneToOneField(
        'Teacher', 
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='user_account'
    )
    
    def __str__(self):
        return self.username

class Teacher(models.Model):
    name = models.TextField()
    
    def __str__(self):
        return self.name

class Subject(models.Model):
    class Operations(Enum):
        CREATE = "CREATE"
        UPDATE = "UPDATE"
        DELETE = "DELETE"

        @classmethod
        def choices(cls):
            return [(key.value, key.name) for key in cls]

    subject_id = models.IntegerField()    
    title = models.CharField(max_length=255, blank=False)
    abbr = models.CharField(max_length=255, blank=False)
    files_count = models.IntegerField()
    review_params = models.CharField(max_length=255, blank=True)
    changer = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    time_update = models.DateTimeField((""), auto_now=True, auto_now_add=False)
    operation_type = models.CharField(
        max_length=20,
        choices=Operations.choices(),
        default=Operations.CREATE.value
    )
    
