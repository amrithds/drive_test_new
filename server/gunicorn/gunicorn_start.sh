#!/bin/bash
#This is the Gunicorn script used to automatically launch the application through Gunicorn
NAME="Drive test"

#path to the folder containing the manage.py file
DIR=/home/super/Desktop/app/drive_test/drivetest

# Replace with your system user
USER=root  
# Replace with your system group
GROUP=root

WORKERS=1

#bind to port 8000
BIND=0.0.0.0:8000

# Put your project name
DJANGO_SETTINGS_MODULE=admin.settings 
DJANGO_WSGI_MODULE=admin.wsgi

LOG_LEVEL=debug

cd $DIR

#activating the virtual environment
source /home/super/Desktop/app/drive_test/venv/bin/activate

export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE

export PYTHONPATH=$DIR:$PYTHONPATH

exec gunicorn ${DJANGO_WSGI_MODULE}:application \

  --name $NAME \

  --workers $WORKERS \

  --user=$USER \

  --group=$GROUP \

  --bind=$BIND \

  --log-level=$LOG_LEVEL \

  --log-file=-