from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.teacher_homepage, name='home'),
    path('classroom/', views.classroom, name='classroom'),
    path('new_classroom/', views.newClassroom, name='new-classroom'),
]
