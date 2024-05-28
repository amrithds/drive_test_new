from django.db import models
from course.models.obstacle import Obstacle
from course.models.session import Session
from course.models.task import Task
from utils.model_util.base_model import BaseModel

class FinalReport(BaseModel):
    RESULT_PASS = 1
    RESULT_FAIL = 2
    
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING)
    obstacle = models.ForeignKey(Obstacle, on_delete=models.DO_NOTHING)
    data = models.JSONField(default=None)
    total_score = models.IntegerField(default=0, null=True, blank=True)
    obtained_score = models.IntegerField(default=0, null=True, blank=True)
    result = models.IntegerField(choices=(
            (RESULT_PASS , "Pass"),
            (RESULT_FAIL , "Fail")
    ), default = RESULT_PASS)
    obstacle_duration = models.IntegerField(default=0, null=True, blank=True)

    class Meta:
        db_table = "report_final_report"
