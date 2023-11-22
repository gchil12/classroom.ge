from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(request):
    return render(request, 'teacher/home.html')


def classroom(request):
    return render(request, 'teacher/class_details.html')