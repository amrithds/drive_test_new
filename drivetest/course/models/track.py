from django.db import models
from utils.model_util.base_model import BaseModel

class Track(BaseModel):
    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length=100,unique=True)

    def __str__(self) -> str:
        return self.name