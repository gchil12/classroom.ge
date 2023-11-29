from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .forms import RegistrationForm
from .models import User


# Create your views here.
def redirect_to_homepage(request):
    if request.user.is_student:
        url = reverse('app_student:home')
        return redirect(url)
    elif request.user.is_teacher:
        url = reverse('app_teacher:home')
        return redirect(url)


def home(request):
    return render(request, 'base/home.html')


def register(request):
    if request.user.is_authenticated:
        return redirect_to_homepage(request)
    
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
                is_student = form.cleaned_data['user_type_student'],
                is_teacher = form.cleaned_data['user_type_teacher'],
            )

            user.save()
            
            context['isvalid'] = True
            context['form'] = RegistrationForm()
            
            messages.info(request, _('message_first_step_of_registration_done'))
            return redirect('app_base:home')
        else:
            context['isvalid'] = False
            
    
    return render(request, 'base/register.html', context)


def loginUser(request):
    if request.user.is_authenticated:
        return redirect_to_homepage(request)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, _('username_or_password_does_not_exist'))
            return render(request, 'base/login.html')

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if not user.email_verified:
                messages.error(request, _('email_is_not_verified_yet'))
                return render(request, 'base/login.html')
            else:
                login(request, user)
                return redirect_to_homepage(request)
                
        else:
            messages.error(request, _('username_or_password_does_not_exist'))
    
    return render(request, 'base/login.html')


def logoutUser(request):
    logout(request)
    return redirect('app_base:home')
