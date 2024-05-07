from django.db import models
from course.models.obstacle import Obstacle
from course.models.session import Session
from utils.model_util.base_model import BaseModel

class ObstacleSessionTracker(BaseModel):
    
    STATUS_IN_PROGRESS = 0
    STATUS_COMPLETED = 1

    obstacle = models.ForeignKey(Obstacle, on_delete=models.DO_NOTHING)
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING)
    status = models.IntegerField(choices=(
            (STATUS_IN_PROGRESS , "In Progres"),
            (STATUS_COMPLETED , "Completed")
    ), default= STATUS_IN_PROGRESS)
    report_status = models.IntegerField(choices=(
            (STATUS_IN_PROGRESS , "In Progres"),
            (STATUS_COMPLETED , "Completed")
    ), default= STATUS_IN_PROGRESS)

    class Meta:
        db_table = "course_obstacle_session_tracker"
    def __str__(self) -> str:
        return f"{self.session} {self.obstacle}"
    