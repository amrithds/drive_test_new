from django.urls import path, include
from report import views

urlpatterns = [
    path('live_report/', views.live_report, name='live_report'),
]