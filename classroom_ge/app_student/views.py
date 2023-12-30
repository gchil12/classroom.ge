from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from app_teacher.models import Classroom, Lesson, Test, TestQuestion
from base.models import QuestionChoice
from .models import StudentToClassroom, StudentProfile, StudentTest, StudentQuestion, StudentQuestionToChoice
from django.utils import timezone
from django.db.models import Count, Q, Subquery, OuterRef, Exists
from django.db.models import BooleanField, Case, When, Value, F, Sum, IntegerField
from django.db.models.functions import Coalesce
from random import shuffle


@login_required(login_url='app_base:login')
def student_homepage(request):
    if not request.user.is_student:
        return redirect('app_base:home')
    
    student_to_classrooms = StudentToClassroom.objects.filter(student=request.user)

    now = timezone.now()

    closest_lessons = Lesson.objects.filter(
        Q(lesson_date__gt=now.date()) | (Q(lesson_date=now.date()) & Q(lesson_start_time__gte=now.time())),
        classroom__studenttoclassroom__student=request.user,
    ).distinct().annotate(
        classroom_name=F('classroom__name'),
        classroom_uuid=F('classroom__uuid'),
        classroom_subject=F('classroom__subject__name'),
    ).order_by(
        'lesson_date', 'lesson_start_time'
    ).values('lesson_start_time', 'name', 'uuid', 'lesson_date', 'classroom_name', 'classroom_uuid', 'classroom_subject')[:5]


    incomplete_test_subquery = StudentTest.objects.filter(
        student=StudentProfile.objects.get(user=request.user),
        test=OuterRef('pk'),
        completed=False
    )

    # Query for tests
    upcoming_tests = Test.objects.filter(
        Q(studenttest__isnull=True) |  # Test not attempted by the student
        Exists(incomplete_test_subquery),  # Test attempted but not completed
        Q(deadline__gt=now.date()) | Q(deadline__isnull=True),
        lesson__classroom__in=student_to_classrooms.values('classroom')
    ).distinct().annotate(
        classroom_name=F('lesson__classroom__name'),
        classroom_uuid=F('lesson__classroom__uuid'),
        classroom_subject=F('lesson__classroom__subject__name'),
        lesson_name=F('lesson__name'),
        lesson_uuid=F('lesson__uuid'),
    ).order_by('deadline').values(
        'name', 'uuid', 'deadline', 'classroom_name', 'classroom_uuid', 'classroom_subject', 'lesson_name', 'lesson_uuid',
    )[:5]  # Replace 'some_date_field' with the field you use to determine the closeness of the test


    context = {
        'student_to_classrooms': student_to_classrooms,
        'closest_lessons': closest_lessons,
        'upcoming_tests': upcoming_tests,
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

    current_student = get_object_or_404(StudentProfile, user=request.user)

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


    for classroom in classrooms_extended_table:
        lessons = Lesson.objects.filter(classroom=classroom)

        n_tests_to_write = 0

        for lesson in lessons:
            tests = Test.objects.filter(lesson=lesson)

            

            for test in tests:
                student_test = StudentTest.objects.filter(student=current_student, test=test).first()

                if student_test is None:
                    n_tests_to_write += 1
                else:
                    if not student_test.completed and (student_test.test.deadline and student_test.test.deadline > timezone.now().date() or student_test.test.deadline is None):
                        n_tests_to_write += 1

            
        classroom.tests_to_write = n_tests_to_write

    context = {
        'classrooms': classrooms_extended_table,
    }
    return render(request, 'app_student/menu_elements/classrooms.html', context)



@login_required(login_url='app_base:login')
def classroom_details(request, uuid):
    if not request.user.is_student:
        return redirect('app_base:home')
    
    classroom = get_object_or_404(Classroom, uuid=uuid)
    
    try:
        StudentToClassroom.objects.get(
            student=request.user,
            classroom=classroom
        )
    except Exception:
        redirect_url = reverse('app_student:subscribe-classroom', kwargs={'classroom_uuid': uuid})
        return redirect(redirect_url)

    current_student = get_object_or_404(StudentProfile, user=request.user)

    num_tests_subquery = Test.objects.filter(
        lesson=OuterRef('pk')
    ).order_by().values('lesson_id').annotate(
        test_count=Count('pk')
    ).values('test_count')

    lessons = Lesson.objects.filter(classroom=classroom)

    for lesson in lessons:
        tests = Test.objects.filter(lesson=lesson)

        n_tests_to_write = 0

        for test in tests:
            student_test = StudentTest.objects.filter(student=current_student, test=test).first()

            if student_test is None:
                n_tests_to_write += 1
            else:
                if not student_test.completed and (student_test.test.deadline and student_test.test.deadline > timezone.now().date() or student_test.test.deadline is None):
                    n_tests_to_write += 1

        
        lesson.tests_to_write = n_tests_to_write

    context = {
        'lessons': lessons,
        'classroom': classroom,
    }

    return render(request, 'app_student/menu_elements/classroom_details.html', context)



@login_required(login_url='app_base:login')
def lesson_details(request, lesson_uuid):
    if not request.user.is_student:
        return redirect('app_base:home')

    lesson = get_object_or_404(Lesson, uuid=lesson_uuid)

    if not StudentToClassroom.objects.filter(student=request.user, classroom=lesson.classroom).exists():
        messages.error(request, _('error_unauthorized_access'))
        return redirect('app_student:home') #NOSONAR

    current_student = StudentProfile.objects.get(user=request.user)

    tests = Test.objects.filter(
        lesson=lesson
    )

    # Subquery to check if the current student has completed the test
    has_completed_subquery = StudentTest.objects.filter(
        test=OuterRef('pk'), 
        student=current_student
    ).annotate(
        has_completed=Coalesce(
            Case(
                When(completed=True, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            ),
            Value(False)
        )
    ).values('has_completed')[:1]  # Ensure it returns a single value

    # Annotate the tests with whether the current student has completed them
    tests = tests.annotate(
        completed=Subquery(has_completed_subquery),
        max_points=Sum(Case(
            When(studenttest__student=current_student, 
                then=F('studenttest__studentquestion__question__max_point'))
        )),
        total_points=Sum(Case(
            When(studenttest__student=current_student, 
                then=F('studenttest__studentquestion__given_point'))
        ))
    ).distinct().order_by('-date_created')  
    
    context = {
        'tests': tests,
        'lesson': lesson,
        'current_time': timezone.now().date()
    }

    return render(request, 'app_student/lesson_details.html', context)


@login_required(login_url='app_base:login')
def test_show_page(request, test_uuid):
    if not request.user.is_student:
        return redirect('app_base:home')
    
    now = timezone.now()
    
    test = get_object_or_404(Test, uuid=test_uuid)
    current_student = get_object_or_404(StudentProfile, user=request.user)

    student_test = StudentTest.objects.filter(student=current_student, test=test)
    student_test_exists = student_test.exists()

    if not student_test_exists:
        student_test = StudentTest.objects.create(
            student=current_student,
            test=test,
            completed=False,
            start_time=now,
            end_time=now
        )
        
        test_questions = list(TestQuestion.objects.filter(test=test).all())
        shuffle(test_questions)
        order_id = 0
        for test_question in test_questions:
            StudentQuestion.objects.create(
                student_test = student_test,
                question = test_question,
                order=order_id,
            )
            order_id += 1

        context = {
            'student_questions': StudentQuestion.objects.filter(student_test=student_test).all().order_by('order'),
            'student_test': student_test,
            'test': test,
        }
        
    else:
        student_test = get_object_or_404(StudentTest, student=current_student, test=test)

        student_questions = StudentQuestion.objects.filter(student_test=student_test).order_by('order')
        selected_choices = StudentQuestion.objects.filter(student_test=student_test).values_list('chosen_choices__pk', flat=True)

        context = {
            'student_questions': student_questions,
            'selected_choices': selected_choices,
            'student_test': student_test,
            'test': test,
        }


    if test.deadline == None or test.deadline >= now.date():
        return render(request, 'app_student/test_form.html', context)
    else:
        redirect_url = reverse('app_student:test-view', kwargs={'test_uuid': test.uuid})
        return redirect(redirect_url)
    



@login_required(login_url='app_base:login')
def test_submit(request, student_test_uuid):
    if not request.user.is_student:
        return redirect('app_base:home')
    
    now = timezone.now()

    current_student = get_object_or_404(StudentProfile, user=request.user)
    student_test = get_object_or_404(StudentTest, uuid=student_test_uuid)

    
    if student_test.student != current_student:
        messages.error(request, _('error_unauthorized_access'))
        return redirect('app_student:home') #NOSONAR
    
    if student_test.test.deadline is not None and student_test.test.deadline < now.date():
        messages.error(request, _('deadline_passed'))
        redirect_url = reverse('app_student:test-view', kwargs={'test_uuid': student_test.test.uuid})
        return redirect(redirect_url)
    
    if student_test.completed:
        redirect_url = reverse('app_student:test-view', kwargs={'test_uuid': student_test.test.uuid})
        return redirect(redirect_url)

    if request.method == 'POST':
        # Handle form submission
        student_test.end_time = now
        student_test.completed = True

        for student_question in student_test.studentquestion_set.all():
            choice_pk = request.POST.get(f'chosen_choices_{student_question.question.pk}')
            if choice_pk:
                choice = get_object_or_404(QuestionChoice, pk=choice_pk)
                StudentQuestionToChoice.objects.create(
                    student_question=student_question,
                    choice=choice,
                )

                student_question.answered = True

                if choice.is_correct:
                    student_question.given_point = student_question.question.max_point
                else:
                    student_question.given_point = 0

                student_question.save()

        student_test.save()

        messages.success(request, _('test_submitted_sucessfully'))
        redirect_url = reverse('app_student:test-view', kwargs={'test_uuid': student_test.test.uuid})
        return redirect(redirect_url)
    

    messages.success(request, _('something_is_wrong'))
    return redirect('app_student:home')
    



@login_required(login_url='app_base:login')
def view_computed_test(request, test_uuid):
    if not request.user.is_student:
        return redirect('app_base:home')
    
    test = get_object_or_404(Test,uuid=test_uuid)
    current_student = StudentProfile.objects.get(user=request.user)

    student_test = get_object_or_404(StudentTest, student=current_student, test=test)
    
    student_questions = StudentQuestion.objects.filter(student_test=student_test).order_by('order')
    
    
    context = {
        'student_questions': student_questions,
        'test': test,
    }

    return render(request, 'app_student/test_completed_overview.html', context)