# classroom.ge


## Initial Setup

### Initial Steps
1) Importand sudo installs:
    ```
    sudo apt update
    sudo apt install libpq-dev postgresql postgresql-contrib curl
    ```
2) Clone git repo: https://github.com/gchil12/classroom.ge.git


### Python virtual environment + pip
1) Install 'python3.10' on the system. To install specific version of python check this link: https://www.neurotec.uni-bremen.de/drupal/node/23
2) Install 'pip3.10'
    ```
    python3.10 -m ensurepip --upgrade
    ```
3) Install 'virtualenv'
    ```
    pip3.10 install virtualenv
    ```
3) cd to directory for classroom.ge
4) Create virtual environment
    ```
    virtualenv venv
    ```
5) Activating virtual environment:
    ```
    source venv/bin/activate
    ```
6) Verify Python version:
    ```
    python --verstion (if this does not work, try python3 --version)
    ```
7) Upgrade pip:
    ```
    pip install --upgrade pip
    ```
8) Install requirements stored in requirements.txt
    ```
    python -m pip install -r requirements.txt
    ```
8) To deactivate virtual environment run:
    ```
    deactivate
    ```


### Django
1) Install pip (skip this step if you installed requirements.txt)
    ```
    pip install Django
    ```
2) Verify installation:
    ```
    python -m django --version
    ```


### Database
1) Install postgresql (skip this step if you installed requirements.txt)
    ```
    pip install psycopg[binary]
    ```


### Support for multiple languages
On linux everything should be already there. On Windows (and maybe Mac OS, have no idea),
you should install it by yourself, because Microsoft employees really want me to learn
anger management:
1) Download and install following binary (static):
    https://mlocati.github.io/articles/gettext-iconv-windows.html
    REMARK: You should restart PC after installation

Here is a link about django translation:
    https://testdriven.io/blog/multiple-languages-in-django/


> [!WARNING]
> The local server will not run, as the instance of the database is not created yet.
> To initiate database and create user:
> - Create database and user with permissions:
>   - Log into an interactive Postgres session with command:
>       ```
>       sudo -u postgres psql
>       ```
>   - In the postgres session create database, user and add permissions:
>       ```
>       CREATE DATABASE classroom_ge;
>       CREATE USER example_archili WITH PASSWORD example_archilis_password;
>       ALTER ROLE example_archili SET client_encoding TO 'utf8';
>       ALTER ROLE example_archili SET default_transaction_isolation TO 'read committed';
>       ALTER ROLE example_archili SET timezone TO 'UTC';
>       GRANT ALL PRIVILEGES ON DATABASE classroom_ge TO example_archili;
>       ```
>   - Quit postgress session
>       ```
>       \q
>       ```
> - Change these lines in the project settings file (classroom_ge/settings.py):
>
>       DATABASES = {
>           'default': {
>               'ENGINE': 'django.db.backends.postgresql',
>               'NAME': 'classroom_ge',
>               'USER': DATABASE_PARAMS['USER'],
>               'PASSWORD': DATABASE_PARAMS['PASSWORD'],
>               'HOST': DATABASE_PARAMS['HOST'],
>               'PORT': DATABASE_PARAMS['PORT'],
>           }
>       }
>
> - Add file 'my_constants.py' in classroom_ge (same folder, where settings.py is located) and add following script:
>
>       DATABASE_PARAMS = {
>           'USER': 'example_archili',
>           'PASSWORD': 'example_archilis_password',
>           'PORT': 5432,
>           'HOST': 'localhost',
>       }
>
> After these, 'python manage.py runserver' should work!


## Routine
### Basic
1) Activate virtual environment
    ```
    source venv/bin/activate
    ```
2) Run server
    ```
    python classroom_ge/manage.py runserver
    ```


### Update texts
1) Define translation texts:
    ```
    {% trans "this_is_the_identifier_for_translation_text" %}
    ```
2) Generate instances in translation files (BASE_DIR/localce/)
    ```
    python3 classroom_ge/manage.py makemessages -all --ignore venv
    ```
3) Update texts in .po translation files: BASE_DIR/locale/{language}/LC_MESSAGES/django.po
4) Compile translations to apply changes:
    ```
    python3 classroom_ge/manage.py compilemessages
    ```

### On model updates:
- General:
    ```
    python classroom_ge/manage.py makemigrations
    python classroom_ge/manage.py showmigrations
    python classroom_ge/manage.py migrate
    ```
- Fake zero: https://simpleisbetterthancomplex.com/tutorial/2016/07/26/how-to-reset-migrations.html



## Some Links
- Postgres
    - https://docs.djangoproject.com/en/4.2/ref/databases/#postgresql-notes
    - https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-22-04
    - https://www.postgresql.org/docs/current/indexes-opclass.html
    - https://www.digitalocean.com/community/tutorials/how-to-move-a-postgresql-data-directory-to-a-new-location-on-ubuntu-16-04
- Translation
    - https://docs.djangoproject.com/en/4.2/topics/i18n/translation/
    - https://testdriven.io/blog/multiple-languages-in-django/


