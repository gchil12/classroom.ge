from modeltranslation.translator import TranslationOptions, register
from .models import Subject, Topic, MultipleChoiceQuestion

@register(Subject)
class SubjectTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Topic)
class TopicTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(MultipleChoiceQuestion)
class MultipleChoiceQuestionTranslationOptions(TranslationOptions):
    fields = ('text',)