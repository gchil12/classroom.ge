from django.core import validators
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from base.models import User
from django import forms
from datetime import date
from django.utils.translation import gettext_lazy as _
from src.validators import password_validator
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox


class RegistrationForm(ModelForm):
    required_css_class = 'required'

    user_type_student = forms.BooleanField(required=False, initial=True)
    user_type_teacher = forms.BooleanField(required=False, initial=False)

    email_conf = forms.CharField(
        max_length  =   200,
        label       =   _('confirm_email',),
        widget      =   forms.TextInput(
            attrs={
                'autocomplete':'off'
            }
        ),
        error_messages={'required':_('this_field_is_required')}
    )

    password_conf = forms.CharField(
        max_length  =   200,
        label       =   _('confirm_password',),
        widget      =   forms.PasswordInput(
            attrs={
                'autocomplete':'off'
            }
        ),
        error_messages={'required':_('this_field_is_required')}
    )

    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox,
        error_messages={'required':_('this_field_is_required')}
    )


    class Meta:
        model  = User

        fields = ['name', 'surname', 'date_of_birth', 'school', 'city', 'email', 'password']

        labels = {
            'name':             _('name'),
            'surname':          _('surname'),
            'date_of_birth':    _('date_of_birth'),
            'school':           _('school'),
            'city':             _('city'),
            'email':            _('email'),
            'password':         _('password'),
        }

        error_messages = {
            'name': {
                'required': _('this_field_is_required'),
            },
            'surname': {
                'required': _('this_field_is_required'),
            },
            'date_of_birth': {
                'required': _('this_field_is_required'),
            },
            'school': {
                'required': _('this_field_is_required'),
            },
            'city': {
                'required': _('this_field_is_required'),
            },
            'email': {
                'required': _('this_field_is_required'),
            },
            'password': {
                'required': _('this_field_is_required'),
            },
        }

        widgets = {
            'date_of_birth': forms.DateInput(
                attrs={'type': 'date', 'id': 'georgianDate'}
            ),
            'password': forms.PasswordInput(),
        }
        

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        self.fields['date_of_birth'].initial = None
        self.fields['school'].initial = None
        self.fields['city'].initial = None
        

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['autocomplete'] = 'off'


    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        email = cleaned_data.get("email")
        email_conf = cleaned_data.get("email_conf")
        
        password = cleaned_data.get("password")
        password_conf = cleaned_data.get("password_conf")

        date_of_birth = cleaned_data.get("date_of_birth")

        user_type_student = cleaned_data.get('user_type_student')
        user_type_teacher = cleaned_data.get('user_type_teacher')


        if date_of_birth is not None and date.today() <= date_of_birth:
            self.add_error("date_of_birth", _('chosen_date_in_future'))
        
        errors = password_validator(password, password_conf)

        for error in errors:
            self.add_error("password", error)

        try:
            validators.validate_email(email)
        except ValidationError as e:
            self.add_error("email", _('invalid_email'))


        try:
            validators.validate_email(email_conf)
        except ValidationError as e:
            self.add_error("email_conf", _('invalid_email'))

            
        if email != email_conf:
            self.add_error("email", _('emails_do_not_match'))

        if user_type_student == None or user_type_teacher == None or not (user_type_student or user_type_teacher):
            self.add_error("email", _('unknown_error_refresh'))

