from django.contrib import admin
from app_config.models import Config

# Register your models here.
class ConfigAdmin(admin.ModelAdmin):
    list_display = ["name", "value"]

admin.site.register(Config,ConfigAdmin)