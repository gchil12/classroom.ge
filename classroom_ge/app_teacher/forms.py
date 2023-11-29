from django.forms import ModelForm
from django import forms
from .models import Classroom
from django.utils.translation import gettext_lazy as _

class CreateNewClassroomForm(ModelForm):
    required_css_class = 'required'
    
    def __init__(self, *args, **kwargs):
        super(CreateNewClassroomForm, self).__init__(*args, **kwargs)

    class Meta:
        model  = Classroom

        fields = ['name']