from django.db import models
from course.models.obstacle import Obstacle
from course.models.task import Task
from utils.model_util.base_model import BaseModel

class SessionReport(BaseModel):
    RESULT_UNKNOWN = 0
    RESULT_PASS = 1
    RESULT_FAIL = 2

    RESULTS = ('Unknown', 'Pass', 'Fail')

    obstacle = models.ForeignKey(Obstacle, on_delete=models.DO_NOTHING)
    task = models.ForeignKey(Task, on_delete=models.DO_NOTHING)
    result = models.IntegerField(choices=(
            (RESULT_UNKNOWN , "Unknown"),
            (RESULT_PASS , "Pass"),
            (RESULT_FAIL , "Fail")
    ), default = RESULT_UNKNOWN)
    remark = models.CharField(max_length=100, default='')

    class Meta:
        db_table = "report_session_report"
    