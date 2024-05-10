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

def createSession(trainerID, traineeID, session_mode, course_name):
    #create session object
    trainer = User.objects.get(id=trainerID)
    trainee = User.objects.get(id=traineeID)
    courseObj = Course.objects.get(name=course_name)
    #update session with in progress status
    sessionObj = Session.objects.create(trainer_no=trainer, trainee_no=trainee, mode=session_mode\
                                        , course=courseObj, status=Session.STATUS_IN_PROGRESS)
    return sessionObj
