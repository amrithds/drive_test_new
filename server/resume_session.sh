#!/bin/bash


cd /home/admin/driving_project
source venv/bin/activate
cd drivetest
python manage.py resume_session
