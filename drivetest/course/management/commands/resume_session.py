from django.core.management.base import BaseCommand
from django.db.models import Q
from course.models.session import Session
from course.helper import process_helper
import logging
logger = logging.getLogger("reportLog")

class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        session_obj = Session.objects.filter(~Q(status=Session.STATUS_COMPELETED)).order_by('-created_at')[:1]

        for session in session_obj:
            if not process_helper.is_process_active(session.pid):
                



