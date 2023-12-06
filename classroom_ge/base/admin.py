from django.contrib import admin
from .models import User, Message, Subject, Topic, MultipleChoiceQuestion, MultipleChoiceQuestionToTopics
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


class CustomTopicAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'name',)
    ordering = ('identifier',)


class CustomMultipleChoiceQustionAdmin(admin.ModelAdmin):
    list_display = ('id', 'text',)
    ordering = ('id',)


class MultipleChoiceQuestionToTopicsAdmin(admin.ModelAdmin):
    list_display = ('topic', 'get_question_text')
    ordering = ('topic',)

    def get_question_text(self, obj):
        return obj.question.text


# Register your models here.
admin.site.register(User, CustomUserAdmin)
admin.site.register(Message)
admin.site.register(Subject)
admin.site.register(Topic, CustomTopicAdmin)

admin.site.register(MultipleChoiceQuestion, CustomMultipleChoiceQustionAdmin)
admin.site.register(MultipleChoiceQuestionToTopics, MultipleChoiceQuestionToTopicsAdmin)