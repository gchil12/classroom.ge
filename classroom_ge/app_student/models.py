from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
from app_teacher.models import Classroom, Test, TestQuestion
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

    start_time = models.DateTimeField(blank=True, verbose_name=_('test_start_time'),)
    end_time = models.DateTimeField(blank=True, verbose_name=_('test_end_time'),)


    class Meta:
        unique_together = ('student', 'test')

    
    def __str__(self):
        return f"{self.student.user.name}'s attempt at {self.test.name}"


class StudentQuestion(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)

    student_test = models.ForeignKey(StudentTest, on_delete=models.CASCADE)
    question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE)
    text_response = models.TextField(blank=True, null=True)
    given_point = models.IntegerField(default=0, blank=True)
    
    # Points given by GPT
    submitted_to_gpt = models.BooleanField(default=False, blank=True, null=True)
    gpt_knowledge = models.FloatField(default=None, blank=True, null=True)
    gpt_reasoning = models.FloatField(default=None, blank=True, null=True)
    gpt_formulation  = models.FloatField(default=None, blank=True, null=True)

    # Teacher corrected version of the points given by GPT
    teacher_knowledge = models.FloatField(default=None, blank=True, null=True)
    teacher_reasoning = models.FloatField(default=None, blank=True, null=True)
    teacher_formulation  = models.FloatField(default=None, blank=True, null=True)
    
    answered = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    chosen_choices = models.ManyToManyField(QuestionChoice, through='StudentQuestionToChoice')
    
    def __str__(self):
        return f"{self.student_test.student.user.name}'s answer to {self.question.question.text}"


class StudentQuestionToChoice(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    student_question = models.ForeignKey(StudentQuestion, on_delete=models.CASCADE)
    choice = models.ForeignKey(QuestionChoice, on_delete=models.CASCADE)


class StudentToClassroom(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)

    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name=_('student'))
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, null=True, verbose_name=_('classroom'))

    class Meta:
        unique_together = ('student', 'classroom')
