from course.models.session import Session
from course.models.obstacle import Obstacle
from course.models.sensor_feed import SensorFeed
from course.models.user import User
from course.models.course import Course

def initialiseSession(trainerID, traineeID, session_mode, course_name):
    trainer = User.objects.get(id=trainerID)
    trainee = User.objects.get(id=traineeID)
    courseObj = Course.objects.get(name=course_name)
    #update session with in progress status
    sessionObj = Session.objects.create(trainer_no=trainer, trainee_no=trainee, mode=session_mode\
                                        , course=courseObj, status=Session.STATUS_IN_PROGRESS)
    #clear sensor table
    SensorFeed.objects.all().delete()
    return sessionObj