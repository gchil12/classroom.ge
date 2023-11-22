from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(request):
    return render(request, 'app_teacher/home.html')


def classroom(request):
    return render(request, 'app_teacher/class_details.html')