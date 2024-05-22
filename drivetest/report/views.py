from django.shortcuts import render
from report.models.session_report import SessionReport
from course.models.obstacle_session_tracker import ObstacleSessionTracker
from course.models.obstacle_task_score import ObstacleTaskScore
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
import json
from django.core import serializers
# Create your views here.

# @login_required
def live_report(request):
    obs_session_trackers = ObstacleSessionTracker.objects.all()

    data = {}
    for obs_session_tracker in obs_session_trackers:

        session_reports = SessionReport.objects.filter(obstacle_id=obs_session_tracker.obstacle_id)
        
        
        obstacle_report = {"tasks": [], "status": SessionReport.RESULT_UNKNOWN\
                            ,"total_marks": 0, "obtained_marks": 0}
        
        for session_report in session_reports:
            task_score_obj = ObstacleTaskScore.objects.get(obstacle_id=session_report.obstacle_id\
                                                           ,task_id=session_report.task_id)
            task_report = {"name": session_report.task.name, "score" : 0,"result": session_report.result, "remark": session_report.remark}

            #if mandatory task fails then whole obstacle result is marked as fail
            if session_report.result == SessionReport.RESULT_FAIL and task_score_obj.is_mandatory:
                obstacle_report["status"] = SessionReport.RESULT_FAIL
            elif session_report.result == SessionReport.RESULT_PASS:
                task_report["score"] = task_score_obj.score
                obstacle_report["obtained_marks"] += task_score_obj.score
                obstacle_report["status"] = SessionReport.RESULT_PASS
            
            obstacle_report["total_marks"] += task_score_obj.score

            obstacle_report["tasks"].append(task_report)
        #mark fail if all task were failed in a obstacle
        if obstacle_report["status"] == SessionReport.RESULT_UNKNOWN:
            obstacle_report["status"] = SessionReport.RESULT_FAIL
        
        obstacle_report["obstacle_name"] = obs_session_tracker.obstacle.name
        data[obs_session_tracker.obstacle_id] = obstacle_report

    # {"start": "tasks": [{name: , status, remarks, marks}, ]}
    return HttpResponse(json.dumps(data), status=200)