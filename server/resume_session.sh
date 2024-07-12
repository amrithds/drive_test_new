#!/bin/bash

echo "Last reboot time:" >> /home/admin/log.log

cd /home/admin/driving_project
source venv/bin/activate
cd drivetest
python manage.py resume_session
