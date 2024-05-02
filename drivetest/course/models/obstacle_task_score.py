from django.db import models
from utils.model_util.base_model import BaseModel
from .obstacle import Obstacle
from .task import Task
from .task_metrics import TaskMetrics

class ObstacleTaskScore(BaseModel):
    id = models.AutoField(primary_key = True)
    obstacle_id = models.ForeignKey(Obstacle, on_delete=models.DO_NOTHING)
    success_task_metrics = models.ForeignKey(TaskMetrics, on_delete=models.DO_NOTHING, default=None)
    score= models.IntegerField(default=0)
    is_mandatory = models.BooleanField(default=False)
    description = models.CharField(max_length=100, blank=True, default='')


