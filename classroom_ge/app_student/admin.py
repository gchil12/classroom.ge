from django.contrib import admin
from .models import StudentToClassroom, StudentProfile

class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)

# Register your models here.
admin.site.register(StudentProfile, StudentProfileAdmin)
admin.site.register(StudentToClassroom)