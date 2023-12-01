from django.db import models
import uuid
from base.models import User
from base.models import Subject
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Classroom(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name=_('owner'))
    name = models.CharField(max_length=200, blank=False, null=False, unique=False, verbose_name=_('name'))
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, verbose_name=_('subject'))
    description = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('description'))

    date_created = models.DateField(auto_now_add=True, blank=True, verbose_name=_('date_created'))
    is_archived = models.BooleanField(default=False, verbose_name=_('is_archived'))


class Lesson(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)

    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, null=True, verbose_name=_('classroom'))
    name = models.CharField(max_length=200, blank=False, null=False, unique=False, verbose_name=_('name'))
    description = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('description'))
    date_created = models.DateField(auto_now_add=True, blank=True, verbose_name=_('date_created'))


class Test(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, verbose_name=_('lesson'))
    name = models.CharField(max_length=200, blank=False, null=False, unique=False, verbose_name=_('name'))
    description = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('description'))
    is_graded = models.BooleanField(default=False, verbose_name=_('is_graded'))
    date_created = models.DateField(auto_now_add=True, blank=True, verbose_name=_('date_created'))


class TestVariant(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)

    test = models.ForeignKey(Test, on_delete=models.CASCADE, null=True, verbose_name=_('test'))
    name = models.CharField(max_length=200, blank=False, null=False, unique=False, verbose_name=_('name'))


class Questions(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)

    name = models.CharField(max_length=200, blank=False, null=False, unique=False, verbose_name=_('name'))

    # TODO Rest


class TestQuestion(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)

    test_variant = models.ForeignKey(TestVariant, on_delete=models.CASCADE, null=True, verbose_name=_('test_variant'))
    question = models.ForeignKey(Questions, on_delete=models.CASCADE, null=True, verbose_name=_('question'))

    max_point = models.DecimalField(blank=False, default=0, max_digits=10, decimal_places=2, verbose_name=_('max_point'))