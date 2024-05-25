from django.contrib import admin
from report.models.session_report import SessionReport

# Register your models here.
    
class SessionReportAdmin(admin.ModelAdmin):
    list_display = ['obstacle', 'task', 'result','remark']

admin.site.register(SessionReport, SessionReportAdmin)