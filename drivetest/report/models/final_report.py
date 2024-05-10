from django.db import models
from course.models.obstacle import Obstacle
from course.models.task import Task
from utils.model_util.base_model import BaseModel

class FinalReport(BaseModel):
    obstacle = models.ForeignKey(Obstacle, on_delete=models.DO_NOTHING)
    data = models.JSONField(default=None)
