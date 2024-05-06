from course.models.obstacle_session_tracker import ObstacleSessionTracker
from singleton_decorator import singleton
from course.models.obstacle_task_score import ObstacleTaskScore
from report.models.session_report import SessionReport
from course.models.session import Session
from course.models.task import Task
from course.models.sensor_feed import SensorFeed
@singleton
class ReportGenerator():
    def __init__(self, session: Session) -> None:
        self.session = session
        #init all obstacle and task entry in report SessionReport
        self.__initializeSessionReport()
        
            
    def generateReport(self):
        """
        Generate report from session data feed
        """
        while True:
            OSTrackers = ObstacleSessionTracker.objects.filter(session = self.session\
                        , status = ObstacleSessionTracker.STATUS_IN_PROGRESS)\
                         .values()
            
            for OSTracker in OSTrackers:
                #SessionReport
                ObsTaskScores = ObstacleTaskScore.objects.get(obstacle_id=ObstacleSessionTracker.obstacle_id\
                                                      , task_id=ObstacleSessionTracker.task_id)
                for ObsTaskScore in ObsTaskScores:
                    task = ObsTaskScore.task

                    result = self.__getResult(task)

    def __initializeSessionReport(self):
        OTScores = ObstacleTaskScore.objects.all()
        
        for OTScore in OTScores:
            SessionReport.objects.create(obstacle_id=OTScore.obstacle_id, task_id=OTScore.task_id)
    
    def __getResult(self, task: Task) -> bool:
        taskType = task.type
        result = False
        if taskType == Task.TASK_TYPE_BOOLEAN:
            result = self.__booleanTasksResult()
        elif taskType == Task.TASK_TYPE_PARKING:
            result = self.__parkingTasksResult()
        elif taskType == Task.TASK_TYPE_SPEED:
            result = self.__speedResult()
        elif taskType == Task.TASK_TYPE_TURNING:
            result = self.__turningTasksResult()

        return result
        
    def __parkingTasksResult(leftSensor, rightSensor):
        
        pass
    
    def __speedResult():
        pass

    def __turningTasksResult(leftSensor, rightSensor):
        pass

    def __booleanTasksResult(sesorValue):
        pass