from django.db import models
from .track import Track
from utils.model_util.base_model import BaseModel

class Obstacle(BaseModel):
    id = models.AutoField(primary_key = True)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_mandatory = models.BooleanField(default=False)
    order = models.IntegerField()
    start_rf_id = models.CharField(max_length=20, blank=False)
    end_rf_id = models.CharField(max_length=20, blank=True)
    audio_file= models.FileField(upload_to ='uploads/', blank=True)

    def __str__(self) -> str:
        return f"{self.name}"


