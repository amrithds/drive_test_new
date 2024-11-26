from django.db import models
from utils.model_util.base_model import BaseModel

class Task(BaseModel):
    TASK_TYPE_BOOLEAN = 0
    TASK_TYPE_PARKING = 1
    TASK_TYPE_LEFT_PARKING = 4
    TASK_TYPE_RIGHT_PARKING = 5
    TASK_TYPE_REVERSE_PARKING = 9
    TASK_TYPE_SPEED = 2
    TASK_TYPE_DUAL_SENSOR_TURNING = 3
    TASK_TYPE_LEFT_TURNING = 6
    TASK_TYPE_RIGHT_TURNING = 7
    TASK_TYPE_DUAL_SENSOR_TURNING_ZIG_ZAG = 8
    TASK_TYPE_FIGURE_OF_EIGHT = 10
    TASK_TYPE_BOOLEAN_ALL_SUCCESS = 11
    TASK_TYPE_PARKING_NEW = 12 # left/right and reverse sensor

    BOOLEAN_TASKS = (TASK_TYPE_BOOLEAN, TASK_TYPE_BOOLEAN_ALL_SUCCESS)
    PARKING_TYPES = (TASK_TYPE_PARKING, TASK_TYPE_LEFT_PARKING, TASK_TYPE_RIGHT_PARKING,TASK_TYPE_REVERSE_PARKING, TASK_TYPE_PARKING_NEW)
    TURNING_TYPES = (TASK_TYPE_DUAL_SENSOR_TURNING, TASK_TYPE_LEFT_TURNING, TASK_TYPE_RIGHT_TURNING, TASK_TYPE_DUAL_SENSOR_TURNING_ZIG_ZAG\
                     , TASK_TYPE_FIGURE_OF_EIGHT)
    
    

    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length=100,unique=True)
    sensor_id=models.CharField(max_length=100)
    category=models.IntegerField(choices=(
            (TASK_TYPE_BOOLEAN , "Boolean"),
            (TASK_TYPE_BOOLEAN_ALL_SUCCESS, "Boolean (All Success)"),
            (TASK_TYPE_PARKING , "Parking (Old)"),
            (TASK_TYPE_PARKING_NEW, "Parking (New)"),
            (TASK_TYPE_LEFT_PARKING , "Left Parking"),
            (TASK_TYPE_RIGHT_PARKING , "Right Parking"),
            (TASK_TYPE_REVERSE_PARKING , "Reverse Parking"),
            (TASK_TYPE_SPEED , "Speed"),
            (TASK_TYPE_DUAL_SENSOR_TURNING , "Turning"),
            (TASK_TYPE_LEFT_TURNING , "Left Turning"),
            (TASK_TYPE_RIGHT_TURNING , "Right Turning"),
            (TASK_TYPE_DUAL_SENSOR_TURNING_ZIG_ZAG , "Zig-zag Turning"),
            (TASK_TYPE_FIGURE_OF_EIGHT, "Figure of 8")
    ), default= 0)

    def __str__(self) -> str:
        return self.name