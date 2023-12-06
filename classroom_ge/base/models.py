from django.db import models
import uuid 
from django.core import validators
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
import datetime

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)

    username = None
    name = models.CharField(verbose_name=_('name'),max_length=200, blank=False, null=False)
    surname = models.CharField(verbose_name=_('surname'),max_length=200, blank=False, null=False)
    date_of_birth = models.DateField(verbose_name=_('date_of_birth'), blank=False, default='0001-01-01')
    school = models.CharField(verbose_name=_('school'),max_length=200, blank=False, default='N/A')
    city = models.CharField(verbose_name=_('city'),max_length=200, blank=False, default='N/A')

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

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    objects = CustomUserManager()


    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")



class Subject(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    name = models.CharField(verbose_name=_('name'),max_length=200, blank=False, null=False, unique=True, error_messages={'unique':_('subject_already_registered')})

    def __str__(self) -> str:
        return self.name


class Topic(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    identifier = models.CharField(verbose_name=_('identifier'), max_length=200, blank=False, null=False, unique=True, error_messages={'unique':_('identifier_already_registered')})
    name = models.CharField(verbose_name=_('name'), max_length=200, blank=True, error_messages={'unique':_('topic_already_registered')})

    def __str__(self) -> str:
        return self.name


class MultipleChoiceQuestion(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    id = models.IntegerField(blank=False, null=False, unique=True, error_messages={'unique':_('id_already_exists')}, verbose_name=_('id'))
    text = models.CharField(verbose_name=_('text'), max_length=200, blank=False, null=False, unique=True, error_messages={'unique':_('question_text_is_already_in_database')})
    n_choices = models.IntegerField(blank=False, null=False, verbose_name=_('number_of_choices'))
    choices = models.CharField(verbose_name=_('multiple_choice_question_choices'), max_length=200, blank=False, null=False,)
    correct_answer = models.IntegerField(verbose_name=_('multiple_choice_question_answer'), blank=False, null=False,)


class MultipleChoiceQuestionToTopics(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    question = models.ForeignKey(MultipleChoiceQuestion, on_delete=models.CASCADE, null=True, verbose_name=_('question'))
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, verbose_name=_('topic'))



# TODO: Implement Messates
class Message(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    severity = models.IntegerField(default=0)
    description = models.CharField(verbose_name=_('description'),max_length=200, blank=True, default="")
    has_read = models.BooleanField(verbose_name=_('has_read'), default=False)
    date_created = models.DateField(verbose_name=_('date_created'), auto_now_add=True, blank=True)
