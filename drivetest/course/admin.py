from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from course.models import Course , Obstacle , Task , TaskMetric, Track, \
    ObstacleTaskScore, User, Session, ObstacleSessionTracker
# Register your models here.
    
class UserAdmin(UserAdmin):
    fieldsets = ((None, {'fields': ('username', 'password')}), ('Personal info', {'fields': ('name', 'unique_ref_id','rank', 'course', 'type')}), ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}), ('Important dates', {'fields': ('last_login', 'date_joined')}))
    list_display = ['id', 'name', 'unique_ref_id','rank', 'course', 'type']

class CourseAdmin(admin.ModelAdmin):
    list_display = ["name"]

class ObstableAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', "track_id", 'is_mandatory', 'order', 'start_rf_id', 'end_rf_id', 'audio_file']

class SessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'trainer_no','trainee_no', 'status', 'mode' ]

class TaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'sensor_id', 'category' ]

class TaskMetricAdmin(admin.ModelAdmin):
    ordering = ['-task', 'success_value']
    list_display = [ 'task','success_value', 'failure_value','left_min_range', "left_max_range", 'right_min_range', "right_max_range", "distance", 'success_message', 'failure_message' ]

class ObstacleTaskScoreAdmin(admin.ModelAdmin):
    ordering = ['obstacle', 'task_metrics', 'score']
    list_display = ['obstacle', 'task_metrics', 'score', 'is_mandatory', 'description' ]

class ObstacleSessionTrackerAdmin(admin.ModelAdmin):
    list_display = ['obstacle', 'session', 'status', 'report_status' ]

admin.site.register(User,UserAdmin)
admin.site.register(Course,CourseAdmin)
admin.site.register(Obstacle,ObstableAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskMetric, TaskMetricAdmin)
admin.site.register(ObstacleTaskScore, ObstacleTaskScoreAdmin)
admin.site.register(ObstacleSessionTracker, ObstacleSessionTrackerAdmin)

admin.site.register([ Track])

