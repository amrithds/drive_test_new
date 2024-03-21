from django.db import models
from utils.model_util.base_model import BaseModel

class Course(BaseModel):
    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length=1024)

    def __str__(self) -> str:
        return self.name