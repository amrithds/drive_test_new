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
from course.helper import process_helper
from course.helper.start_session_helper import createSession
from course.helper.report_generator import ReportGenerator
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
import json
import logging
logger = logging.getLogger("default")

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
        

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by('-created_at')
    serializer_class = CourseSerializer

@require_http_methods(["POST"])
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
                    from django.forms.models import model_to_dict
                    user_data = {'name': user.name}
                    data = {'success': True, 'user': user_data}
                else:
                    data = {'success': False, 'error': 'User is not active'}
            else:
                data = {'success': False, 'error': 'Wrong username and/or password'}

            return HttpResponse(json.dumps(data), content_type='application/json')

    # Request method is not POST or one of username or password is missing
    return HttpResponseBadRequest() 

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
    try:
        course_id = request.GET['courseId']
        trainer_id = request.GET['trainerId']
        trainee_id = request.GET['traineeId']
        mode = request.GET['mode']

        #p = subprocess.Popen(['python', 'manage.py', f'start_session -i {trainer_id} -s {trainee_id} -ses {sessionObj.id} -m {mode}'])
        p = subprocess.Popen(['python', 'manage.py', f'test'])
        sessionObj = createSession( trainer_id, trainee_id, mode, course_id, p.pid)

        return JsonResponse({'session_id': sessionObj.id}, status=200)
    except Exception as e:
        logger.exception(e)
        return JsonResponse({'message': str(e)}, status=500)

@login_required
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


