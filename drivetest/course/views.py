from .models import User
from .models import Course
from .models import Obstacle
from .serializers import UserSerializer
from .serializers import CourseSerializer
from .serializers import SessionSerializer
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
from rest_framework.decorators import api_view, permission_classes
import json
import logging
logger = logging.getLogger("default")

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserSerializer
    authentication_classes = [ TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
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
        print(queryset.query, search_id)
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
    serializer_class = CourseSerializer
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
        queryset = queryset.select_related('trainee')
        return queryset

@api_view(['GET'])
def user_login(request):
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
        
        sessionObj = createSession( trainer_id, trainee_id, mode, course_id)
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
        session_id = request.GET['session_id']
        sessionObj = Session.objects.get(id=session_id)
        report_gen = ReportGenerator(sessionObj)
        report_gen.generateFinalReport()
        
        process_helper.stop_process(sessionObj.pid)

        sessionObj.status = Session.STATUS_COMPELETED
        sessionObj.save()

        return JsonResponse({'session_id': sessionObj.id}, status=200)
    except Exception as e:
        logger.exception(e)
        return JsonResponse({'message': str(e)}, status=500)

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def session_in_progress(request):
    session_obj = Session.objects.filter(status=Session.STATUS_IN_PROGRESS)[:1]
    if session_obj:
        return JsonResponse(session_obj[0].serialize(), status=200)
    else:
        return JsonResponse({}, status=200)
    
@login_required
def index(request):
    return render(request,'index/index.html')

def test(request):
    import subprocess
    subprocess.Popen(['python', 'manage.py', 'test'])
    #a = call_command(f'test &')
    from django.http import JsonResponse 
    return JsonResponse({'error': 'Some error'}, status=200)

# @api_view(['GET'])
# @permission_classes((IsAuthenticated, ))
# def user_logout(request):
#     logout(request)
#     data = {'success': True}
#     return HttpResponse(json.dumps(data), content_type='application/json')