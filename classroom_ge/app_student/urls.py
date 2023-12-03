from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.student_homepage, name='home'),
    path('classroom/subscribe/<uuid:classroom_uuid>', views.subscribe_to_classroom, name='subscribe-classroom')
]
