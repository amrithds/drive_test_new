from django.db import models
from .track import Track
from utils.model_util.base_model import BaseModel

class Obstacle(BaseModel):
    id = models.AutoField(primary_key = True)
    track_id = models.ForeignKey(Track, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_mandatory = models.BooleanField(default=False)
    order = models.IntegerField()
    start_device_id = models.CharField(max_length=20, blank=False)
    end_device_id = models.CharField(max_length=20, blank=True)
    audio_file= models.CharField(max_length=100)


