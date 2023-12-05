from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from .forms import CreateNewClassroomForm, CreateNewLessonForm
from django.utils.translation import gettext_lazy as _
from .models import Classroom, Lesson, Level, ClassroomToLevels
from app_student.models import StudentToClassroom
from django.contrib import messages
from django.db.models import Count, Q

# Create your views here.
@login_required(login_url='app_base:login')
def teacher_homepage(request):
    if not request.user.is_teacher:
        return redirect('app_base:home')
    
    # classrooms = Classroom.objects.filter(owner=request.user)
    classrooms_with_levels = Classroom.objects.annotate(
        num_levels=Count('classroomtolevels__level'),
        num_students=Count('studenttoclassroom__student', filter=Q(studenttoclassroom__student__is_student=True))
    ).filter(owner=request.user)

    context = {'classrooms': classrooms_with_levels,}
    
    return render(request, 'app_teacher/menu_elements/teacher_homepage.html', context)


############### Classrooms #################

@login_required(login_url='app_base:login')
def classrooms(request):
    if not request.user.is_teacher:
        return redirect('app_base:home')
    
    # classrooms_with_levels = Classroom.objects.prefetch_related('classroomtolevels_set__level').all()
    classrooms_with_levels = Classroom.objects.annotate(
        num_levels=Count('classroomtolevels__level'),
        num_students=Count('studenttoclassroom__student', filter=Q(studenttoclassroom__student__is_student=True))
    ).filter(owner=request.user)
    
    return render(request, 'app_teacher/menu_elements/classrooms_page.html', {'classrooms': classrooms_with_levels})


@login_required(login_url='app_base:login')
def classroom_details(request, uuid):
    if not request.user.is_teacher:
        return redirect('app_base:home')
    
    classroom = get_object_or_404(Classroom, uuid=uuid)

    if classroom.owner != request.user:
        messages.error(request, _('error_unauthorized_access'))
        return redirect('app_teacher:home')

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
            
            level = Level.objects.filter(level=form.cleaned_data['levels']).first()
            print(level)
            
            try:
                classroom_to_level = ClassroomToLevels.objects.create(
                    classroom=classroom,
                    level = level,
                )
                classroom_to_level.save()
            except:
                # Pair Exists or user did not chose anything
                pass

            
            messages.success(request, _('new_class_created'))
            redirect_url = reverse('app_teacher:classroom-detail', kwargs={'uuid': classroom.uuid})
            return redirect(redirect_url)
        else:
            messages.error(request, _('invalid_input'))
            context['isvalid'] = False

    return render(request, 'app_teacher/classroom/new_classroom_page.html', context)
    
        

@login_required(login_url='app_base:login')
def delete_classroom(request, uuid):
    if not request.user.is_teacher:
        return redirect('app_base:home')
    
    classroom = get_object_or_404(Classroom, uuid=uuid)

    
    if classroom.owner != request.user:
        messages.error(request, _('error_unauthorized_access'))
        return redirect('app_teacher:home')
    

    if request.method == 'POST':        
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
    else:
        classroom.is_archived = not classroom.is_archived

        if classroom.is_archived:
            messages.success(request, _('classroom_archived'))
        else:
            messages.success(request, _('classroom_unarchived'))

        classroom.save()

    return redirect('app_teacher:home')


############### Lessons #################

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


    if lesson.classroom.owner != request.user:
        messages.error(request, _('error_unauthorized_access'))
        return redirect('app_teacher:home')
    

    if request.method == 'POST':
        messages.success(request, _('classroom_deleted'))
        lesson.delete()

        redirect_url = reverse('app_teacher:classroom-detail', kwargs={'uuid': classroom_uuid})
        return redirect(redirect_url)
    else:
        return render(request, 'app_teacher/classroom/confirm_lesson_deletion.html', {'lesson': lesson})

