from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='url-teacher-home'),
    path('login/', views.login, name='url-teacher-login'),
    path('register/', views.register, name='url-teacher-register'),
    path('home/', views.student_homepage, name='url-teacher-teacher-homepage'),
    path('classroom/', views.classroom, name='url-teacher-classroom'),
]
