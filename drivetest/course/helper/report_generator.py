from course.models.obstacle_session_tracker import ObstacleSessionTracker
from singleton_decorator import singleton
from course.models.obstacle_task_score import ObstacleTaskScore
from report.models.session_report import SessionReport
from course.models.session import Session
from course.models.task import Task
from course.models.sensor_feed import SensorFeed
from django.db.models import Q
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
                sessionTaskReports = SessionReport.objects.filter(obstacle_id=OSTracker.obstacle_id\
                                                            , result=SessionReport.RESULT_UNKNOWN)
                
                for sessionTaskReport in sessionTaskReports:
                    ObsTaskScore = ObstacleTaskScore.objects.filter(obstacle_id=sessionTaskReport.obstacle_id\
                                                      , task_id=sessionTaskReport.task_id).first()
                    
                    result = self.__getResult(ObsTaskScore)
                    
                    if result is True:
                        sessionTaskReport.result = SessionReport.RESULT_PASS
                        sessionTaskReport.remark = ObsTaskScore.success_task_metrics.message
                        sessionTaskReport.save()


    def __initializeSessionReport(self):
        OTScores = ObstacleTaskScore.objects.all()
        #init all obstacle and task entry in report SessionReport
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
            successValue = ObsTaskScore.success_task_metrics.value
            sensor_id = ObsTaskScore.task.sensor_id
            result = self.__booleanTasksResult(ObsTaskScore.obstacle_id, sensor_id, successValue)
        elif task_category == Task.TASK_TYPE_PARKING:
            result = self.__parkingTasksResult()
        elif task_category == Task.TASK_TYPE_SPEED:
            result = self.__speedResult()
        elif task_category == Task.TASK_TYPE_TURNING:
            result = self.__turningTasksResult()

        return result
        
    def __parkingTasksResult(leftSensor, rightSensor):
        
        pass
    
    def __speedResult():
        pass

    def __turningTasksResult(leftSensor, rightSensor):
        pass

    def __booleanTasksResult(self, obs_id, sensor_id, sensorValue) -> bool:
        filter_query = Q(**{"%s" % sensor_id: sensorValue, "obstacle_id": obs_id })
        return SensorFeed.objects.filter(filter_query).exists()
        