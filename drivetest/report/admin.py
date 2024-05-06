from django.contrib import admin
from report.models import SessionReport

# Register your models here.
    
class SessionReportAdmin(admin.ModelAdmin):
    list_display = ['obstacle', 'task', 'result','remark']

admin.site.register(SessionReport, SessionReportAdmin)