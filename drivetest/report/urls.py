from django.urls import path, include
from rest_framework import routers
from report import views

router = routers.DefaultRouter()
router.register(r'finalReport', views.FinalReportViewSet)

urlpatterns = [
    path('live_report/', views.live_report, name='live_report'),
    path('', include(router.urls)),
]