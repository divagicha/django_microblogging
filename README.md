## Sample Usage

### Steps to follow:
1. `cd` into your project directory
2. clone this git repo using command
   ```shell
   git clone https://github.com/divagicha/django_microblogging.git .
   ```
3. create a virtual environment using your preferred python module and activate the virtual environment
4. start postgresql and redis using command 
   ```shell
   docker-compose up -d
   ```
5. run following commands (as is) in order (press `Enter` after each command)
   ```shell
   docker exec -it postgresql bash
   psql -U dbuser
   CREATE DATABASE microblog;
   ALTER ROLE dbuser SET client_encoding TO 'utf8';
   ALTER ROLE dbuser SET default_transaction_isolation TO 'read committed';
   ALTER ROLE dbuser SET timezone TO 'UTC';
   exit
   exit
   ```
5. generate and run django app migrations using command
   ```shell
   python manage.py makemigrations && python manage.py migrate
   ```
6. run command
   ```shell
   pip install -r requirements.txt
   ```
7. create superuser using command
   ```shell
   python manage.py createsuperuser
   ```
8. start django server using command
   ```shell
   python manage.py runserver
   ```
9. user superuser credentials to log in to the admin panel `http://localhost:8000/admin/`
10. navigate to the following link in your browser `http://localhost:8000/docs/`
