from .models import User
from .models import Course
from .models import Obstacle
from .serializers import UserSerializer
from .serializers import CourseSerializer
from .serializers import SessionSerializer
from .serializers import ObstacleSerializer
from rest_framework import viewsets
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from course.models.session import Session
from django.http import JsonResponse 
import subprocess
import shlex
from course.helper import process_helper
from course.helper.start_session_helper import createSession
from course.helper.report_generator import ReportGenerator
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.contrib.auth import logout
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from app_config.models import Config
from django.db.models import Exists, OuterRef
from report.models import FinalReport
from rest_framework.decorators import api_view, permission_classes
import json
import logging
logger = logging.getLogger("default")
from course.shared_state import terminate_process
from course.models import ObstacleSessionTracker
from django.db.models import Q

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserSerializer
    authentication_classes = [ TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def create(self, request):
        #request.data._mutable=True
        post_data = request.data
        user_driver_str = str(User.DRIVER)
        if post_data['type'] == user_driver_str or User.DRIVER:
            course_name = post_data.get('course')
            if course_name:
                course, _ = Course.objects.get_or_create(name=course_name)
                post_data['course'] = course.id
        else:
            post_data['course'] = None
        request._full_data = post_data
        return super().create(request)
    
    def destroy(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        # you custom logic #
        return super(UserViewSet, self).destroy(request, pk, *args, **kwargs)

    def get_queryset(self):
        """
        """
        queryset = User.objects.filter(is_superuser=False).exclude(username='admin')
        course_name = self.request.query_params.get('course_id', None)
        search_id = self.request.query_params.get('search_id', None)
        user_type = self.request.query_params.get('type', None)
        course = None
        if course_name is not None and course_name != '':
            course_name = course_name.strip()
            course = Course.objects.get(name=course_name)
        if search_id is not None:
            #ilike serial_no or unique_ref_id
            queryset = queryset.filter(Q(unique_ref_id__contains=search_id) | Q(serial_no__contains=search_id))
        if user_type is not None:
            queryset = queryset.filter(type=user_type)
        if course is not None:
            queryset = queryset.filter(course_id=course.id)
        
        return queryset

class UserLogIn(ObtainAuthToken):
    """Token based login

    Args:
        ObtainAuthToken (_type_): _description_
    """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token = Token.objects.get(user=user)
        
        return HttpResponse(json.dumps({
            'token': token.key,
            'id': user.pk,
            'username': user.username
        }), content_type='application/json')

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by('-created_at')
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

class ObstacleViewSet(viewsets.ModelViewSet):
    queryset = Obstacle.objects.all().order_by('created_at')
    serializer_class = ObstacleSerializer
    permission_classes = [IsAuthenticated]

class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all().order_by('-created_at')
    serializer_class = SessionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['trainer', 'trainee', 'status', 'mode']

    def get_queryset(self):
        """filter sessions using search field
        search can be serial_no or unique_ref_id

        Returns:
            queryset: 
        """
        queryset = super(SessionViewSet, self).get_queryset()

        search = self.request.query_params.get('search', None)
        if search:
            #if search is string then don't search serial_no(throws error)
            if search.isdigit():
                filter = Q(trainee__unique_ref_id = search) | Q(trainee__serial_no= search)
            else:
                filter = Q(trainee__unique_ref_id = search)
            
            queryset = queryset.filter(filter)

        # Filter sessions that have a related FinalReport
        queryset = queryset.annotate(
            has_final_report=Exists(FinalReport.objects.filter(session=OuterRef('pk')))
        ).filter(has_final_report=True)

        queryset = queryset.select_related('trainee')
        return queryset

@api_view(['GET'])
def user_login(request):
    print('here')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        print('here',password, username)
        if username and password:
            # Test username/password combination
            user = authenticate(username=username, password=password)
            # Found a match
            if user is not None:
                # User is active
                if user.is_active:
                    # Officially log the user in
                    login(request, user)
                    
                    user_data = {'name': user.name}
                    data = {'success': True, 'user': json.dumps(user_data)}
                else:
                    data = {'success': False, 'error': 'User is not active'}
            else:
                data = {'success': False, 'error': 'Wrong username and/or password'}

            return HttpResponse(json.dumps(data), content_type='application/json')

    # Request method is not POST or one of username or password is missing
    return HttpResponseBadRequest() 

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def start_session(request):
    try:
        course_id = request.GET['course_id']
        trainer_id = request.GET['trainer_id']
        trainee_id = request.GET['trainee_id']
        mode = request.GET['mode']
        
        with open('output.txt', 'w', encoding='utf-8') as f:
            pass

        #close pending sessions
        pending_sessions = Session.objects.filter(status=Session.STATUS_IN_PROGRESS)
        for pending_session in pending_sessions:
            __terminate_session(pending_session)
        
        sessionObj = createSession(trainer_id, trainee_id, mode, course_id)
        command = shlex.split(f'python manage.py start_session -i {trainer_id} -s {trainee_id} -ses {sessionObj.id} -m {mode}')
        p = subprocess.Popen(command)
        #p = subprocess.Popen(['python', 'manage.py', f'test'])
        sessionObj.pid = p.pid
        sessionObj.save()
        return JsonResponse({'session_id': sessionObj.id}, status=200)
    except Exception as e:
        logger.exception(e)
        return JsonResponse({'message': str(e)}, status=500)
    
@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def stop_session(request):
    try:
        with open('output.txt', 'w', encoding='utf-8') as f:
            pass
        session_id = request.GET['session_id']
        sessionObj = Session.objects.get(id=session_id)

        #close pending obstacle sessions
        pending_obstacle_sessions = ObstacleSessionTracker.objects.filter(session=sessionObj, status=ObstacleSessionTracker.STATUS_IN_PROGRESS)
        for pending_obstacle_session in pending_obstacle_sessions:
            pending_obstacle_session.status = ObstacleSessionTracker.STATUS_COMPLETED
            pending_obstacle_session.save()

        report_gen = ReportGenerator(sessionObj)
        
        logger = logging.getLogger("reportLog")
        logger.info(session_id)
        
        report_gen.generateFinalReport()
            
        __terminate_session(sessionObj)
        return JsonResponse({'session_id': sessionObj.id}, status=200)
    except Exception as e:
        logger.exception(e)
        return JsonResponse({'message': str(e)}, status=500)

def __terminate_session(sessionObj: Session):
    import os
    os.system("pkill -9 -f 'manage.py start_session'")

    sessionObj.status = Session.STATUS_COMPELETED
    sessionObj.save()

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def session_in_progress(request):
    # session_obj = Session.objects.filter(status=Session.STATUS_IN_PROGRESS)[:1]
    session_obj = Session.objects.filter(status=Session.STATUS_IN_PROGRESS).first()
    if session_obj:
        serializer = SessionSerializer(session_obj, context={'request': request})
        return JsonResponse(serializer.data, status=200)
    else:
        return JsonResponse({}, status=200)
    
@login_required
def index(request):
    return render(request,'index/index.html')

def test(request):
    from playsound import playsound
    from django.conf import settings
    AUDIO_LOCATION = str(settings.MEDIA_ROOT)+'/uploads/2.mp3'
    try:
        playsound(AUDIO_LOCATION)
    except Exception as e:
        logger.exception(e)
    return JsonResponse({'error': 'Some error'}, status=200)

# @api_view(['GET'])
# @permission_classes((IsAuthenticated, ))
# def user_logout(request):
#     logout(request)
#     data = {'success': True}
#     return HttpResponse(json.dumps(data), content_type='application/json')
