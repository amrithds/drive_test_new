from course.models.obstacle_session_tracker import ObstacleSessionTracker
from singleton_decorator import singleton
from course.models.obstacle_task_score import ObstacleTaskScore
from course.models.obstacle import Obstacle
from report.models.session_report import SessionReport
from course.models.session import Session
from report.models.final_report import FinalReport 
from course.models.task import Task
from course.models.sensor_feed import SensorFeed
from django.db.models import Q
import datetime
import logging
logger = logging.getLogger("reportLog")
@singleton
class ReportGenerator():
    def __init__(self, session: Session) -> None:
        """init
        Args:
            session (Session): session object
        """
        self.session = session
       
    def generateReport(self):
        """
        Generate report from session data feed
        """
        self.__initializeSessionReport()
        while True:
            OSTrackers = ObstacleSessionTracker.objects.filter(session = self.session\
                        , report_status = ObstacleSessionTracker.STATUS_IN_PROGRESS)
            
            for OSTracker in OSTrackers:
                #SessionReport
                sessionTaskReports = SessionReport.objects.filter(obstacle_id=OSTracker.obstacle_id)
                
                for sessionTaskReport in sessionTaskReports:
                    ObsTaskScore = ObstacleTaskScore.objects.get(obstacle_id=sessionTaskReport.obstacle_id\
                                                      , task_id=sessionTaskReport.task_id)
                    
                    result = self.__getResult(ObsTaskScore)
                    
                    
                    if result is True:
                        sessionTaskReport.result = SessionReport.RESULT_PASS
                    else:
                        sessionTaskReport.result = SessionReport.RESULT_FAIL
                    sessionTaskReport.remark = ObsTaskScore.success_task_metrics.message
                    sessionTaskReport.save()
    
    @classmethod 
    def generateFinalReport(self):
        """
        Generate final report from session data feed
        """
        obstacles = Obstacle.objects.all()

        for obstacle in obstacles:
            final_report = FinalReport.objects.create(obstacle=obstacle, )
            session_task_reports = SessionReport.objects.filter(obstacle_id=obstacle.obstacle_id)




    def __initializeSessionReport(self):
        """
        init all obstacle and task entry in report SessionReport
        """
        OTScores = ObstacleTaskScore.objects.all()
        
        for OTScore in OTScores:
            SessionReport.objects.create(obstacle_id=OTScore.obstacle_id, task_id=OTScore.task_id)
    
    def __getResult(self, ObsTaskScore: ObstacleTaskScore) -> bool:
        """Gets task result in each obstacle based on Success task metrics

        Args:
            ObsTaskScore (ObstacleTaskScore): Obj

        Returns:
            bool: result (True : pass, False : Fail)
        """
        task_category = ObsTaskScore.task.category
        result = False
        if task_category == Task.TASK_TYPE_BOOLEAN:
            result = self.__booleanTasksResult(ObsTaskScore)
        elif task_category == Task.TASK_TYPE_PARKING:
            result = self.__parkingTasksResult(ObsTaskScore, )
        elif task_category == Task.TASK_TYPE_SPEED:
            result = self.__speedResult()
        elif task_category == Task.TASK_TYPE_TURNING:
            result = self.__turningTasksResult()

        return result
        
    def __parkingTasksResult(self, ObsTaskScore:ObstacleTaskScore):
        left_range = ObsTaskScore.success_task_metrics.range_1
        right_range = ObsTaskScore.success_task_metrics.range_2
        sensor_ids = ObsTaskScore.task.sensor_id.split(",")
        left_sensor_id = sensor_ids[0]
        right_sensor_id = sensor_ids[1]
        filter_query = Q(**{"%s__lt" % left_sensor_id: left_range, "%s__lt" % right_sensor_id: right_range,\
                             "obstacle_id": ObsTaskScore.obstacle_id })
        return not SensorFeed.objects.filter(filter_query).exists()
    
    def __speedResult(self, ObsTaskScore:ObstacleTaskScore):
        """Check if speed is in limit

        Args:
            ObsTaskScore (ObstacleTaskScore): _description_

        Returns:
            _type_: _description_
        """
        filter_query = Q(**{"obstacle_id": ObsTaskScore.obstacle_id })
        last_date = SensorFeed.objects.filter(filter_query).order_by('-created_at').first()
        first_date = SensorFeed.objects.filter(filter_query).order_by('created_at').first()
        average_distance = ObsTaskScore.success_task_metrics.distance
        speed_limit = ObsTaskScore.success_task_metrics.value
        #date format from db
        datetime_format = '%Y-%m-%dT%H:%M:%S.%f'
        #speed = distance / time taken
        last_date_timestamp = datetime.datetime.strptime(last_date, datetime_format)
        first_date_timestamp = datetime.datetime.strptime(first_date, datetime_format)
        diff = last_date_timestamp - first_date_timestamp
        speed = average_distance/diff.seconds
        
        result = None
        if speed < speed_limit:
            result = True
        else:
            result = False

        return result

    def __turningTasksResult(self, ObsTaskScore:ObstacleTaskScore):
        left_range = ObsTaskScore.success_task_metrics.range_1
        right_range = ObsTaskScore.success_task_metrics.range_2
        sensor_ids = ObsTaskScore.task.sensor_id.split(",")
        left_sensor_id = sensor_ids[0]
        right_sensor_id = sensor_ids[1]
        filter_query = Q(**{"%s__lt" % left_sensor_id: left_range, "%s__lt" % right_sensor_id: right_range,\
                             "obstacle_id": ObsTaskScore.obstacle_id })
        return not SensorFeed.objects.filter(filter_query).exists()

    def __booleanTasksResult(self, ObsTaskScore:ObstacleTaskScore) -> bool:
        success_value = ObsTaskScore.success_task_metrics.value
        sensor_id = ObsTaskScore.task.sensor_id
        filter_query = Q(**{"%s" % sensor_id: success_value, "obstacle_id": ObsTaskScore.obstacle_id })
        return SensorFeed.objects.filter(filter_query).exists()
        