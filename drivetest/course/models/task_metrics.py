from django.db import models
from .task import Task
from utils.model_util.base_model import BaseModel

class TaskMetric(BaseModel):
    id = models.AutoField(primary_key = True)
    value = models.CharField(max_length=1024, default=None, blank=True)
    range_1 = models.CharField(max_length=100, default=None, blank=True)
    range_2 = models.CharField(max_length=100, default=None, blank=True)
    distance = models.CharField(max_length=100, default=None, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    message = models.CharField(max_length=1024, default='')

    class Meta:
        db_table = "course_task_metric"
    
    def __str__(self) -> str:
        return f"{self.task} {self.value}"
