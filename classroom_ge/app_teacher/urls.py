from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.teacher_homepage, name='home'),
    path('classrooms/', views.classrooms, name='classrooms'),


    path('classroom/<uuid:uuid>/', views.classroom_details, name='classroom-detail'),
    path('archive_classroom/<uuid:uuid>/', views.archive_classroom, name='classroom-archive'),
    path('delete_classroom/<uuid:uuid>/', views.delete_classroom, name='classroom-delete'),
    path('create_classroom/', views.new_classroom, name='create-new-classroom'),

    path('create_lesson/<uuid:classroom_uuid>/', views.new_lesson, name='create-new-lesson'),
    path('delete_lesson/<uuid:uuid>/', views.delete_lesson, name='lesson-delete'),
    path('lesson/<uuid:uuid>/', views.lesson_details, name='lesson-detail'),

    path('tests', views.tests_main_page, name='test-main'),
    path('test_example/<uuid:uuid>/', views.test_example_page, name='test-example-page'),
    path('test_details/<uuid:test_uuid>/', views.test_details, name='test-details'),
    path('test_delete/<uuid:test_uuid>/', views.test_delete, name='test-delete'),
    path('test_results/<uuid:test_uuid>/<uuid:student_uuid>', views.test_results_student, name='test-results-student'),

    path('choose_lesson/<uuid:topic_uuid>/', views.choose_lessons_to_add_test, name='choose-lesson'),
    path('choose_lesson/<uuid:classroom_uuid>/<uuid:lesson_uuid>/<uuid:topic_uuid>', views.add_test_to_lesson_confirmation, name='add-test-confirmation'),
]
