from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .forms import RegistrationForm
from .models import User

from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from .tokens import account_activation_token


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
            send_email_after_registration(request, urlsafe_base64_encode(force_bytes(user.uuid)))
            return redirect('app_base:login') # NOSONAR
        else:
            context['isvalid'] = False
            
    
    return render(request, 'base/register.html', context)


def login_user(request):
    if request.user.is_authenticated:
        return redirect_to_homepage(request)
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except Exception as e: # NOSONAR
            messages.error(request, _('email_or_password_does_not_exist'))
            return render(request, 'base/login.html') # NOSONAR

        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            if not user.email_verified:
                messages.error(request, _('email_is_not_verified_yet'))
                return render(request, 'base/login.html')
            else:
                login(request, user)
                return redirect_to_homepage(request)
                
        else:
            messages.error(request, _('email_or_password_does_not_exist'))
    
    return render(request, 'base/login.html')


@login_required(login_url='app_base:login')
def logout_user(request):
    logout(request)
    return redirect('app_base:home')



################# Account Activation #################

def send_email_after_registration(request, uidb64):
    uuid = force_str(urlsafe_base64_decode(uidb64))
    user = User.objects.get(uuid = uuid)
    
    email_subject = 'Classroom.ge: ' + _('activate_account')
    message = render_to_string('base/template_activate_account.html', {
        'name': user.name,
        'surname': user.surname,
        'uidb64': urlsafe_base64_encode(force_bytes(user.uuid)),
        'domain': get_current_site(request).domain,
        'protocol': 'https' if request.is_secure() else 'http', # TODO
        'token': account_activation_token.make_token(user)
    })

    email = EmailMessage(email_subject, message, to=[user.email])

    if email.send():
        messages.success(request, 'Email Varification Sent')
        print('here')

    if request.method == 'POST':
        return redirect('app_base:login')


def activate_account(request, uidb64, token):
    try:
        uuid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(uuid = uuid)
    except Exception as e: # NOSONAR
        user = None

    if user is not None:
        if account_activation_token.check_token(user, token):
            user.email_verified = True
            user.save()

            messages.success(request, _('email_activation_was_successfull'))
            return redirect('app_base:login')
        else:
            return render(request, 'base/template_activation_link_expired.html', {'uuid': urlsafe_base64_encode(force_bytes(user.uuid))})
    else:
        messages.error(request, _('something_went_wrong'))

    return redirect('app_base:home')
