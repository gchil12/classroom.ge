# Changes to make Django project work again

## Nov 25, 2023
### 1/2 Recaptcha
requirements.txt file was updated. Install the required packages to use reCaptcha.
Additionally, add private and public keys for reCaptcha in 'classroom_ge/my_constants.py':
```
captcha_public_key = 'str_private_key_obtained_from_google'
captcha_private_key = 'str_private_key_obtained_from_google'
```
Make sure to add '127.0.0.1' and 'localhost' in the 'Domains' when you register reCaptcha (https://www.google.com/recaptcha/about/)



### 2/2 Major changes in Database
As the authentification procedure was changed (custom User table was created), simple migration is not possilbe. As the database does not include anything special yet, the simplest way is to drop (delete) database and recreate it with new **custom** user table. Hereby I will write how to do it:

1) Firstly, we need to open interactive postgres session. In the terminal type:
```
sudo -u postgres psql
```
2) Now we should create postgres user and add some roles (if you already created the user, you can skip this step):
```
CREATE USER example_archili WITH PASSWORD example_archilis_password;
ALTER ROLE example_archili SET client_encoding TO 'utf8';
ALTER ROLE example_archili SET default_transaction_isolation TO 'read committed';
ALTER ROLE example_archili SET timezone TO 'UTC';
```
3) Now we should get rid of the old database. If you have not created the database, skip this step.
```
DROP DATABASE  classroom_ge;
```
4) Now, create the database again and grand privileges to your user:
```
CREATE DATABASE classroom_ge;
GRANT ALL PRIVILEGES ON DATABASE classroom_ge TO example_archili;
```
5) Now, you should delete migrations inside 'migrations' folders (basically, everything except of '__init__.py'):
- base/migrations
    - Delete directory __pycache__
    - Delete all python files except of __init__.py
- Repeat this for the following directories:
    - app_student/migrations
    - app_teacher/migrations
    - app_administrator/migrations
6) Now we can migrate!
```
python classroom_ge/manage.py makemigrations
python classroom_ge/manage.py migrate
```
> [!NOTE]
> As new user system is created (with more required fields than it was required by default django user), 'python classroom_ge/manage.py createsuperuser' will throw an error that some required stuff is missing. For this reason, I created a custom registration for superuser:
>   ```
>   python classroom_ge/manage.py createsuperuser2
>   ```
>
> This the example of superuser creation:
>   ```
>   archili@my_pc:/web/classroom.ge$ python classroom_ge/manage.py createsuperuser2
>   Username: asakevarashvili
>   Password:
>   Repeat Password:
>   Email: test@gmail.com
>   Repeat Email: test@gmail.com
>   Name: Archili
>   Surname: Sakevarashvili
>   Date of birth (Format: YYYY-MM-DD) (optional):
>   School (optional):
>   City (optional):
>   Superuser created successfully.
>   ```
> Note, that the "optional" fields are only optional to create superuser. Registration from website requires students to fill these fields.