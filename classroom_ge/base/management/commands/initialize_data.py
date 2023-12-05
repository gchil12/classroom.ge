from django.core.management.base import BaseCommand
from base.models import Subject, User
from app_teacher.models import Level
from classroom_ge.settings import LANGUAGES


class Command(BaseCommand):
    help = 'Initialize data in the database'

    def create_basic_fields(self):
        try:
            self.subject = Subject.objects.create(name_ka='მათემატიკა')
        except:
            print('Subject Math Already Exists')

        for level in range(1,13):
            try:
                Level.objects.create(level=level)
            except:
                print(f'Level {level} already exists')
    

    def create_users(self):
        try:
            self.teacher_1 = User.objects.create_user(
                email = 'testteacher1@email.com',
                password = '1a2B345!',
                name = 'TeacherName_1',
                surname = 'TeacherSurname_1',
                date_of_birth = '1965-12-11',
                school = 'TeacherSchool_1',
                city = 'TeacherCity_1',
                is_student = False,
                is_teacher = True,
                email_verified = True
            )
        except:
            print(f'User testteacher1@email.com exists')


        try:
            self.teacher_2 = User.objects.create_user(
                email = 'testteacher2@email.com',
                password = '1a2B345!',
                name = 'TeacherName_2',
                surname = 'TeacherSurname_2',
                date_of_birth = '1965-12-11',
                school = 'TeacherSchool_2',
                city = 'TeacherCity_2',
                is_student = False,
                is_teacher = True,
                email_verified = True
            )
        except:
            print(f'User testteacher2@email.com exists')


        try:
            self.student_1 = User.objects.create_user(
                email = 'teststudent1@email.com',
                password = '1a2B345!',
                name = 'StudentName_1',
                surname = 'StudentSurname_1',
                date_of_birth = '1965-12-11',
                school = 'StudentSchool_1',
                city = 'StudentCity_1',
                is_student = True,
                is_teacher = False,
                email_verified = True
            )
        except:
            print(f'User teststudent1@email.com exists')


        try:
            self.student_2 = User.objects.create_user(
                email = 'teststudent2@email.com',
                password = '1a2B345!',
                name = 'StudentName_2',
                surname = 'StudentSurname_2',
                date_of_birth = '1965-12-11',
                school = 'StudentSchool_2',
                city = 'StudentCity_2',
                is_student = True,
                is_teacher = False,
                email_verified = True
            )
        except:
            print(f'User teststudent2@email.com exists')

    

    def handle(self, *args, **options):
        # Add Subject
        self.create_basic_fields()
        self.create_users()

        

        