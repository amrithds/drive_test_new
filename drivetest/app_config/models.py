from django.db import models
from utils.model_util.base_model import BaseModel

class Config(BaseModel):
    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length=1024)
    value = models.CharField(max_length=1024)

    def __str__(self) -> str:
        return self.name