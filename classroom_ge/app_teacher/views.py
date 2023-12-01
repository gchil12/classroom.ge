from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CreateNewClassroomForm
from django.utils.translation import gettext_lazy as _
from .models import Classroom
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

    context = {
        'classroom': classroom
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
            messages.error(request, _('error:deleting_classroom'))
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
        pass
    else:
        classroom.is_archived = not classroom.is_archived

        if classroom.is_archived:
            messages.success(request, _('classroom_archived'))
        else:
            messages.success(request, _('classroom_unarchived'))

        classroom.save()

    return redirect('app_teacher:home')