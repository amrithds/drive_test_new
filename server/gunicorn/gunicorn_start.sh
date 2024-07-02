#!/bin/bash
#This is the Gunicorn script used to automatically launch the application through Gunicorn
NAME="Drivetest"

#path to the folder containing the manage.py file

DIR=/home/admin/driving_project


# Replace with your system user
USER=admin  
# Replace with your system group
GROUP=admin

WORKERS=1

#bind to port 8000
BIND=0.0.0.0:8000

# Put your project name
DJANGO_SETTINGS_MODULE=admin.settings 
DJANGO_WSGI_MODULE=admin.wsgi


LOG_LEVEL=debug
HOME_DIR="$(dirname $0)/../.."
echo $HOME_DIR
echo "fff"
# cd $HOME_DIR
LOG_FILE=/home/admin/driving_project/drivetest/log/gunicorn.log

#activating the virtual environment
source $HOME_DIR/venv/bin/activate

export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE

export PYTHONPATH=$DIR:$PYTHONPATH

exec gunicorn admin.wsgi:application --bind=$BIND --user=$USER --log-file=$LOG_FILE --name $NAME --workers $WORKERS --user=$USER --group=$GROUP --log-level=$LOG_LEVEL --log-file=$LOG_FILE

