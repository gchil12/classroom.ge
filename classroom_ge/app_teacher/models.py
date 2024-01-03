from django.db import models
import uuid
from base.models import User, Subject, Question, VideoLecture
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class TeacherProfile(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.CharField(max_length=200, blank=True, default="", verbose_name=_('profile_picture'))
    phone_number =  models.CharField(max_length=200, blank=True, default="", verbose_name=_('phone_number'))
    

# Create your models here.
class Classroom(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name=_('owner'))
    name = models.CharField(max_length=200, blank=False, null=False, unique=False, default='', verbose_name=_('name'))
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, verbose_name=_('subject'))
    description = models.CharField(max_length=200, blank=True, default="", verbose_name=_('description'))
    online_meeting_link = models.CharField(max_length=200, blank=True, default="", verbose_name=_('online_meeging_link'))

    date_created = models.DateField(auto_now_add=True, blank=True, verbose_name=_('date_created'))
    is_archived = models.BooleanField(default=False, verbose_name=_('is_archived'))


class Level(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    level = models.CharField(blank=False, null=False, unique=True, default='-')


class ClassroomToLevels(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, blank=False, verbose_name=_('owner'))
    level = models.ForeignKey(Level, on_delete=models.CASCADE, blank=False, verbose_name=_('owner'))

    class Meta:
        # Set the combination of model1 and model2 to be unique
        unique_together = ('classroom', 'level')



class Lesson(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)

    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, null=True, verbose_name=_('classroom'))
    name = models.CharField(max_length=200, blank=False, null=False, unique=False, verbose_name=_('name'))
    description = models.CharField(max_length=200, blank=True, default="", verbose_name=_('description'))
    lesson_date = models.DateField(blank=False, null=True, verbose_name=_('lesson_date'))
    lesson_start_time = models.TimeField(blank=False, null=True, verbose_name=_('lesson_start_time'))
    lesson_end_time = models.TimeField(blank=False, null=True, verbose_name=_('lesson_end_time'))
    date_created = models.DateField(auto_now_add=True, blank=True, verbose_name=_('date_created'))


TEST_TYPE_CHOICES = [
    ('assignment', _('assignment')),
    ('quiz', _('quiz')),
    ('test', _('test')),
    ('exam', _('exam')),
]
class Test(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, blank=False, null=True, verbose_name=_('lesson'))
    name = models.CharField(verbose_name=_('name'), max_length=200, blank=True,)
    test_type = models.CharField(verbose_name=_('test_type'), max_length=20, choices=TEST_TYPE_CHOICES, default='assignment')
    deadline = models.DateField(blank=False, null=True, verbose_name=_('test_deadline'), default=None)

    text_input_required = models.BooleanField(default=False)

    questions = models.ManyToManyField(Question, through='TestQuestion', verbose_name=_('question'))
    date_created = models.DateTimeField(auto_now_add=True, blank=True, verbose_name=_('date_created'),)
    
    
    def __str__(self):
        return self.name


class TestQuestion(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    
    test = models.ForeignKey(Test, on_delete=models.CASCADE, blank=False, null=True, verbose_name=_('test'))
    question = models.ForeignKey(Question, on_delete=models.CASCADE, blank=False, null=True, verbose_name=_('question'))
    max_point = models.IntegerField(default=0, blank=True)



class VideoLectureToLesson(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    video_lecture = models.ForeignKey(VideoLecture, on_delete=models.CASCADE, blank=False, null=True, verbose_name=_('video_lecture'))
    custom_video_lecture = models.CharField(max_length=255, blank=True, null=True, default=None, verbose_name=_('custom_video_lecture'))
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, blank=False, null=True, verbose_name=_('lesson'))

    def clean(self):
        if (self.video_lecture is None and self.custom_video_lecture is None) or (self.video_lecture is not None and self.custom_video_lecture is not None):
            raise ValidationError(_('Either video_lecture or custom_video_lecture must be set, but not both.'))

    def save(self, *args, **kwargs):
        self.clean()
        super(VideoLectureToLesson, self).save(*args, **kwargs)


class GoogleCalendarSubscription(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name=_('user'))
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, null=True, verbose_name=_('classroom'))

    class Meta:
        unique_together = ('user', 'classroom')


class GoogleCalendarLessonEvents(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    
    subscription = models.ForeignKey(GoogleCalendarSubscription, on_delete=models.CASCADE, blank=False, null=True, verbose_name=_('subsription'))
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, verbose_name=_('lesson'))
    google_calendar_event_id = models.CharField(max_length=255, blank=True, null=True, default=None, verbose_name=_('google_calendar_event'))

    class Meta:
        unique_together = ('subscription', 'lesson')
    
