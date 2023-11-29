"""
URL configuration for classroom_ge project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path

urlpatterns = [
    path('', include(('base.urls', 'app_base'), namespace='app_base')),
    path('student/', include(('app_student.urls', 'app_student'), namespace='app_student')),
    path('teacher/', include(('app_teacher.urls', 'app_teacher'), namespace='app_teacher')),
    path('moderator/', include(('app_administrator.urls', 'app_administrator'), namespace='app_administrator')),
    path('admin/', admin.site.urls),
]
