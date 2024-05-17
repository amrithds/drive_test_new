from django.urls import path, include
from rest_framework import routers
from course import views

router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet)
router.register(r'course', views.CourseViewSet)

urlpatterns = [
    path('start_session/', views.start_session, name='start_session'),
    path('stop_session/', views.stop_session, name='stop_session'),
    path('test/', views.test,name='test'),
    path('', include(router.urls)),
]