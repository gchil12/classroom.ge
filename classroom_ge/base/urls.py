from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('activate-acount/<uidb64>/<token>', views.activate_account, name='activate'),
    path('send_verification_email/<uidb64>', views.send_email_after_registration, name='send_email_verification'),
]
