from .models import User
from .models import Course
from .serializers import UserSerializer
from .serializers import CourseSerializer
from rest_framework import viewsets
from django.shortcuts import render
from django.core.management import call_command
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models.session import Session
#from rest_framework.response import Response
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
        course_name = (self.request.query_params.get('course_id', None)).strip()
        unique_ref_id = self.request.query_params.get('unique_ref_id', None)
        user_type = self.request.query_params.get('type', None)
        course = None
        if course_name is not None and course_name != '':
            course = Course.objects.get(name=course_name)
        if unique_ref_id is not None:
            #ilike
            queryset = queryset.filter(Q(unique_ref_id__contains=unique_ref_id))
        if user_type is not None:
            queryset = queryset.filter(type=user_type)
        if course is not None:
            queryset = queryset.filter(course_id=course.id)
        print(queryset.query, unique_ref_id)
        return queryset
        

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by('-created_at')
    serializer_class = CourseSerializer

@login_required
def index(request):
    return render(request,'index/index.html')

def test(request):
    return render(request,'test.html')

def start_session(request):
    courseId = request.GET['courseId']
    trainerId = request.GET['trainerId']
    traineeId = request.GET['traineeId']
    mode = request.GET['mode']

    # #out = StringIO()
    # #sys.stdout = out
    course = Course.objects.get(name=courseId)
    trainer = User.objects.get(id=trainerId)
    trainee = User.objects.get(id=traineeId)
    sessionObj,_ = Session.objects.get_or_create(trainee_no=trainee,trainer_no=trainer, course=course, 
                                                 mode=mode, status=Session.STATUS_IDEAL
                                                 )
    call_command(f'start_session -i {trainerId} -s {traineeId} -ses {sessionObj.id} -m {mode}')
