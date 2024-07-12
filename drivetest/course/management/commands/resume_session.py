from django.core.management.base import BaseCommand
from django.db.models import Q
from course.models.session import Session
from course.helper import process_helper
import shlex
import subprocess
import logging
import time

logger = logging.getLogger("reportLog")
class Command(BaseCommand):
    help = "Resumes the session with the specified criteria"

    def handle(self, *args, **options):
        while True:
            logger.info("Resuming session")
            session = Session.objects.filter(~Q(status=Session.STATUS_COMPELETED)).order_by('-created_at').first()
            if session:
                if not process_helper.is_process_active(session.pid):
                    command = shlex.split(f'python manage.py start_session -i {session.trainer_id} -s {session.trainee_id} -ses {session.id} -m {session.mode} -r 1')
                    p = subprocess.Popen(command)
                    session.pid = p.pid
                    session.save()
            time.sleep(10)



