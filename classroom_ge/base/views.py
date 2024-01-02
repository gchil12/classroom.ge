from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .forms import RegistrationForm
from .models import User
from app_student.models import StudentProfile
from app_teacher.models import TeacherProfile, Classroom, Lesson

from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from .tokens import account_activation_token
import threading
from google_auth_oauthlib.flow import Flow
from classroom_ge.settings import GOOGLE_OAUTH2_CLIENT_ID, GOOGLE_OAUTH2_CLIENT_SECRET
from classroom_ge.my_constants import google_oauth2_redirect_url
from googleapiclient.discovery import build
import uuid
from app_teacher.models import GoogleCalendarLessonEvents, GoogleCalendarSubscription


# Create your views here.
def redirect_to_homepage(request):
    if request.user.is_student:
        url = reverse('app_student:home')
        return redirect(url)
    elif request.user.is_teacher:
        url = reverse('app_teacher:home')
        return redirect(url)


def home(request):
    return redirect('app_base:login')
    # return render(#request, 'base/home.html')


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
            
            if user.is_student:
                StudentProfile.objects.create(
                    user=user
                )
            elif user.is_teacher:
                TeacherProfile.objects.create(
                    user=user
                )

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
        except Exception:
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
class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=False)


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

    EmailThread(email).start()
    messages.success(request, 'Email Varification Sent')

    if request.method == 'POST':
        return redirect('app_base:login')


def activate_account(request, uidb64, token):
    try:
        uuid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(uuid = uuid)
    except Exception:
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


################## Google Calendar ########################
def google_login(request, classroom_uuid):
    flow = Flow.from_client_config(
        client_config={
            'web': {
                'client_id': GOOGLE_OAUTH2_CLIENT_ID,
                'client_secret': GOOGLE_OAUTH2_CLIENT_SECRET,
                'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                'token_uri': 'https://accounts.google.com/o/oauth2/token'
            }
        },
        scopes=['https://www.googleapis.com/auth/calendar'],
        redirect_uri=google_oauth2_redirect_url,
    )

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    request.session['classroom_uuid'] = str(classroom_uuid)
    request.session['state'] = state
    request.session.save()

    return redirect(authorization_url)


def google_callback(request):
    state = request.session.get('state')

    flow = Flow.from_client_config(
        client_config={
            'web': {
                'client_id': GOOGLE_OAUTH2_CLIENT_ID,
                'client_secret': GOOGLE_OAUTH2_CLIENT_SECRET,
                'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                'token_uri': 'https://accounts.google.com/o/oauth2/token'
            }
        },
        scopes=['https://www.googleapis.com/auth/calendar'],
        state=state,
        redirect_uri=google_oauth2_redirect_url,
    )

    flow.fetch_token(authorization_response=request.build_absolute_uri())

    credentials = flow.credentials

    classroom_uuid_str = request.session.get('classroom_uuid')
    classroom_uuid = uuid.UUID(classroom_uuid_str)

    if 'classroom_uuid' in request.session:
        del request.session['classroom_uuid']


    return add_google_calendar_classroom_sbscription(request, credentials, classroom_uuid)


def add_google_calendar_classroom_sbscription(request, credentials, classroom_uuid):
    service = build('calendar', 'v3', credentials=credentials)

    classroom = get_object_or_404(Classroom, uuid=classroom_uuid)

    user_subscription = GoogleCalendarSubscription.objects.filter(user=request.user, classroom=classroom)

    if user_subscription.exists():
        if request.user.is_teacher:
            messages.error(request, _('classroom_already_added_to_google_calendar'))
            redirect_url = reverse('app_teacher:classroom-detail', kwargs={'uuid': classroom.uuid})
        elif request.user.is_student:
            messages.error(request, _('classroom_already_added_to_google_calendar'))
            redirect_url = reverse('app_student:classroom-detail', kwargs={'uuid': classroom.uuid})
        else:
            messages.error(request, _('error_in_class_subscription'))
            redirect_url = reverse('app_base:home')
        
        return redirect(redirect_url)


    db_current_subscription = GoogleCalendarSubscription.objects.create(
        user=request.user,
        classroom=classroom
    )

    lessons = Lesson.objects.filter(classroom=classroom)

    error_occurred = False
    for lesson in lessons:
        try:
            google_calendar_event = add_event_to_google_calendar(service, lesson)
        except Exception:
            messages.error(request, f'{lesson.name}: ' + _('error_adding_lesson_event_to_google_calendar'))
            error_occurred = True

        try:
            db_cur_lesson_event = GoogleCalendarLessonEvents.objects.create(
                subscription=db_current_subscription,
                lesson=lesson,
                google_calendar_event_id = google_calendar_event['id']
            )
        except Exception as e:
            messages.error(request, f'{lesson.name}: ' + _('error_adding_lesson_event_to_database'))
            error_occurred = True
    
    if not error_occurred:
        messages.success(request, _('classroom_sucessfully_added_to_calendar'))
    
    if request.user.is_teacher:
        redirect_url = reverse('app_teacher:classroom-detail', kwargs={'uuid': classroom.uuid})
    elif request.user.is_student:
        redirect_url = reverse('app_student:classroom-detail', kwargs={'uuid': classroom.uuid})
    else:
        messages.error(request, _('error_in_class_subscription'))
        redirect_url = reverse('app_base:home')
    
    return redirect(redirect_url)



def check_event_exists(service, event_id):
    try:
        # Attempt to get the event by its ID
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        return True  # Event exists, return True and the event details
    except Exception as e:
        return False  # Event does not exist, return False
    

def add_event_to_google_calendar(service, lesson):
    event = {
        'summary': lesson.name,
        'description': lesson.description,
        'start': {
            'dateTime': f'{lesson.lesson_date.isoformat()}T{lesson.lesson_start_time.isoformat()}',
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': f'{lesson.lesson_date.isoformat()}T{lesson.lesson_end_time.isoformat()}',
            'timeZone': 'UTC',
        },
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()
    
    return created_event
    