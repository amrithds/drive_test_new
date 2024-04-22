from django.db import models
from .task import Task
from utils.model_util.base_model import BaseModel

class TaskMetrics(BaseModel):
    id = models.AutoField(primary_key = True)
    value = models.CharField(max_length=1024)
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE)
    message = models.CharField(max_length=1024, default='')
    created_at = models.DateField()
    updated_at = models.DateField()

    
