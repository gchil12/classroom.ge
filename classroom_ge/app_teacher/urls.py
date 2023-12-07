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

    path('exercises', views.exercises_main_page, name='exercises-main'),
    path('exercise_details/<uuid:uuid>/', views.exercise_main_details, name='exercises-main-details'),

    path('choose_lesson/<uuid:topic_uuid>/', views.choose_lessons_to_add_exercises, name='choose-lesson'),
]
