from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from app_teacher.models import Classroom
from .models import StudentToClassroom


@login_required(login_url='app_base:login')
def student_homepage(request):
    if not request.user.is_student:
        return redirect('app_base:home')
    
    student_to_classrooms = StudentToClassroom.objects.filter(student=request.user)

    context = {
        'student_to_classrooms': student_to_classrooms,
    }
    return render(request, 'app_student/student_homepage.html', context)
    

@login_required(login_url='app_base:login')
def subscribe_to_classroom(request, classroom_uuid):
    if not request.user.is_student:
        redirect_url = reverse('app_teacher:classroom-detail', kwargs={'uuid': classroom_uuid})
        return redirect(redirect_url)
    

    if request.method == 'POST':
        classroom = get_object_or_404(Classroom, uuid=classroom_uuid)
        student_to_classroom_exists = StudentToClassroom.objects.filter(student=request.user, classroom=classroom).exists()
        

        if student_to_classroom_exists:
            messages.success(request, _('already_subscribed_to_classroom'))
            return redirect('app_student:home')
        else:
            StudentToClassroom.objects.create(
                student = request.user,
                classroom = classroom,
            )
            messages.success(request, _('subscribed_to_classroom_successfully'))
            return redirect('app_student:home')
    else:
        classroom = get_object_or_404(Classroom, uuid=classroom_uuid)
        
        context = {
            'classroom': classroom
        }

        return render(request, 'app_student/classroom_subscribe.html', context)
