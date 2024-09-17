from django.db import models
from .user import User
from .course import Course
from utils.model_util.base_model import BaseModel

class Training(BaseModel):
    id = models.AutoField(primary_key = True)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING)
    trainer = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='trainer_user_set')
    trainee = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='trinee_user_set')

    def __str__(self) -> str:
        return self.name