from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.teacher_homepage, name='home'),
    path('classroom/<uuid:uuid>/', views.classroom, name='classroom-detail'),
    path('archive_classroom/<uuid:uuid>/', views.archive_classroom, name='classroom-archive'),
    path('delete_classroom/<uuid:uuid>/', views.delete_classroom, name='classroom-delete'),
    path('create_classroom/', views.newClassroom, name='create-new-classroom'),

    path('create_lesson/<uuid:classroom_uuid>/', views.new_lesson, name='create-new-lesson'),
    path('delete_lesson/<uuid:uuid>/', views.delete_lesson, name='lesson-delete'),
]
