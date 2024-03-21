from django.db import models
from utils.model_util.base_model import BaseModel
from .obstacle import Obstacle
from .task import Task

class ObstacleTaskScore(BaseModel):
    id = models.AutoField(primary_key = True)
    obstacle_id = models.ForeignKey(Obstacle, on_delete=models.CASCADE)
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE)
    name = models.CharField(max_length=100,unique=True)
    score= models.IntegerField(default=0)
    is_mandatory = models.BooleanField(default=False)
    description = models.CharField(max_length=100)
    order = models.IntegerField()


