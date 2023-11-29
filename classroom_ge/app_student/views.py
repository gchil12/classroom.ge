from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _


@login_required(login_url='app_base:login')
def student_homepage(request):
    if not request.user.is_student:
        return redirect('app_base:home')
    
    return render(request, 'app_student/student_homepage.html')
    
        