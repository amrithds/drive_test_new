from course.models.session import Session
from course.models.obstacle import Obstacle
from course.models.sensor_feed import SensorFeed
from course.models.user import User

def initialiseSession(self, trainerID, traineeID, session_mode ):
    trainer = User.objects.get(id=trainerID)
    trainee = User.objects.get(id=traineeID)
    #update session with in progress status
    sessionObj = Session.objects.create(trainer_no=trainer, trainee_no=trainee, mode=session_mode, status=Session.STATUS_IN_PROGRESS)
    #clear sensor table
    SensorFeed.objects.all().delete()
    return sessionObj