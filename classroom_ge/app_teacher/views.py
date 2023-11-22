from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(request):
    return render(request, 'app_teacher/home.html')


def login(request):
    return render(request, 'app_teacher/login.html')


def register(request):
    return render(request, 'app_teacher/register.html')


def student_homepage(request):
    return render(request, 'app_teacher/teacher_homepage.html')


def classroom(request):
    return render(request, 'app_teacher/class_details.html')