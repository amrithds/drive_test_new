from django.db import models
from course.models.obstacle import Obstacle
from course.models.task import Task
from utils.model_util.base_model import BaseModel

class FinalReport(BaseModel):
    RESULT_PASS = 1
    RESULT_FAIL = 2

    obstacle = models.ForeignKey(Obstacle, on_delete=models.DO_NOTHING)
    data = models.JSONField(default=None)
    score = models.IntegerField(default=0)
    result = models.IntegerField(choices=(
            (RESULT_PASS , "Pass"),
            (RESULT_FAIL , "Fail")
    ), default = RESULT_PASS)
