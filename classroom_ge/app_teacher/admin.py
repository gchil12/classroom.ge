from django.contrib import admin
from .models import (
    Classroom,
    Lesson,
    Test,
    TestVariant,
    Questions,
    TestQuestion
)

# Register your models here.
admin.site.register(Classroom)
admin.site.register(Lesson)
admin.site.register(Test)
admin.site.register(TestVariant)
admin.site.register(Questions)
admin.site.register(TestQuestion)
