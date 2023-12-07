from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from app_teacher.models import Classroom, Lesson
from .models import StudentToClassroom
from django.utils import timezone
from django.db.models import Count, Q, Subquery, OuterRef


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


@login_required(login_url='app_base:login')
def classroom_list(request):
    if not request.user.is_student:
        return redirect('app_base:home')
    
    now = timezone.now()
    
    closest_lesson_subquery = Lesson.objects.filter(
        Q(lesson_date__gt=now.date()) | (Q(lesson_date=now.date()) & Q(lesson_start_time__gte=now.time())),
        classroom=OuterRef('pk'),
    ).order_by('lesson_date', 'lesson_start_time').values('lesson_start_time', 'name', 'lesson_date')[:1]
    
    n_lessons_subquery = Lesson.objects.filter(
        classroom=OuterRef('pk')
    ).values('classroom').annotate(
        n_lessons=Count('classroom')
    ).values('n_lessons')[:1]

    classrooms_extended_table = Classroom.objects.annotate(
        closest_lesson_start_time=Subquery(closest_lesson_subquery.values('lesson_start_time')),
        closest_lesson_name=Subquery(closest_lesson_subquery.values('name')),
        closest_lesson_date=Subquery(closest_lesson_subquery.values('lesson_date')),
        n_lessons=Subquery(n_lessons_subquery),
    ).filter(studenttoclassroom__student=request.user)

    # classrooms = Classroom.objects.filter(studenttoclassroom__student=request.user)

    context = {
        'classrooms': classrooms_extended_table,
    }
    return render(request, 'app_student/menu_elements/classrooms.html', context)


@login_required(login_url='app_base:login')
def classroom_details(request, uuid):
    if not request.user.is_student:
        return redirect('app_base:home')
    
    classroom = get_object_or_404(Classroom, uuid=uuid)

    obj = StudentToClassroom.objects.get(
        student=request.user,
        classroom=classroom
    )

    if obj is None:
        redirect_url = reverse('app_student:subscribe-classroom', kwargs={'uuid': uuid})
        return redirect(redirect_url)

    lessons = Lesson.objects.filter(classroom=classroom)

    context = {
        'lessons': lessons,
        'classroom': classroom,
    }

    return render(request, 'app_student/menu_elements/classroom_details.html', context)