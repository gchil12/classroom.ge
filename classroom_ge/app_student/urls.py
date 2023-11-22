from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='url-student-home'),
    path('login/', views.login, name='url-student-login'),
    path('register/', views.register, name='url-student-register'),
    path('home/', views.student_homepage, name='url-student-student-homepage'),
]
