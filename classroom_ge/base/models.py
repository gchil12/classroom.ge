from django.db import models
import uuid 
from django.core import validators
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
import datetime

# Create your models here.
class User(AbstractUser):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)

    username = models.CharField(verbose_name=_('username'),max_length=200, blank=False, null=False, unique=True, error_messages={'unique':_('user_already_registered')})
    name = models.CharField(verbose_name=_('name'),max_length=200, blank=False, null=False)
    surname = models.CharField(verbose_name=_('surname'),max_length=200, blank=False, null=False)
    date_of_birth = models.DateField(verbose_name=_('date_of_birth'),blank=False, null=False)
    school = models.CharField(verbose_name=_('school'),max_length=200, blank=False, default=None)
    city = models.CharField(verbose_name=_('city'),max_length=200, blank=False, default=None)

    email_verified = models.BooleanField(verbose_name=_('email_verified'),default=False)

    is_student = models.BooleanField(verbose_name=_('is_student'), default=False)
    is_teacher = models.BooleanField(verbose_name=_('is_teacher'), default=False)
    is_moderator = models.BooleanField(verbose_name=_('is_moderator'), default=False)
    is_administrator = models.BooleanField(verbose_name=_('is_administrator'), default=False)

    email = models.CharField(
        _('email'),
        max_length=200,
        null=False,
        blank=False,
        validators=[validators.EmailValidator(message=_('invalid_email'))],
        unique=True,
        error_messages={'unique':_('email_already_registered')}
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name', 'surname']
    

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")



class Subject(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    name = models.CharField(verbose_name=_('name'),max_length=200, blank=False, null=False, unique=True, error_messages={'unique':_('subject_already_registered')})

    def __str__(self) -> str:
        return self.name


class Message(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    severity = models.IntegerField(default=0)
    description = models.CharField(verbose_name=_('description'),max_length=200, blank=True, null=True)
    has_read = models.BooleanField(verbose_name=_('has_read'), default=False)
    date_created = models.DateField(verbose_name=_('date_created'), auto_now_add=True, blank=True)