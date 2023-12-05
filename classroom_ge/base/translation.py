from modeltranslation.translator import TranslationOptions, register
from .models import Subject, User

@register(Subject)
class SubjectTranslationOptions(TranslationOptions):
    fields = ('name',)

