from django.db import models
import uuid 
from django.core import validators
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext

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
    name = models.CharField(verbose_name=_('name'),max_length=200, blank=False,)
    surname = models.CharField(verbose_name=_('surname'),max_length=200, blank=False,)
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
    name = models.CharField(verbose_name=_('name'),max_length=200, blank=False, unique=True, error_messages={'unique':_('subject_already_registered')})

    def __str__(self) -> str:
        return self.name


class Topic(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    identifier = models.CharField(verbose_name=_('identifier'), max_length=200, blank=False, unique=True, error_messages={'unique':_('identifier_already_registered')})
    name = models.CharField(verbose_name=_('name'), max_length=200, blank=True, error_messages={'unique':_('topic_already_registered')})
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, verbose_name=_('subject'))
    questions = models.ManyToManyField('Question', through='QuestionToTopic')
    video_lectures = models.ManyToManyField('VideoLecture', through='VideoToTopic')

    def __str__(self) -> str:
        return self.name


QUESTION_TYPE_CHOICES = [
        ('single_choice', _('single_choice')),
        ('multiple_choice', _('multiple_choice')),
        ('open_end', _('open_end')),
    ]

class Question(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    question_id = models.IntegerField(unique=True, verbose_name=_('question_id'))
    text = models.TextField(verbose_name=_('text'), blank=False, error_messages={'unique':_('question_text_already_exists')})
    question_type = models.CharField(verbose_name=_('question_type'), max_length=20, choices=QUESTION_TYPE_CHOICES, default='single_choice')
    topics = models.ManyToManyField(Topic, through='QuestionToTopic')

    def __str__(self):
        return self.text


class QuestionToTopic(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, blank=False, verbose_name=_('question'))
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, blank=False, verbose_name=_('topic'))

    class Meta:
        unique_together = ('question', 'topic')



class QuestionChoice(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, blank=False, verbose_name=_('question'))
    text = models.CharField(max_length=255, blank=False, verbose_name=_('text'))
    is_correct = models.BooleanField(default=False, verbose_name=_('is_correct'))

    def __str__(self):
        return self.text


class VideoLecture(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    url = models.CharField(max_length=255, blank=False, verbose_name=_('url'), unique=True, error_messages={'unique':_('question_text_already_exists')})
    title = models.CharField(max_length=255, verbose_name=_('title'),)
    description = models.CharField(max_length=255, verbose_name=_('description'),)
    topics = models.ManyToManyField(Topic, through='VideoToTopic')
    subjects = models.ManyToManyField(Subject, through='VideoToSubject')

    def __str__(self):
        return self.url


class VideoToSubject(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    video_lecture = models.ForeignKey(VideoLecture, on_delete=models.CASCADE, blank=False, verbose_name=_('video_lecture'))
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, blank=False, verbose_name=_('topic'))


class VideoToTopic(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    video_lecture = models.ForeignKey(VideoLecture, on_delete=models.CASCADE, blank=False, verbose_name=_('video_lecture'))
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, blank=False, verbose_name=_('topic'))

    class Meta:
        unique_together = ('video_lecture', 'topic')
    

# TODO: Implement Messates
class Message(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    severity = models.IntegerField(default=0)
    description = models.CharField(verbose_name=_('description'),max_length=200, blank=True, default="")
    has_read = models.BooleanField(verbose_name=_('has_read'), default=False)
    date_created = models.DateField(verbose_name=_('date_created'), auto_now_add=True, blank=True)
