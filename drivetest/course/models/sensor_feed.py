from django.db import models
from .course import Course
from .training import Training
class SensorFeed(models.Model):
    id = models.AutoField(primary_key = True)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, default=None)
    training = models.ForeignKey(Training, on_delete=models.DO_NOTHING, default=None)
    s1 = models.IntegerField()
    s2 = models.IntegerField()
    s3 = models.IntegerField()
    s4 = models.IntegerField()
    s5 = models.IntegerField()
    s6 = models.IntegerField()
    s7 = models.IntegerField()
    s8 = models.IntegerField()
    s9 = models.IntegerField()
    s10 = models.IntegerField()
    s11 = models.IntegerField()
    s12 = models.IntegerField()
    s13 = models.IntegerField()
    s14 = models.IntegerField()
    s15 = models.IntegerField()
    s16 = models.IntegerField()
    s17 = models.IntegerField()
    s18 = models.IntegerField()
    s19 = models.IntegerField()
    device_time = models.DateTimeField(default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    