from rest_framework import viewsets
from app_config.models import Config
from rest_framework.permissions import IsAuthenticated
from app_config.serializers import ConfigSerializer
from rest_framework.decorators import api_view
import subprocess
from django.http import HttpResponse
# Create your views here.
class ConfigViewSet(viewsets.ModelViewSet):
    queryset = Config.objects.all().order_by('-created_at')
    serializer_class = ConfigSerializer
    permission_classes = [IsAuthenticated]

def updateSystemTime(request):
    client_system_time = request.GET['system_time']
    if client_system_time:
        command = f"sudo date -s '{client_system_time}'"
        subprocess.Popen(command, shell=True)
    data = {'success': True}
    return HttpResponse(data, content_type='application/json')
    