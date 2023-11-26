from django.db import models
import uuid
from base.models import User
from base.models import Subject
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Classroom(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(verbose_name=_('name'),max_length=200, blank=False, null=False, unique=False)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    description = models.CharField(verbose_name=_('description'),max_length=200, blank=True, null=True)

    date_created = models.DateField(verbose_name=_('date_created'), auto_now_add=True, blank=True)
    is_archived = models.BooleanField(verbose_name=_('is_archived'), default=False)


class Lesson(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)

    classroom = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True)
    name = models.CharField(verbose_name=_('name'),max_length=200, blank=False, null=False, unique=False)
    description = models.CharField(verbose_name=_('description'),max_length=200, blank=True, null=True)
    date_created = models.DateField(verbose_name=_('date_created'), auto_now_add=True, blank=True)


class Test(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True)
    name = models.CharField(verbose_name=_('name'),max_length=200, blank=False, null=False, unique=False)
    description = models.CharField(verbose_name=_('description'),max_length=200, blank=True, null=True)
    is_graded = models.BooleanField(verbose_name=_('is_graded'), default=False)
    date_created = models.DateField(verbose_name=_('date_created'), auto_now_add=True, blank=True)


class TestVariant(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    test = models.ForeignKey(Test, on_delete=models.SET_NULL, null=True)
    name = models.CharField(verbose_name=_('name'),max_length=200, blank=False, null=False, unique=False)


class Questions(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    name = models.CharField(verbose_name=_('name'),max_length=200, blank=False, null=False, unique=False)

    # TODO Rest


class TestQuestion(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    test_variant = models.ForeignKey(TestVariant, on_delete=models.SET_NULL, null=True)
    question = models.ForeignKey(Questions, on_delete=models.SET_NULL, null=True)

    max_point = models.DecimalField(blank=False, default=0, max_digits=10, decimal_places=2)