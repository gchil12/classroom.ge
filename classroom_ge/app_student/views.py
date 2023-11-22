from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(request):
    return render(request, 'app_student/home.html')


def login(request):
    return render(request, 'app_student/login.html')


def register(request):
    return render(request, 'app_student/register.html')


def student_homepage(request):
    return render(request, 'app_student/student_homepage.html')