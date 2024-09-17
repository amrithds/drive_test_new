import django
django.setup()
from course.models.obstacle_task_score import ObstacleTaskScore
from course.models.obstacle_session_tracker import ObstacleSessionTracker
from report.models.session_report import SessionReport
from report.helper.report_helper import get_obstacle_duration
from django.core.cache import cache

def live_report():
    """
        json format
        ["tasks": [{name: <task_name> , status: 1, remarks: '', total_marks: 0, obtained_marks:0}
        , {name: <task_name_2> , status: 2, remarks: '', total_marks: 0, obtained_marks:0 ]
        "tasks": [{name: <task_name> , status: 1, remarks: '', total_marks: 0, obtained_marks:0}]
        ]
    """
    while True:
        obs_session_trackers = ObstacleSessionTracker.objects.all()

        
        data = []
        for obs_session_tracker in obs_session_trackers:

            session_reports = SessionReport.objects.filter(obstacle_id=obs_session_tracker.obstacle_id)
            
            obstacle_report = {"tasks": [], "status": obs_session_tracker.status, "result": ObstacleSessionTracker.RESULT_PASS\
                                ,"total_marks": 0, "obtained_marks": 0}
            
            for session_report in session_reports:
                task_score_obj = ObstacleTaskScore.objects.get(obstacle_id=session_report.obstacle_id\
                                                            ,task_id=session_report.task_id)
                task_report = {"name": session_report.task.name, "score" : 0,"result": session_report.result, "remark": session_report.remark}

                
                if obs_session_tracker.status != ObstacleSessionTracker.STATUS_IN_PROGRESS:
                    #if mandatory task fails then whole obstacle result is marked as fail
                    if session_report.result == SessionReport.RESULT_FAIL and task_score_obj.is_mandatory:
                        obstacle_report["result"] = SessionReport.RESULT_FAIL
                    elif session_report.result == SessionReport.RESULT_PASS:
                        task_report["score"] = task_score_obj.score
                        obstacle_report["obtained_marks"] += task_score_obj.score
                
                # avoid displaying failed result when task is in progress
                elif session_report.result == SessionReport.RESULT_FAIL:
                    task_report["result"] = SessionReport.RESULT_UNKNOWN
                
                
                obstacle_report["total_marks"] += task_score_obj.score

                obstacle_report["tasks"].append(task_report)

            obstacle_report["obstacle_duration"] = get_obstacle_duration(obs_session_tracker.obstacle_id)
            obstacle_report["name"] = obs_session_tracker.obstacle.name
            obstacle_report["id"] = obs_session_tracker.obstacle_id
            data.append(obstacle_report)
        
        cache.set('LIVE_REPORT', data)
