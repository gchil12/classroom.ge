from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import (
    TeacherProfile,
    Classroom,
    Level,
    ClassroomToLevels,
    Lesson,
    Test,
    TestQuestion,
    UsersToLessonGoogleCalendarEvents
    # Test,
    # TestVariant,
    # Questions,
    # TestQuestion
)

class TeacherProfileAdmin(ModelAdmin):
    list_display = ('user',)

class LevelAdmin(ModelAdmin):
    ordering = ('level',)

class TestAdmin(admin.ModelAdmin):
    list_display = ('name', 'test_type')
    ordering = ('name',)


class TestQuestionAdmin(admin.ModelAdmin):
    list_display = ('test', 'question', 'max_point')
    ordering = ('test',)


# Register your models here.
admin.site.register(TeacherProfile, TeacherProfileAdmin)
admin.site.register(Classroom)
admin.site.register(Level, LevelAdmin)
admin.site.register(ClassroomToLevels)
admin.site.register(Lesson)
admin.site.register(Test, TestAdmin)
admin.site.register(TestQuestion, TestQuestionAdmin)
admin.site.register(UsersToLessonGoogleCalendarEvents)