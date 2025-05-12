from enum import Enum
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

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
    user = models.OneToOneField(TeacherData, on_delete=models.CASCADE)
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

    subject_id = models.IntegerField(default=1)    
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

@receiver(post_save, sender=Subject)
def create_subject_history(sender, instance, created, **kwargs):
    operation = Subject.Operations.CREATE.value if created else Subject.Operations.UPDATE.value
    SubjectHistory.objects.create(
        subject_id=instance.id,
        title=instance.title,
        abbr=instance.abbr,
        files_count=instance.files_count,
        review_params=instance.review_params,
        changer=instance.changer,
        operation_type=operation
    )

@receiver(pre_delete, sender=Subject)
def log_deleted_subject(sender, instance, **kwargs):
    SubjectHistory.objects.create(
        subject_id=instance.id,
        title=instance.title,
        abbr=instance.abbr,
        files_count=instance.files_count,
        review_params=instance.review_params,
        changer=instance.changer,
        operation_type=Subject.Operations.DELETE.value
    )
    
class SubjectHistory(models.Model):
    subject_id = models.IntegerField()
    title = models.CharField(max_length=255)
    abbr = models.CharField(max_length=255)
    files_count = models.IntegerField()
    review_params = models.CharField(max_length=255, blank=True)
    changer = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    time_update = models.DateTimeField(auto_now_add=True)
    operation_type = models.CharField(max_length=20, choices=Subject.Operations.choices())
    
    class Meta:
        ordering = ['-time_update']
    
    def get_operation_display(self):
        return dict(Subject.Operations.choices()).get(self.operation_type, self.operation_type)