from django.db import models
from utils.model_util.base_model import BaseModel

class Task(BaseModel):
    TASK_TYPE_BOOLEAN = 0
    TASK_TYPE_PARKING = 1
    TASK_TYPE_LEFT_PARKING = 4
    TASK_TYPE_RIGHT_PARKING = 5
    TASK_TYPE_SPEED = 2
    TASK_TYPE_DUAL_SENSOR_TURNING = 3
    TASK_TYPE_LEFT_TURNING = 6
    TASK_TYPE_RIGHT_TURNING = 7
    
    

    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length=100,unique=True)
    sensor_id=models.CharField(max_length=100)
    category=models.IntegerField(choices=(
            (0 , "Boolean"),
            (1 , "Parking"),
            (2 , "Speed"),
            (3 , "Turning"),
            (4 , "Left Parking"),
            (5 , "Right Parking"),
    ), default= 0)

    def __str__(self) -> str:
        return self.name