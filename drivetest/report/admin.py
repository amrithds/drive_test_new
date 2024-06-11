from django.contrib import admin
from report.models.session_report import SessionReport
from report.models.sensor_feed import SensorFeed

# Register your models here.
    
class SessionReportAdmin(admin.ModelAdmin):
    list_display = ['obstacle', 'task', 'result','remark']

class SensorFeedAdmin(admin.ModelAdmin):
    list_display = ['obstacle', 's0', 's1','s2','s3', 's4','s5','s6', 's7','s8','s9', 's10','s11','s12', 's13','s14','s15', 's16']

admin.site.register(SessionReport, SessionReportAdmin)
admin.site.register(SensorFeed, SensorFeedAdmin)