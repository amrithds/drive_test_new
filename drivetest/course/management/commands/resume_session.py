from django.core.management.base import BaseCommand
from django.db.models import Q
from course.models.session import Session
import logging
logger = logging.getLogger("reportLog")

class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        session = Session.objects.filter(~Q(status=Session.STATUS_COMPELETED)).order_by('-created_at')

        if 