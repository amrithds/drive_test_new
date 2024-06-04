from django.urls import path, include
from rest_framework import routers
from course import views

router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet)
router.register(r'course', views.CourseViewSet)
router.register(r'obstacle', views.ObstacleViewSet)
router.register(r'session', views.SessionViewSet)

urlpatterns = [
    # path('logout/', views.user_logout, name='course_logout'),
    path('login/', views.UserLogIn.as_view(), name='course_login'),
    path('start_session/', views.start_session, name='start_session'),
    path('stop_session/', views.stop_session, name='stop_session'),
    path('current_session/', views.session_in_progress, name='current_session'),
    path('test/', views.test,name='test'),
    path('', include(router.urls)),
]