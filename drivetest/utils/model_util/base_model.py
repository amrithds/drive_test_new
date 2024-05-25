from django.db import models
from .custom_date_time import DateTimeWithoutTZField as DateTimeField
class BaseModel(models.Model):
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True