from django.db import models
from .task import Task
from utils.model_util.base_model import BaseModel

class TaskMetric(BaseModel):
    id = models.AutoField(primary_key = True)
    success_value = models.IntegerField(blank=True, null=True)
    failure_value = models.IntegerField(default=0, blank=True, null=True)
    left_min_range = models.IntegerField(blank=True, null=True)
    left_max_range = models.IntegerField(blank=True, null=True)
    right_min_range = models.IntegerField(blank=True, null=True)
    right_max_range = models.IntegerField(blank=True, null=True)
    back_min_range = models.IntegerField(blank=True, null=True)
    back_max_range = models.IntegerField(blank=True, null=True)
    distance = models.IntegerField( blank=True, null=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    success_message = models.CharField(max_length=1024, default='')
    failure_message = models.CharField(max_length=1024, default='')

    class Meta:
        db_table = "course_task_metric"
    
    def __str__(self) -> str:
        return f"{self.task} : {self.success_value} - {self.failure_value}"
