from django.db import models
from .obstacle import Obstacle
class SensorFeed(models.Model):
    LEFT_DISTANCE_SENSOR = 's1'
    RIGHT_DISTANCE_SENSOR = 's1'
    
    obstacle = models.ForeignKey(Obstacle, on_delete=models.DO_NOTHING, default=None)
    s0 = models.IntegerField(blank=True, null=True)
    s1 = models.IntegerField(blank=True, null=True)
    s2 = models.IntegerField(blank=True, null=True)
    s3 = models.IntegerField(blank=True, null=True)
    s4 = models.IntegerField(blank=True, null=True)
    s5 = models.IntegerField(blank=True, null=True)
    s6 = models.IntegerField(blank=True, null=True)
    s7 = models.IntegerField(blank=True, null=True)
    s8 = models.IntegerField(blank=True, null=True)
    s9 = models.IntegerField(blank=True, null=True)
    s10 = models.IntegerField(blank=True, null=True)
    s11 = models.IntegerField(blank=True, null=True)
    s12 = models.IntegerField(blank=True, null=True)
    s13 = models.IntegerField(blank=True, null=True)
    s14 = models.IntegerField(blank=True, null=True)
    s15 = models.IntegerField(blank=True, null=True)
    s16 = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "course_sensor_feed"