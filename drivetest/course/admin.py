from django.contrib import admin
from course.models import Course , Obstacle , Task , TaskMetrics, SensorFeed, Track, ObstacleTaskScore

# Register your models here.
admin.site.register([Course,Obstacle, Task , TaskMetrics,Track, ObstacleTaskScore, SensorFeed])