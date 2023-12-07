from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
from app_teacher.models import Classroom, Test
from base.models import User, Question, QuestionChoice


class StudentProfile(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE,)
    profile_picture = models.CharField(max_length=200, blank=True, default="", verbose_name=_('profile_picture'))
    phone_number =  models.CharField(max_length=200, blank=True, default="", verbose_name=_('phone_number'))
    school_year = models.IntegerField(blank=True, default=0, verbose_name=_('school_year'))
    tests = models.ManyToManyField(Test, through='StudentTest')


class StudentTest(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    start_time = models.DateField(auto_now_add=True, blank=True, verbose_name=_('test_start_time'))
    end_time = models.DateField(auto_now_add=True, blank=True, verbose_name=_('test_end_time'))

    def __str__(self):
        return f"{self.student.user.username}'s attempt at {self.test.name}"


class StudentAnswer(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)

    student_test = models.ForeignKey(StudentTest, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    chosen_choices = models.ManyToManyField(QuestionChoice)
    text_response = models.TextField(blank=True, null=True)
    given_point = models.IntegerField(default=0, blank=True)
    answered = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.student_test.student.user.username}'s answer to {self.question.text}"



# Create your models here.
class StudentToClassroom(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)

    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name=_('student'))
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, null=True, verbose_name=_('classroom'))

    class Meta:
        unique_together = ('student', 'classroom')
