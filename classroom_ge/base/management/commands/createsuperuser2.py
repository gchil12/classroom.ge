from django.core.management.base import BaseCommand
from base.models import User
import getpass
from django.core import validators
from django.core.exceptions import ValidationError

class Command(BaseCommand):
    help = 'Create a superuser with custom questions'

    def handle(self, *args, **options):
        # Validate username
        while True:
            username = input('Username: ')

            if len(username) < 5:
                print('\033[91mUsername should be at least 5 character long\033[0m')
            else:
                break

        
        # Validate Password
        while True:
            password = getpass.getpass('Password: ')

            if len(password) < 8:
                print('\033[91mPassword should be at least 8 character long\033[0m')
            else:
                break

        repeat = 0
        while True:
            password_repeat = getpass.getpass('Repeat password: ')
            
            if password == password_repeat:
                break
            
            print('\033[91mPasswords do not match\033[0m')
            repeat += 1

            if repeat == 3:
                break

        
        # Validate Email
        while True:
            validator = validators.EmailValidator()
            email = input('Email: ')

            try:
                validator(email)
                break
            except ValidationError as e:
                print('\033[91mInvalid Email\033[0m')


        while True:
            validator = validators.EmailValidator()
            email_repeat = input('Repeat email: ')

            try:
                validator(email_repeat)

                if email_repeat == email:
                    break
                else:
                    print('\033[91mEmails do not match\033[0m')
            except ValidationError as e:
                print('\033[91mInvalid Email\033[0m')
        

        while True:
            name = input('Name (required): ')

            if len(name) == 0:
                print('\033[91mThis field is mandatory\033[0m')
            else:
                break

        
        while True:
            surname = input('Surname (required): ')

            if len(surname) == 0:
                print('\033[91mThis field is mandatory\033[0m')
            else:
                break

        
        date_of_birth = input('Date of birth (Format: YYYY-MM-DD) (optional): ')
        if len(date_of_birth) == 0:
            date_of_birth = '0001-01-01'

        school = input('School (optional): ')
        city = input('City (optional): ')

        # Perform additional actions if needed, such as validation or customization

        User.objects.create_superuser(
            username = username,
            email = email,
            password = password,
            name = name,
            surname = surname,
            date_of_birth = date_of_birth,
            school = school,
            city = city
        )

        self.stdout.write(self.style.SUCCESS('Superuser created successfully.'))