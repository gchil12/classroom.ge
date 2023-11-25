from django.shortcuts import render
from .forms import RegistrationForm
from base.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def home(request):
    return render(request, 'app_student/home.html')


def loginUser(request):
    if request.user.is_authenticated:
        return redirect('url-student-student-homepage')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, _('username_or_password_does_not_exist'))
            return render(request, 'app_student/login.html')

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if not user.email_verified:
                messages.error(request, _('email_is_not_verified_yet'))
                return render(request, 'app_student/login.html')
            else:
                login(request, user)
                return redirect('url-student-student-homepage')
        else:
            messages.error(request, _('username_or_password_does_not_exist'))
        
    return render(request, 'app_student/login.html')


def logoutUser(request):
    logout(request)
    return redirect('url-base-home')


def register(request):
    if request.user.is_authenticated:
        return redirect('url-student-student-homepage')
    
    form = RegistrationForm()

    context = {
        'form': form,
        'isvalid': False,
        'submitted': False
    }
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        context['form'] = form
        context['submitted'] = True
        
        if form.is_valid():
            user = User.objects.create_user(
                username = request.POST.get('username'),
                email = request.POST.get('email'),
                password = request.POST.get('password'),
                name = request.POST.get('name'),
                surname = request.POST.get('surname'),
                date_of_birth = request.POST.get('date_of_birth'),
                school = request.POST.get('school'),
                city = request.POST.get('city'),
                is_student = True,
            )

            user.save()
            
            context['isvalid'] = True
            context['form'] = RegistrationForm()
            
            messages.info(request, _('message_first_step_of_registration_done'))
            return redirect('url-base-home')
        else:
            context['isvalid'] = False
            
    
    return render(request, 'app_student/register.html', context)


@login_required(login_url='url-student-login')
def student_homepage(request):
    return render(request, 'app_student/student_homepage.html')