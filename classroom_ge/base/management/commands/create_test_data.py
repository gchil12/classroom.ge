from django.core.management.base import BaseCommand
from base.models import User

class Command(BaseCommand):
    help = 'Initialize test data in the database'
    passford_for_dummy_users = '1a2B345!'
    n_teachers = 5
    n_students = 10
    max_classrooms = 3
    max_lessons_per_classroom = 7

    def create_users(self):
        for teacher_id in range(self.n_teachers):
            try:
                self.teacher_1 = User.objects.create_user(
                    email = f'testteacher{teacher_id}@email.com',
                    password = self.passford_for_dummy_users,
                    name = f'TeacherName_{teacher_id}',
                    surname = f'TeacherSurname_{teacher_id}',
                    date_of_birth = '1965-12-11',
                    school = f'TeacherSchool_{teacher_id}',
                    city = f'TeacherCity_{teacher_id}',
                    is_student = False,
                    is_teacher = True,
                    email_verified = True
                )
            except Exception as e:
                f'Error creating teacher: {e}'
                print(f'User testteacher{teacher_id}@email.com exists')


        for student_id in range(self.n_students):
            try:
                User.objects.create_user(
                    email = f'teststudent{student_id}@email.com',
                    password = self.passford_for_dummy_users,
                    name = f'StudentName_{student_id}',
                    surname = f'StudentSurname_{student_id}',
                    date_of_birth = '1965-12-11',
                    school = f'StudentSchool_{student_id}',
                    city = f'StudentCity_{student_id}',
                    is_student = True,
                    is_teacher = False,
                    email_verified = True
                )
            except Exception as e:
                f'Error creating student: {e}'
                print(f'User teststudent{student_id}@email.com exists')
