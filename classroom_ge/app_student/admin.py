from django.contrib import admin
from .models import StudentProfile, StudentToClassroom, StudentTest, StudentQuestion, StudentQuestionToChoice

class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)


class StudentTestAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('student', 'test' ,'completed', 'start_time')}),
    )

    list_display = ('test', 'student',)


class StudentQuestionAdmin(admin.ModelAdmin):
    list_display = ('student_test', 'given_point', 'answered',)

# Register your models here.
admin.site.register(StudentProfile, StudentProfileAdmin)
admin.site.register(StudentToClassroom)
admin.site.register(StudentTest, StudentTestAdmin)
admin.site.register(StudentQuestion, StudentQuestionAdmin)
admin.site.register(StudentQuestionToChoice)