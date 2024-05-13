from .models import User
from .models import Course
from .serializers import UserSerializer
from .serializers import CourseSerializer
from rest_framework import viewsets
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models.session import Session
from django.http import JsonResponse 
import subprocess
import psutil
from course.helper.start_session_helper import createSession
from course.helper.report_generator import ReportGenerator
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
    import subprocess
    subprocess.Popen(['python', 'manage.py', 'test'])
    #a = call_command(f'test &')
    from django.http import JsonResponse 
    return JsonResponse({'error': 'Some error'}, status=200)

@login_required
def start_session(request):
    course_id = request.GET['courseId']
    trainer_id = request.GET['trainerId']
    trainee_id = request.GET['traineeId']
    mode = request.GET['mode']

    sessionObj = createSession( trainer_id, trainee_id, mode, course_id)
    p = subprocess.Popen(['python', 'manage.py', f'start_session -i {trainer_id} -s {trainee_id} -ses {sessionObj.id} -m {mode}'])
    sessionObj.pid = p.id
    sessionObj.save()

    return JsonResponse({'session_id': sessionObj.id}, status=200)

@login_required
def stop_session(request):
    try:
        session_id = request.GET['session_id']
        sessionObj = Session.objects.get(id=session_id)
        ReportGenerator.generateFinalReport()
        p = psutil.Process(sessionObj.pid)
        p.terminate()

        return JsonResponse({'session_id': sessionObj.id}, status=200)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=500)


