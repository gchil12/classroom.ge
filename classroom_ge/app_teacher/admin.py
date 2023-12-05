from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import (
    Classroom,
    Level,
    ClassroomToLevels,
    Lesson,
    Test,
    TestVariant,
    Questions,
    TestQuestion
)


class LevelAdmin(ModelAdmin):
    ordering = ('level',)


# Register your models here.
admin.site.register(Classroom)
admin.site.register(Level, LevelAdmin)
admin.site.register(ClassroomToLevels)
admin.site.register(Lesson)
admin.site.register(Test)
admin.site.register(TestVariant)
admin.site.register(Questions)
admin.site.register(TestQuestion)
