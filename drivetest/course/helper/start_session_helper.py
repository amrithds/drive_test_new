from course.models.session import Session
from course.models.obstacle_session_tracker import ObstacleSessionTracker
from course.models.sensor_feed import SensorFeed
from course.models.user import User
from course.models.course import Course
from report.models.session_report import SessionReport

def initialiseSession():
    #clear sensor table
    SensorFeed.objects.all().delete()
    #clear obstacle session tracker
    ObstacleSessionTracker.objects.all().delete()
    #session report
    SessionReport.objects.all().delete()

def createSession(trainer_id, trainee_id, session_mode, course_name, p_id = None):
    #create session object
    trainer = User.objects.get(id=trainer_id)
    trainee = User.objects.get(id=trainee_id)
    courseObj = Course.objects.get(name=course_name)

    #update session with in progress status
    sessionObj = Session.objects.create(trainer=trainer, trainee=trainee, mode=session_mode\
                                        , course=courseObj, status=Session.STATUS_IN_PROGRESS)
    print(sessionObj)
    if p_id:
        sessionObj.pid = p_id
        sessionObj.save()
    return sessionObj
