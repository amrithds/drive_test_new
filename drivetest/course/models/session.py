from django.db import models
from utils.model_util.base_model import BaseModel
from .user import User
from .course import Course

class Session(BaseModel):
    STATUS_IDEAL = 0
    STATUS_IN_PROGRESS = 1
    STATUS_COMPELETED = 2

    MODE_EVALUATE = 0
    MODE_TRAINING = 1

    MODE_CHOICES=(
        (MODE_EVALUATE, "Evaluate"),
        (MODE_TRAINING, "Training")
    )

    id=models.AutoField(primary_key = True)
    trainer = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='trainer_session_set')
    trainee = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='trainee_session_set')
    status=models.IntegerField(choices=(
            (0, "Ideal"),
            (1, "In progress"),
            (2, "Completed"),
        ), default=0)
    mode=models.IntegerField(choices=MODE_CHOICES, default=0)
    course=models.ForeignKey(Course, on_delete=models.DO_NOTHING, default=None)
    pid = models.IntegerField(default=None, null=True)

    def __str__(self) -> str:
        return f"{self.id} {self.course} {self.trainer} {self.trainee}"
    
    def serialize(self):
        return {
            "id": self.id,
            "trainer": self.trainer,
            "trainee": self.trainee,
            "status": self.status,
            "mode" : self.mode,
            "course": self.course,
            "pid" : self.pid
        }