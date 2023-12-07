from modeltranslation.translator import TranslationOptions, register
from .models import Subject, Topic, Question, QuestionChoice

@register(Subject)
class SubjectTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Topic)
class TopicTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Question)
class QuestionTranslationOptions(TranslationOptions):
    fields = ('text',)


@register(QuestionChoice)
class QuestionChoiceTranslationOptions(TranslationOptions):
    fields = ('text',)
