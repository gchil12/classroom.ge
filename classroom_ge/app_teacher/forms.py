from django.forms import ModelForm
from django import forms
from .models import Classroom, Lesson, Level
from django.utils.translation import gettext_lazy as _
from django.forms.widgets import SelectDateWidget

class CreateNewClassroomForm(ModelForm):
    required_css_class = 'required'

    try:
        levels = forms.ChoiceField(
            choices=[('', _('None'))] + [(cur_level.level, cur_level.level) for cur_level in Level.objects.all()],
            label       =   _('class_level',),
            required=False,
        )
    except:
        levels = []

    def __init__(self, *args, **kwargs):
        super(CreateNewClassroomForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


    class Meta:
        model  = Classroom

        fields = ['name', 'subject', 'description', 'online_meeting_link']


class CreateNewLessonForm(ModelForm):
    required_css_class = 'required'
    
    def __init__(self, *args, **kwargs):
        super(CreateNewLessonForm, self).__init__(*args, **kwargs)

        self.fields['lesson_date'].initial = None

        self.fields['lesson_start_time'].widget = forms.TimeInput(attrs={'type': 'time'})
        self.fields['lesson_end_time'].widget = forms.TimeInput(attrs={'type': 'time'})
        

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model  = Lesson

        fields = ['name', 'description', 'lesson_date', 'lesson_start_time', 'lesson_end_time']

        widgets = {
            'lesson_date': forms.DateInput(
                attrs={'type': 'date', 'id': 'georgianDate'}
            ),
            'lesson_start_time': forms.TimeInput(format='%H:%M'),
        }
