from django.db import models
import uuid
from base.models import User
from app_teacher.models import Classroom
from django.utils.translation import gettext_lazy as _

# Create your models here.
class StudentToClassroom(models.Model):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False, unique=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name=_('student'))
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, null=True, verbose_name=_('classroom'))

    class Meta:
        unique_together = ('student', 'classroom')
