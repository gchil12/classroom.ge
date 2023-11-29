from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import CreateNewClassroomForm
from django.utils.translation import gettext_lazy as _

# Create your views here.
@login_required(login_url='app_base:login')
def teacher_homepage(request):
    if not request.user.is_teacher:
        return redirect('app_base:home')
    
    return render(request, 'app_teacher/teacher_homepage.html')


@login_required(login_url='app_base:login')
def classroom(request):
    if not request.user.is_teacher:
        return redirect('app_base:home')
    
    return render(request, 'app_teacher/classroom/class_details.html')
    

@login_required(login_url='app_base:login')
def newClassroom(request):
    if not request.user.is_teacher:
        return redirect('app_base:home')
    
    form = CreateNewClassroomForm()
    
    context = {
        'form': form,
        'isvalid': False,
        'submitted': False
    }

    return render(request, 'app_teacher/classroom/new_classroom_page.html', context)
    
        