from django.core.management.base import BaseCommand, CommandError
import logging
logger = logging.getLogger("reportLog")

class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        while True:
            logger.info('Inside')
            import time
            time.sleep(1)
