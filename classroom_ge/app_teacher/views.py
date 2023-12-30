from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import gettext_lazy as _
from app_student.models import StudentToClassroom, StudentProfile, StudentTest, StudentQuestion
from django.contrib import messages
from django.db.models import Count, Q, Subquery, OuterRef, Avg, FloatField, ExpressionWrapper, IntegerField, Exists, BooleanField
from django.db.models import Case, When, Value, F, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from base.models import Topic, Question, QuestionToTopic
from .models import Classroom, Lesson, Level, ClassroomToLevels
from .forms import CreateNewClassroomForm, CreateNewLessonForm, DateForm
import json
import uuid as unique_id_import
import uuid
from .models import Test, TestQuestion
from collections import OrderedDict
import numpy as np

# Create your views here.
@login_required(login_url='app_base:login')
def teacher_homepage(request):
    if not request.user.is_teacher:
        return redirect('app_base:home') #NOSONAR
    
    now = timezone.now()
    # Subquery for closest lessons in Classrooms (for closest_lessons)
    closest_lesson_subquery = Lesson.objects.filter(
        Q(lesson_date__gt=now.date()) | (Q(lesson_date=now.date()) & Q(lesson_start_time__gte=now.time())),
        classroom=OuterRef('pk'),
        classroom__owner=request.user,
    ).order_by('lesson_date', 'lesson_start_time').values('lesson_start_time', 'name', 'lesson_date')[:5]


    classrooms_extended_table = Classroom.objects.annotate(
        num_levels=Count('classroomtolevels__level'),
        num_students=Count('studenttoclassroom__student', filter=Q(studenttoclassroom__student__is_student=True)),
        closest_lesson_start_time=Subquery(closest_lesson_subquery[:1].values('lesson_start_time')),
        closest_lesson_name=Subquery(closest_lesson_subquery[:1].values('name')),
        closest_lesson_date=Subquery(closest_lesson_subquery[:1].values('lesson_date')),
    ).filter(owner=request.user)

    classrooms_with_rank = annotate_classrooms_with_rank(classrooms_extended_table, now)

    user_classrooms = request.user.classroom_set.all()

    all_lessons = []
    for classroom in user_classrooms:
        lessons = classroom.lesson_set.filter(
            Q(lesson_date__gt=now.date()) | (Q(lesson_date=now.date()) & Q(lesson_start_time__gte=now.time()))
        )
        all_lessons.extend(lessons)

    # Sort all lessons by date and time
    closest_lessons = sorted(all_lessons, key=lambda lesson: (lesson.lesson_date, lesson.lesson_start_time))[:5]

    context = {
        'classrooms': classrooms_with_rank,
        'closest_lessons': closest_lessons,
    }
    
    return render(request, 'app_teacher/menu_elements/teacher_homepage.html', context)


############### Classrooms #################
def annotate_classrooms_with_rank(classrooms_extended_table, now):
    # Convert queryset to list and add rank
    classrooms_with_rank = list(classrooms_extended_table)

    for classroom in classrooms_with_rank:
        classroom_lessons = Lesson.objects.filter(classroom=classroom)

        student_to_classroom = StudentToClassroom.objects.filter(classroom=classroom)

        student_points = 0
        total_points = 0

        for student_classroom in student_to_classroom:
            student_profile = StudentProfile.objects.get(user=student_classroom.student)

            for lesson in classroom_lessons:
                tests = Test.objects.filter(
                    lesson=lesson
                ).annotate(
                    total_max_point = Sum(F('testquestion__max_point'))
                )

                for test in tests:
                    student_test = StudentTest.objects.filter(student=student_profile, test=test.uuid).first()

                    if student_test and student_test.completed:
                        student_points += StudentQuestion.objects.filter(student_test=student_test).aggregate(Sum('given_point'))['given_point__sum'] or 0
                    elif test.deadline:
                        if test.deadline < now.date():
                            student_points += 0
                        else:
                            continue
                    else:
                        continue

                    total_points += test.total_max_point

        classroom.rank = round(student_points/total_points*100, 3) if total_points else 0

    return classrooms_with_rank


@login_required(login_url='app_base:login')
def classrooms(request):
    if not request.user.is_teacher:
        return redirect('app_base:home')
    
    now = timezone.now()
    closest_lesson_subquery = Lesson.objects.filter(
        Q(lesson_date__gt=now.date()) | (Q(lesson_date=now.date()) & Q(lesson_start_time__gte=now.time())),
        classroom=OuterRef('pk'),
    ).order_by('lesson_date', 'lesson_start_time').values('lesson_start_time', 'name', 'lesson_date')[:1]

    classrooms_extended_table = Classroom.objects.annotate(
        num_levels=Count('classroomtolevels__level'),
        num_students=Count('studenttoclassroom__student', filter=Q(studenttoclassroom__student__is_student=True)),
        closest_lesson_start_time=Subquery(closest_lesson_subquery.values('lesson_start_time')),
        closest_lesson_name=Subquery(closest_lesson_subquery.values('name')),
        closest_lesson_date=Subquery(closest_lesson_subquery.values('lesson_date')),
    ).filter(owner=request.user)

    classrooms_with_rank = annotate_classrooms_with_rank(classrooms_extended_table, now)

    return render(request, 'app_teacher/menu_elements/classrooms_page.html', {'classrooms': classrooms_with_rank})


@login_required(login_url='app_base:login')
def classroom_details(request, uuid):
    if not request.user.is_teacher:
        return redirect('app_base:home')
    
    current_date = timezone.now().date()

    classroom = get_object_or_404(Classroom, uuid=uuid)

    if classroom.owner != request.user:
        messages.error(request, _('error_unauthorized_access'))
        return redirect('app_teacher:home') #NOSONAR

    lessons = Lesson.objects.filter(classroom=classroom)

    student_to_classrooms = StudentToClassroom.objects.filter(classroom=classroom)

    all_tests = Test.objects.filter(
        lesson__classroom = classroom
    ).annotate(
        total_max_point = Sum(F('testquestion__max_point'))
    )

    students_with_scores = {}

    for student_classroom in student_to_classrooms:
        student = student_classroom.student
        student_profile = StudentProfile.objects.get(user=student)

        students_with_scores[student] = {'given_point': 0, 'max_point': 0}

        for test in all_tests:
            student_test = StudentTest.objects.filter(student=student_profile, test=test.uuid).first()
            
            if student_test and student_test.completed:
                given_points = StudentQuestion.objects.filter(student_test=student_test).aggregate(Sum('given_point'))['given_point__sum'] or 0
            elif test.deadline:
                if test.deadline < current_date:
                    given_points = 0
                else:
                    continue
            else:
                continue
            
            students_with_scores[student]['given_point'] += given_points
            students_with_scores[student]['max_point'] += test.total_max_point


        students_with_scores[student]['score'] = 100*students_with_scores[student]['given_point'] / students_with_scores[student]['max_point'] if students_with_scores[student]['max_point'] > 0 else 0
        students_with_scores[student]['score'] = round(students_with_scores[student]['score'],3)
    

    students_with_scores = OrderedDict(sorted(students_with_scores.items(), key=lambda item: item[1]['score'], reverse=True))

    domain = get_current_site(request).domain
    
    context = {
        'classroom': classroom,
        'lessons': lessons,
        'domain': domain,
        'students_with_scores': students_with_scores,
    }

    return render(request, 'app_teacher/classroom/classroom_details.html', context)
    

@login_required(login_url='app_base:login')
def new_classroom(request):
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
            
            try:
                classroom_to_level = ClassroomToLevels.objects.create(
                    classroom=classroom,
                    level = level,
                )
                classroom_to_level.save()
            except Exception:
                # Pair Exists or user did not chose anything
                pass

            
            messages.success(request, _('new_class_created'))
            redirect_url = reverse('app_teacher:classroom-detail', kwargs={'uuid': classroom.uuid}) #NOSONAR
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



@login_required(login_url='app_base:login')
def lesson_details(request, uuid):
    if not request.user.is_teacher:
        return redirect('app_base:home')

    lesson = get_object_or_404(Lesson, uuid=uuid)
    
    if lesson.classroom.owner != request.user:
        messages.error(request, _('error_unauthorized_access'))
        return redirect('app_teacher:home')

    # Number of students in the classroom
    n_students = len(StudentToClassroom.objects.filter(
        classroom=lesson.classroom
    ))

    # Tests in current classroom
    tests = Test.objects.filter(lesson=lesson)

    # Maximum Score for Each Test
    tests = tests.annotate(
        max_score=Sum('testquestion__max_point')
    )

    # Total Points for Each Student Test
    total_points_subquery = StudentQuestion.objects.filter(
        student_test__test=OuterRef('pk')
    ).values(
        'student_test__test'
    ).annotate(
        total_given_points=Sum('given_point')
    ).values(
        'total_given_points'
    )

    tests = tests.annotate(
        students_completed=Count('studenttest__student', filter=Q(studenttest__completed=True), distinct=True),
    )

    if n_students > 0:
        # Average Performance + Number of students who completed the test
        tests = tests.annotate(
            total_points=Subquery(total_points_subquery, output_field=FloatField()),
            average_performance=ExpressionWrapper(
                Coalesce(
                    Avg(Case(
                        When(total_points__isnull=False, then='total_points'),
                        default=0,
                        output_field=FloatField()
                    )),
                    Value(0)
                ) / F('max_score')*100,
                output_field=FloatField()
            ),
        ).order_by('-date_created')
    else:
        tests = tests.annotate(
            average_performance=Value(0.0, output_field=FloatField())
        )


    context = {
        'lesson': lesson,
        'tests': tests,
        'n_students': n_students,
    }

    return render(request, 'app_teacher/classroom/lesson.details.html', context)


############### Tests/Exercises #################
@login_required(login_url='app_base:login')
def tests_main_page(request):
    if not request.user.is_teacher:
        return redirect('app_base:home')

    subject_filter = request.GET.get('subject_filter', '')
    topic_filter = request.GET.get('topic_filter', '')

    lesson_uuid = request.GET.get('lesson', '')
    print(lesson_uuid)
    try:
        lesson = Lesson.objects.get(uuid=lesson_uuid)
    except Exception:
        lesson = None

    topics_with_at_least_one_question = Topic.objects.annotate(
        n_questions=Count('question')
    ).filter(n_questions__gte=1).order_by('identifier')

    if subject_filter:
        topics_with_at_least_one_question = topics_with_at_least_one_question.filter(subject__name__icontains=subject_filter)
    if topic_filter:
        topics_with_at_least_one_question = topics_with_at_least_one_question.filter(name__icontains=topic_filter)

    if subject_filter:
        topics_with_at_least_one_question = topics_with_at_least_one_question.filter(subject__name__icontains=subject_filter)
    if topic_filter:
        topics_with_at_least_one_question = topics_with_at_least_one_question.filter(name__icontains=topic_filter)

    context = {
        'topics': topics_with_at_least_one_question,
        'lesson': lesson,
    }

    return render(request, 'app_teacher/menu_elements/tests.html', context)



@login_required(login_url='app_base:login')
def test_example_page(request, uuid):
    if not request.user.is_teacher:
        return redirect('app_base:home')
    
    # Try to get lesson UUID from URL
    try:
        lesson_uuid = request.GET.get('lesson')
        uuid_obj = unique_id_import.UUID(lesson_uuid)
        
        # UUID OK
        if uuid_obj:
            lesson = get_object_or_404(Lesson, uuid=lesson_uuid)

            # Lesson belongs to current teacher
            if lesson.classroom.owner != request.user:
                messages.error(request, _('error_unauthorized_access'))
                return redirect('app_teacher:home')
        else:
            lesson = None
    except Exception:
        lesson = None
        
    
    topic = get_object_or_404(Topic, uuid=uuid)
    
    questions_for_topic = Question.objects.filter(questiontotopic__topic=topic).order_by('uuid').prefetch_related('questionchoice_set')

    context = {
        'topic': topic,
        'questions': questions_for_topic,
        'lesson': lesson,
    }

    return render(request, 'app_teacher/tests/test_example_page.html', context)



def create_test_questions(topic_uuid:uuid, lesson_uuid:uuid, deadline):
    topic = get_object_or_404(Topic, uuid=topic_uuid)
    lesson = get_object_or_404(Lesson, uuid=lesson_uuid)
    
    try:
        cur_test = Test.objects.create(
            lesson=lesson,
            name=topic.name,
            test_type='assignment',
            deadline=deadline
        )
    except Exception as e:
        return False
    

    for question in topic.questions.all():
        try:
            TestQuestion.objects.create(
                test=cur_test,
                question=question,
                max_point=1,
            )
        except Exception as e:
            return False
        
    return True
    


@login_required(login_url='app_base:login')
def choose_lessons_to_add_test(request, topic_uuid):
    if not request.user.is_teacher:
        return redirect('app_base:home')

    # Choosing classroom
    classroom_uuid = request.GET.get('classroom')

    try:
        # Classroom already chosen by user
        classroom = Classroom.objects.get(uuid=classroom_uuid)
    except Exception:
        # Classroom was not chosen yet
        classrooms = Classroom.objects.filter(
            owner=request.user,
        )

        now = timezone.now()
        closest_lesson_subquery = Lesson.objects.filter(
            Q(lesson_date__gt=now.date()) | (Q(lesson_date=now.date()) & Q(lesson_start_time__gte=now.time())),
            classroom=OuterRef('pk'),
        ).order_by('lesson_date', 'lesson_start_time').values('lesson_start_time', 'name', 'lesson_date')[:1]
            
        classrooms = Classroom.objects.annotate(
            num_levels=Count('classroomtolevels__level'),
            num_students=Count('studenttoclassroom__student', filter=Q(studenttoclassroom__student__is_student=True)),
            closest_lesson_start_time=Subquery(closest_lesson_subquery[:1].values('lesson_start_time')),
            closest_lesson_name=Subquery(closest_lesson_subquery[:1].values('name')),
            closest_lesson_date=Subquery(closest_lesson_subquery[:1].values('lesson_date')),
        ).filter(owner=request.user)

        classrooms = annotate_classrooms_with_rank(classrooms, now)
        return render(request, 'app_teacher/tests/add_test_to_lesson.html', {'classrooms': classrooms, 'topic_uuid': topic_uuid})


    # Classroom does not belong to teacher
    if classroom.owner != request.user:
        messages.error(request, _('error_unauthorized_access'))
        return redirect('app_teacher:home')

    
    # Choosing lesson
    lesson_uuid = request.GET.get('lesson')

    try:
        # Lesson already chosen by user
        lesson = Lesson.objects.get(uuid=lesson_uuid)
    except Exception:
        classroom=Classroom.objects.get(uuid=classroom_uuid)
        # Lesson was not chosen yet
        lessons = Lesson.objects.filter(
            classroom=classroom
        )
        return render(request, 'app_teacher/tests/add_test_to_lesson.html', {'lessons': lessons, 'topic_uuid': topic_uuid, 'classroom': classroom},)


    # Lesson does not belong to teacher
    if lesson.classroom.owner != request.user:
        messages.error(request, _('error_unauthorized_access'))
        return redirect('app_teacher:home')
    
    redirect_url = reverse('app_teacher:add-test-confirmation', kwargs={'classroom_uuid': classroom_uuid, 'lesson_uuid': lesson_uuid, 'topic_uuid': topic_uuid})
    return redirect(redirect_url)


@login_required(login_url='app_base:login')
def add_test_to_lesson_confirmation(request, classroom_uuid, lesson_uuid, topic_uuid):
    classroom = Classroom.objects.get(uuid=classroom_uuid)
    lesson = Lesson.objects.get(uuid=lesson_uuid)
    topic = get_object_or_404(Topic, uuid=topic_uuid)

    context = {
        'classroom': classroom,
        'lesson': lesson,
        'topic': topic
    }

    if request.method == 'POST':
        form = DateForm(request.POST)
        try:
            if form.is_valid():
                deadline = form.cleaned_data['deadline']

                # Adding test to lesson
                try: 
                    res = create_test_questions(topic_uuid, lesson_uuid, deadline)

                    if res:
                        messages.success(request, _('exercises_added_successfully'))
                        redirect_url = reverse('app_teacher:lesson-detail', kwargs={'uuid': lesson_uuid})
                        return redirect(redirect_url)
                    else:
                        messages.error(request, _('unknown_error_refresh'))
                        return redirect('app_teacher:home')
                except Exception:
                    messages.error(request, _('unknown_error_refresh'))
                    return redirect('app_teacher:home')
            else:
                raise Exception
        except Exception:
            messages.error(request, _('invalid_input'))
            context['deadline_form'] = DateForm()
            return render(request, 'app_teacher/tests/add_test_to_lesson_confirmation_page.html', context)
    else:
        deadline_form = DateForm()

        context['deadline_form'] = deadline_form
        return render(request, 'app_teacher/tests/add_test_to_lesson_confirmation_page.html', context)



@login_required(login_url='app_base:login')
def test_details(request, test_uuid):
    if not request.user.is_teacher:
        return redirect('app_base:home')
    
    test = get_object_or_404(Test, uuid=test_uuid)

    if test.lesson.classroom.owner != request.user:
        messages.error(request, _('error_unauthorized_access'))
        return redirect('app_teacher:home')

    students = StudentProfile.objects.filter(
        user__studenttoclassroom__classroom=test.lesson.classroom
    ).annotate(
        max_points=Subquery(
            StudentTest.objects.filter(
                student=OuterRef('pk'),
                test=test,
            ).annotate(
                total_max_points=Sum('studentquestion__question__max_point')
            ).values('total_max_points')
        ),
        student_points=Subquery(
            StudentTest.objects.filter(
                student=OuterRef('pk'),
                test=test,
            ).annotate(
                student_points=Sum('studentquestion__given_point')
            ).values('student_points')
        ),
        completed=Subquery(
            StudentTest.objects.filter(
                student=OuterRef('pk'),
                test=test,
            ).values('completed')
        ),
    )


    student_points = [student.student_points for student in students if student.student_points is not None and student.completed]
    print(student_points)
    student_points_histogram, student_points_bin_edges = np.histogram(student_points, bins=range(11))

    # Convert histogram data to a format suitable for Chart.js
    
    student_points = student_points_histogram.tolist()
    student_points_labels = [f'{int(student_points_bin_edges[i])}' for i in range(len(student_points_bin_edges)-1)]
    
    context={
        'students': students,
        'test': test,
        'student_points': student_points,
        'student_points_label': student_points_labels,
    }

    return render(request, 'app_teacher/tests/test_details.html', context)



@login_required(login_url='app_base:login')
def test_results_student(request, test_uuid, student_uuid):
    if not request.user.is_teacher:
        return redirect('app_base:home')
    
    test = get_object_or_404(Test,uuid=test_uuid)
    current_student = StudentProfile.objects.get(uuid=student_uuid)

    student_test = get_object_or_404(StudentTest, student=current_student, test=test)
    
    student_questions = StudentQuestion.objects.filter(student_test=student_test).order_by('question__question__uuid')
    
    
    context = {
        'test': test,
        'student_questions': student_questions,
        'student_test': student_test,
    }

    return render(request, 'app_student/test_completed_overview.html', context)


@login_required(login_url='app_base:login')
def test_delete(request, test_uuid):
    if not request.user.is_teacher:
        return redirect('app_base:home')
    
    test = get_object_or_404(Test,uuid=test_uuid)
    lesson_uuid = test.lesson.uuid

    if test.lesson.classroom.owner != request.user:
        messages.error(request, _('error_unauthorized_access'))
        return redirect('app_teacher:home')

    
    if request.method == 'POST':        
        messages.success(request, _('test_deleted'))
        test.delete()

        redirect_url = reverse('app_teacher:lesson-detail', kwargs={'uuid': lesson_uuid})
        return redirect(redirect_url)
    else:
        return render(request, 'app_teacher/tests/confirm_test_deletion.html', {'test': test, 'lesson_uuid': lesson_uuid})