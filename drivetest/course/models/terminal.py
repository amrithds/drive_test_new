from django.db import models
from utils.model_util.base_model import BaseModel

class Terminal(BaseModel):
    id = models.AutoField(primary_key = True)
    vehicle_no = models.CharField(max_length=100,unique=True)
    center_name=models.CharField(max_length=100,unique=True)
    program_name=models.CharField(max_length=255,unique=True)
    vehicle_type=models.CharField(max_length=100,unique=True)
    ip_address=models.IPAddressField()
    bluetooth_speaker=models.CharField(max_length=100,unique=True)
    def __str__(self) -> str:
        return self.vehicle_no