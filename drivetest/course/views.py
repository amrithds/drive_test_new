from .models import User
from .models import Course
from .serializers import UserSerializer
from .serializers import CourseSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import render
from django.core.management import call_command
import sys
#from django.utils.six import StringIO
# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserSerializer

    def create(self, request):
        request.data._mutable=True
        post_data = request.data
        course_name = post_data['course']
        course,_ = Course.objects.get_or_create(name=course_name)
        request.data['course'] = course.id
        return super().create(request)
    
    def destroy(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        # you custom logic #
        return super(UserViewSet, self).destroy(request, pk, *args, **kwargs)

    def get_queryset(self):
        """
        """
        queryset = User.objects.all()
        course_name = self.request.query_params.get('course_id', None)
        unique_ref_id = self.request.query_params.get('unique_ref_id', None)
        user_type = self.request.query_params.get('type', None)
        course = None
        if course_name is not None:
            course = Course.objects.get(name=course_name)
        if unique_ref_id is not None:
            queryset = queryset.filter(unique_ref_id=unique_ref_id)
        if user_type is not None:
            queryset = queryset.filter(type=user_type)
        if course is not None:
            queryset = queryset.filter(course_id=course.id)
        return queryset
        

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by('-created_at')
    serializer_class = CourseSerializer


def index(request):
    return render(request,'index.html')

def start_session(request):
    courseId = request.GET['courseId']
    trainerId = request.GET['trainerId']
    traineeId = request.GET['traineeId']

    #out = StringIO()
    #sys.stdout = out
    call_command('start_session', trainerId, traineeId, courseId)
