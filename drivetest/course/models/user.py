from django.db import models
from course.models import Course
from utils.model_util.base_model import BaseModel

class User(BaseModel):
    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length=100)
    unique_ref_id=models.CharField(max_length=100)
    course_id=models.ForeignKey(Course, on_delete=models.CASCADE)
    rank=models.CharField(max_length=50)
    unit=models.CharField(max_length=50)
    type=models.IntegerField(max_length=1, choices=(
            (1, "Driver"),
            (2, "Instructor")
        ))

    class Meta:
        unique_together = ('course_id', 'unique_ref_id')


    