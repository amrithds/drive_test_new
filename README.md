# create virtual env
python -m venv venv
source venv/bin/activate

# os requirements
sudo apt-get update

sudo apt-get upgrade

sudo apt-get install apache2

sudo apt-get install python-pip python-virtualenv python-setuptools python-dev build-essential

sudo apt-get install libapache2-mod-wsgi-py3
sudo apt-get install python3-dev default-libmysqlclient-dev
apt install python3-gst-1.0
pip install -r requirement.txt

# Install packages using 
pip install <package> && pip freeze > requirements.txt

https://stackoverflow.com/questions/15793990/django-how-to-set-foreign-key-checks-to-0

# Application setup
python manage.py migrate
python manage.py createsuperuser 

# install angular and django side by side
# report ApI
# Bulk report api
# Test

# Installation steps

python manage.py migrate authtoken


# case when user was already created 
from course.models.user import User
from rest_framework.authtoken.models import Token

for user in User.objects.all():
    Token.objects.get_or_create(user=user)

# Reference
https://gist.github.com/Kyle-Koivukangas/9f6627b03c2d80ecb4b4f722ea26da35

https://blog.renu.ac.ug/index.php/2023/11/11/deploying-django-application-with-gunicorn-apache-and-mysql-on-ubuntu-server/
# angular
https://faun.pub/deploy-angular-app-to-apache-server-b7d87dab96df
python manage.py start_session -i 7 -s 6 -ses 16 -m 1


# App configs
bluetooth speaker
vehicle number
