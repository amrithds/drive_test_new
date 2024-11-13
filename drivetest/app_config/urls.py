from django.urls import path, include
from rest_framework import routers
from app_config import views

router = routers.DefaultRouter()
router.register(r'config', views.ConfigViewSet)

urlpatterns = [
    path('update_system_time/', views.updateSystemTime,name='update_system_time'),
    path('', include(router.urls)),
]