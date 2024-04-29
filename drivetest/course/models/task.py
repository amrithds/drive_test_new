from django.db import models
from utils.model_util.base_model import BaseModel

class Task(BaseModel):
    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length=100,unique=True)
    sensor_id=models.IntegerField()
    category=models.IntegerField(choices=(
            (0 , "Boolean"),
            (1 , "Parking"),
            (2 , "Speed"),
            (3 , "Turning")
    ), default= 0)

    def __str__(self) -> str:
        return self.name