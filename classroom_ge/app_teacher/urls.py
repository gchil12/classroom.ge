from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='url-teacher-home'),
    path('classroom/', views.classroom, name='url-teacher-classroom')
]
