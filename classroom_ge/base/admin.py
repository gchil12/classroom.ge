from django.contrib import admin
from .models import User, Message, Subject, Topic, Question, QuestionChoice, QuestionToTopic
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

class CustomUserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'email_verified' ,'password')}),
        (_('Personal info'), {'fields': ('name', 'surname', 'date_of_birth', 'school', 'city')}),
        (_('WEB Groups'), {'fields': ('is_student', 'is_teacher', 'is_moderator', 'is_administrator')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    list_display = ( 'uuid', 'name', 'surname', 'email', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'name', 'surname')
    ordering = ('email', 'name', 'surname')

    capitalize = False


class TopicAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'subject', 'name',)
    ordering = ('identifier',)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_type', 'text')
    ordering = ('question_type',)


class QuestionToTopicAdmin(admin.ModelAdmin):
    list_display = ('question', 'topic')
    ordering = ('topic',)


class QuestionChoiceAdmin(admin.ModelAdmin):
    list_display = ('question', 'text', 'is_correct')
    ordering = ('question',)



# Register your models here.
admin.site.register(User, CustomUserAdmin)
admin.site.register(Message)
admin.site.register(Subject)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionChoice, QuestionChoiceAdmin)
admin.site.register(QuestionToTopic, QuestionToTopicAdmin)

