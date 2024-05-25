from django.core.management.base import BaseCommand
from django.db.models import Q
from course.models.session import Session
from course.helper import process_helper
import subprocess
import logging
logger = logging.getLogger("reportLog")

class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        session_obj = Session.objects.filter(~Q(status=Session.STATUS_COMPELETED)).order_by('-created_at')[:1]

        if session_obj:
            session = session_obj[0]
            if not process_helper.is_process_active(session.pid):
                p = subprocess.Popen(['python', 'manage.py', f'start_session -i {session.trainer_id} -s {session.trainee_id} -ses {session.id} -m {session.mode} -r 1'])
                session.pid(p.pid)
                session.save()



