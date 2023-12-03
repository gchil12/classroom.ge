from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from .forms import CreateNewClassroomForm, CreateNewLessonForm
from django.utils.translation import gettext_lazy as _
from .models import Classroom, Lesson
from app_student.models import StudentToClassroom
from django.contrib import messages

# Create your views here.
@login_required(login_url='app_base:login')
def teacher_homepage(request):
    if not request.user.is_teacher:
        return redirect('app_base:home')
    
    classrooms = Classroom.objects.filter(owner=request.user)

    context = {'classrooms': classrooms,}
    
    return render(request, 'app_teacher/teacher_homepage.html', context)


@login_required(login_url='app_base:login')
def classroom(request, uuid):
    if not request.user.is_teacher:
        return redirect('app_base:home')
    
    classroom = get_object_or_404(Classroom, uuid=uuid)
    lessons = Lesson.objects.filter(classroom=classroom)

    student_to_classrooms = StudentToClassroom.objects.filter(classroom=classroom)

    domain = get_current_site(request).domain
    
    context = {
        'classroom': classroom,
        'lessons': lessons,
        'domain': domain,
        'student_to_classrooms': student_to_classrooms,
    }

    return render(request, 'app_teacher/classroom/classroom_details.html', context)
    

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

    if request.method == 'POST':
        form = CreateNewClassroomForm(request.POST)
        context['form'] = form
        context['submitted'] = True
        
        if form.is_valid():
            classroom = form.save(commit=False)
            
            classroom.owner = request.user

            classroom.save()
            
            
            messages.success(request, _('new_class_created'))
            return redirect('app_teacher:home')
        else:
            messages.error(request, _('invalid_input'))
            context['isvalid'] = False

    return render(request, 'app_teacher/classroom/new_classroom_page.html', context)
    
        

@login_required(login_url='app_base:login')
def delete_classroom(request, uuid):
    if not request.user.is_teacher:
        return redirect('app_base:home')
    
    classroom = get_object_or_404(Classroom, uuid=uuid)

    if request.method == 'POST':
        if classroom.owner != request.user:
            pass
            messages.error(request, _('error_unauthorized_access'))
        else:
            messages.success(request, _('classroom_deleted'))
            classroom.delete()

        return redirect('app_teacher:home')
    else:
        return render(request, 'app_teacher/classroom/confirm_classroom_deletion.html', {'classroom': classroom})


@login_required(login_url='app_base:login')
def archive_classroom(request, uuid):
    if not request.user.is_teacher:
        return redirect('app_base:home')
    
    classroom = get_object_or_404(Classroom, uuid=uuid)

    if classroom.owner != request.user:
        messages.error(request, _('error_unauthorized_access'))
        pass
    else:
        classroom.is_archived = not classroom.is_archived

        if classroom.is_archived:
            messages.success(request, _('classroom_archived'))
        else:
            messages.success(request, _('classroom_unarchived'))

        classroom.save()

    return redirect('app_teacher:home')


@login_required(login_url='app_base:login')
def new_lesson(request, classroom_uuid):
    if not request.user.is_teacher:
        return redirect('app_base:home')
    
    classroom = get_object_or_404(Classroom, uuid=classroom_uuid)

    if classroom.owner != request.user:
        messages.error(request, _('error_unauthorized_access'))
        return redirect('app_teacher:home')

    form = CreateNewLessonForm()
    
    context = {
        'form': form,
        'isvalid': False,
        'submitted': False,
        'classroom': classroom,
    }

    if request.method == 'POST':
        form = CreateNewLessonForm(request.POST)
        context['form'] = form
        context['submitted'] = True
        
        if form.is_valid():
            lesson = form.save(commit=False)
            
            lesson.classroom = classroom

            lesson.save()
            
            messages.success(request, _('new_lesson'))

            redirect_url = reverse('app_teacher:classroom-detail', kwargs={'uuid': classroom_uuid})
            return redirect(redirect_url)
        else:
            messages.error(request, _('invalid_input'))
            context['isvalid'] = False

    return render(request, 'app_teacher/classroom/new_lesson_page.html', context)
    

@login_required(login_url='app_base:login')
def delete_lesson(request, uuid):
    if not request.user.is_teacher:
        return redirect('app_base:home')
    
    lesson = get_object_or_404(Lesson, uuid=uuid)
    classroom_uuid = lesson.classroom.uuid

    if request.method == 'POST':
        if lesson.classroom.owner != request.user:
            pass
            messages.error(request, _('error_unauthorized_access'))
        else:
            messages.success(request, _('classroom_deleted'))
            lesson.delete()

        redirect_url = reverse('app_teacher:classroom-detail', kwargs={'uuid': classroom_uuid})
        return redirect(redirect_url)
    else:
        return render(request, 'app_teacher/classroom/confirm_lesson_deletion.html', {'lesson': lesson})


################# Adding Students to Classrooms #################
