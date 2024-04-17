from django.db import models
from course.models import Course
from utils.model_util.base_model import BaseModel

class User(BaseModel):
    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length=100)
    unique_ref_id=models.CharField(max_length=100)
    course=models.ForeignKey(Course, on_delete=models.CASCADE)
    rank=models.CharField(max_length=50, choices=(
            ("Rect" , "Rect"),
            ("SEP" , "SEP"),
            ("L Nk" , "L Nk"),
            ("Nk" , "Nk"),
            ("L Hav" , "L Hav"),
            ("Hav" , "Hav"),
            ("Nb Sub" , "Nb Sub"),
            ("Sub" , "Sub"),
            ("Sub Maj" , "Sub Maj"),
            ("Lt" , "Lt"),
            ("Maj" , "Maj"),
            ("Capt" , "Capt"),
            ("Lt Col" , "Lt Col"),
        )
    )
    unit=models.CharField(max_length=50)
    type=models.IntegerField(choices=(
            (1, "Driver"),
            (2, "Instructor")
        ), default=1)

    class Meta:
        unique_together = ('course', 'unique_ref_id')
    
    def __str__(self) -> str:
        return self.name