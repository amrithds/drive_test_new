from django.db import models
from .obstacle import Obstacle
class SensorFeed(models.Model):
    Obstacle = models.ForeignKey(Obstacle, on_delete=models.DO_NOTHING, default=None)
    s1 = models.CharField(max_length=10)
    s2 = models.CharField(max_length=10)
    s3 = models.CharField(max_length=10)
    s4 = models.CharField(max_length=10)
    s5 = models.CharField(max_length=10)
    s6 = models.CharField(max_length=10)
    s7 = models.CharField(max_length=10)
    s8 = models.CharField(max_length=10)
    s9 = models.CharField(max_length=10)
    s10 = models.CharField(max_length=10)
    s11 = models.CharField(max_length=10)
    s12 = models.CharField(max_length=10)
    s13 = models.CharField(max_length=10)
    s14 = models.CharField(max_length=10)
    s15 = models.CharField(max_length=10)
    s16 = models.CharField(max_length=10)
    s17 = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    