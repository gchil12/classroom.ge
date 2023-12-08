from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.student_homepage, name='home'),
    path('classroom/subscribe/<uuid:classroom_uuid>', views.subscribe_to_classroom, name='subscribe-classroom'),

    path('classrooms/', views.classroom_list, name='classrooms'),
    path('classroom/<uuid:uuid>/', views.classroom_details, name='classroom-detail'),

    path('lesson/<uuid:lesson_uuid>/', views.lesson_details, name='lesson-detail'),
    path('test/<uuid:test_uuid>/', views.test_show_page, name='test-page'),
    path('test_submit/<uuid:student_test_uuid>/', views.test_submit, name='test-submit'),
    path('test_view/<uuid:test_uuid>/', views.view_computed_test, name='test-view')
]
