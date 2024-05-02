from django.db import models
from course.models.obstacle import Obstacle
from course.models.session import Session
from utils.model_util.base_model import BaseModel

class SessionReport(BaseModel):
    obstacle = models.ForeignKey(Obstacle, on_delete=models.DO_NOTHING)
    