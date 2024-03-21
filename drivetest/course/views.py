from .models import User
from .models import Course
from .serializers import UserSerializer
from .serializers import CourseSerializer
from rest_framework import permissions, viewsets
from django.shortcuts import render

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserSerializer

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by('-created_at')
    serializer_class = CourseSerializer
    #permission_classes = [permissions.IsAuthenticated]

def index(request):
    return render(request,'index.html')