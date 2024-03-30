from django.db import models
from .course import Course
from .training import Training
class SensorFeed(models.Model):
    id = models.AutoField(primary_key = True)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, default=None)
    training = models.ForeignKey(Training, on_delete=models.DO_NOTHING, default=None)
    s1 = models.IntegerField(max_length=2)
    s2 = models.IntegerField(max_length=2)
    s3 = models.IntegerField(max_length=2)
    s4 = models.IntegerField(max_length=2)
    s5 = models.IntegerField(max_length=2)
    s6 = models.IntegerField(max_length=2)
    s7 = models.IntegerField(max_length=2)
    s8 = models.IntegerField(max_length=2)
    s9 = models.IntegerField(max_length=2)
    s10 = models.IntegerField(max_length=2)
    s11 = models.IntegerField(max_length=2)
    s12 = models.IntegerField(max_length=2)
    s13 = models.IntegerField(max_length=2)
    s14 = models.IntegerField(max_length=2)
    s15 = models.IntegerField(max_length=2)
    s16 = models.IntegerField(max_length=2)
    s17 = models.IntegerField(max_length=2)
    s18 = models.IntegerField(max_length=2)
    s19 = models.IntegerField(max_length=2)
    device_time = models.DateTimeField(default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    