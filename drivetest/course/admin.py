from django.contrib import admin
from course.models import Course , Obstacle , Task , TaskMetrics, Track, \
    ObstacleTaskScore, User, Session

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'name','unique_ref_id', "type"]

class CourseAdmin(admin.ModelAdmin):
    list_display = ["name"]

class ObstableAdmin(admin.ModelAdmin):
    list_display = ['id', "track_id", 'is_mandatory', 'order', 'start_rf_id', 'end_rf_id', 'audio_file']

class SessionAdmin(admin.ModelAdmin):
    list_display = ['id', "trainer_id", 'trainee_id', 'status', 'mode', ]

admin.site.register(User,UserAdmin)
admin.site.register(Course,CourseAdmin)
admin.site.register(Obstacle,ObstableAdmin)
#admin.site.register(SessionAdmin,Session)
admin.site.register([ Task , TaskMetrics,Track, ObstacleTaskScore, Session])

