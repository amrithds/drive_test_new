import django
django.setup()

from course.helper.report_generator import ReportGenerator
from course.models.session import Session
import logging

report_logger = logging.getLogger("reportLog")

def report_generator(session: Session, resume: int=0):
    #initialise session report
    try:
        report_generotor = ReportGenerator(session, resume)
        report_generotor.generateReport()
    except Exception as e:
        report_logger.exception("Error: "+str(e))



