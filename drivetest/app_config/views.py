from rest_framework import viewsets
from app_config.models import Config
from rest_framework.permissions import IsAuthenticated
from app_config.serializers import ConfigSerializer
# Create your views here.
class ConfigViewSet(viewsets.ModelViewSet):
    queryset = Config.objects.all().order_by('-created_at')
    serializer_class = ConfigSerializer
    permission_classes = [IsAuthenticated]