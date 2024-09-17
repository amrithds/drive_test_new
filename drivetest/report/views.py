from django.shortcuts import render
from report.models.session_report import SessionReport
from report.models.final_report import FinalReport
from course.models.obstacle_session_tracker import ObstacleSessionTracker
from course.models.session import Session
from course.models.obstacle_task_score import ObstacleTaskScore
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import json
from report.serializers import FinalReportSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from report.helper.report_helper import get_obstacle_duration
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from django.utils.timezone import make_aware
from django.utils import timezone
from django.db.models import Max
from django.core.cache import cache
# Create your views here.

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def live_report(request):
    """live summary of test

    Args:
        request (Request):

    Returns:
        _type_: _description_
        
    json format
        ["tasks": [{name: <task_name> , status: 1, remarks: '', total_marks: 0, obtained_marks:0}
        , {name: <task_name_2> , status: 2, remarks: '', total_marks: 0, obtained_marks:0 ]
        "tasks": [{name: <task_name> , status: 1, remarks: '', total_marks: 0, obtained_marks:0}]
        ]
    """
    data = cache.get('LIVE_REPORT', {})

    return HttpResponse(json.dumps(data), status=200)
class FinalReportViewSet(viewsets.ModelViewSet):
    queryset = FinalReport.objects.order_by('id')
    serializer_class = FinalReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        request = self.request

        course_id = request.query_params.get('course_id', None)
        from_date = request.query_params.get('from_date', None)
        to_date = request.query_params.get('to_date', None)
        session = request.query_params.get('session',None)

        if session:
            queryset = queryset.filter(session__id=session)

        if course_id:
            queryset = queryset.filter(session__course__id=course_id)
        

        if course_id and from_date and to_date:
            # Convert from_date and to_date to datetime objects
            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()

            # Define start_datetime and end_datetime for the range filter
            start_datetime = datetime.combine(from_date_obj, datetime.min.time()).replace(tzinfo=timezone.utc)
            end_datetime = datetime.combine(to_date_obj, datetime.max.time()).replace(tzinfo=timezone.utc)


            latest_sessions = Session.objects.filter(
                course_id=course_id,
                created_at__range=(start_datetime, end_datetime),
            ).values('trainee_id').annotate(
                max_created_at=Max('created_at')
            )

            # Build a list of session IDs for the latest sessions
            session_ids = []
            for session in latest_sessions:
                trainee_id = session['trainee_id']
                max_created_at = session['max_created_at']
                session_id = Session.objects.filter(
                    trainee_id=trainee_id,
                    created_at=max_created_at
                ).values_list('id', flat=True).first()
                if session_id:
                    session_ids.append(session_id)
           
            queryset = queryset.filter(session_id__in=session_ids)
            
        return queryset
