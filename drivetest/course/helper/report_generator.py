from course.models.obstacle_session_tracker import ObstacleSessionTracker
from singleton_decorator import singleton
from course.models.obstacle_task_score import ObstacleTaskScore
from course.models.obstacle import Obstacle
from report.models.session_report import SessionReport
from course.models.session import Session
from course.models.task_metrics import TaskMetric
from report.models.final_report import FinalReport 
from course.models.task import Task
from course.models.sensor_feed import SensorFeed
from django.db.models import Min, Q, Max
from operator import or_
import datetime
import logging

logger = logging.getLogger("reportLog")

@singleton
class ReportGenerator():
    DISTANCE_SENSOR_LEFT_ONLY = 0
    DISTANCE_SENSOR_RIGHT_ONLY = 1
    DISTANCE_SENSOR_LEFT_RIGHT = 2

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
                    
                    logger.info(ObsTaskScore.task.name )
                    logger.info(result )
                    if result is True:
                        print('result', result, ObsTaskScore.obstacle, ObsTaskScore.task)
                        sessionTaskReport.result = SessionReport.RESULT_PASS
                        sessionTaskReport.remark = ObsTaskScore.task_metrics.success_message
                    else:
                        # if sessionTaskReport.task.name == "Seat Belt" and sessionTaskReport.result == SessionReport.RESULT_PASS:
                        #     print(result, sessionTaskReport, ObsTaskScore)
                        sessionTaskReport.result = SessionReport.RESULT_FAIL
                        sessionTaskReport.remark = ObsTaskScore.task_metrics.failure_message
                    sessionTaskReport.save()

                #when task is complted then stop generating report 
                if OSTracker.status == ObstacleSessionTracker.STATUS_COMPLETED:
                    OSTracker.report_status = ObstacleSessionTracker.STATUS_COMPLETED
                    OSTracker.save()
    
    @classmethod 
    def generateFinalReport(cls):
        """
        Generate final report from session data feed
        """
        obstacles = Obstacle.objects.all()

        for obstacle in obstacles:
            final_report = FinalReport.objects.create(obstacle=obstacle, data={})
            session_task_reports = SessionReport.objects.filter(obstacle_id=obstacle.obstacle_id).order_by('obstacle_id', 'task_id')
            #init obstacle level report
            data = []
            total_obs_score = 0
            for session_task_report in session_task_reports:
                task_report_json = {"task":session_task_report.task.name, "result" : SessionReport.RESULTS[session_task_report.result]\
                               , "score": 0 }
                
                obs_task_score = ObstacleTaskScore.objects.get(obstacle_id=session_task_report.obstacle_id\
                                                               , task_id=session_task_report.task_id)
                
                if session_task_report.result == SessionReport.RESULT_PASS:
                    task_report_json.score = obs_task_score.score
                    total_obs_score += obs_task_score.score
                else:
                    if obs_task_score.is_mandatory:
                        final_report.result = FinalReport.RESULT_FAIL
                        final_report.save()

                data.append(task_report_json)
            
            final_report.score = total_obs_score
            final_report.data = data
            final_report.save()



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
        elif task_category in Task.PARKING_TYPES:
            result = self.__parkingTasksResult(ObsTaskScore )
        elif task_category == Task.TASK_TYPE_SPEED:
            result = self.__speedResult()
        elif task_category in Task.TURNING_TYPES:
            result = self.__turningTasksResult(ObsTaskScore)

        return result
        
    def __parkingTasksResult(self, obs_task_score:ObstacleTaskScore):
        
        sensor_ids = obs_task_score.task.sensor_id.split(",")
        hand_brake_sensor_id = sensor_ids[2]
        park_light_sensor_id = sensor_ids[3]

        task_obj = obs_task_score.task

        #either parking light or hand brake is enabled
        filter = Q(obstacle_id= obs_task_score.obstacle_id) & Q(~Q(**{"%s" % hand_brake_sensor_id: 0}) | ~Q(**{"%s" % park_light_sensor_id: 0}))
        # ,or_(~Q(**{"%s" % reverse_sensor_id: '0'}),\
        #                                                    ~Q(**{"%s" % park_light_sensor_id: '0'}))
        latest_sensor_feeds = SensorFeed.objects.filter(filter).order_by('-created_at')[:1]
        result = False
        if latest_sensor_feeds:
            #choose which calculation logic to use
            dis_sensor_calculation = self.DISTANCE_SENSOR_LEFT_RIGHT

            if task_obj.category == Task.TASK_TYPE_LEFT_PARKING:
                dis_sensor_calculation = self.DISTANCE_SENSOR_LEFT_ONLY
            elif task_obj.category == Task.TASK_TYPE_RIGHT_PARKING:
                dis_sensor_calculation = self.DISTANCE_SENSOR_RIGHT_ONLY
            
            result = self.__distance_sensor_result(dis_sensor_calculation, latest_sensor_feeds, obs_task_score)
        return result
    
    def __distance_sensor_result(self, sensor_calculation: int, sensor_feeds: SensorFeed, obs_task_score:ObstacleTaskScore) -> bool:
        
        left_min_range = int(obs_task_score.task_metrics.left_min_range)
        left_max_range = int(obs_task_score.task_metrics.left_max_range)
        right_min_range = int(obs_task_score.task_metrics.right_min_range)
        right_max_range = int(obs_task_score.task_metrics.right_max_range)

        sensor_ids = obs_task_score.task.sensor_id.split(",")
        left_sensor_id = sensor_ids[0]
        right_sensor_id = sensor_ids[1]

        result = False
        for sensor_feed in sensor_feeds:
            if sensor_calculation == self.DISTANCE_SENSOR_LEFT_ONLY:
                    left_sensor_val = int(getattr(sensor_feed, left_sensor_id))
                    if  left_min_range <= left_sensor_val and left_sensor_val <= left_max_range:
                        result = True
            elif sensor_calculation == self.DISTANCE_SENSOR_RIGHT_ONLY:
                right_sensor_val = int(getattr(sensor_feed, right_sensor_id))
                if right_min_range <= right_sensor_val and right_sensor_val  <= right_max_range:
                    result = True
            elif sensor_calculation == self.DISTANCE_SENSOR_LEFT_RIGHT:
                
                left_sensor_val = int(getattr(sensor_feed, left_sensor_id))
                right_sensor_val = int(getattr(sensor_feed, right_sensor_id))
                
                if  left_min_range <= left_sensor_val and left_sensor_val <= left_max_range and \
                    right_min_range <= right_sensor_val and right_sensor_val  <= right_max_range:
                    result = True
            
            #break if one result is failed
            if result == False:
                break

        return result
    
    def __speedResult(self, ObsTaskScore:ObstacleTaskScore):
        """Check if speed is in limit

        Args:
            ObsTaskScore (ObstacleTaskScore): _description_

        Returns:
            _type_: _description_
        """
        filter_query = Q(**{"obstacle_id": ObsTaskScore.obstacle_id })
        
        dates = SensorFeed.objects.filter(filter_query).aggregate(first_date=Min("created_at"),\
                                    last_date=Max("created_at"))
        first_date = dates.first_date
        last_date = dates.last_date
        average_distance = ObsTaskScore.task_metrics.distance
        speed_limit = ObsTaskScore.task_metrics.success_value
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

    def __turningTasksResult(self, obs_task_score:ObstacleTaskScore)->bool:
        """Turing result calculator

        Args:
            obs_task_score (ObstacleTaskScore): _description_

        Returns:
            Bool: Boolean
        """
        dis_sensor_calculation = self.DISTANCE_SENSOR_LEFT_RIGHT
        
        task_category = obs_task_score.task.category

        dis_sensor_calculation = self.DISTANCE_SENSOR_LEFT_RIGHT
        if task_category == Task.TASK_TYPE_LEFT_TURNING:
            dis_sensor_calculation = self.DISTANCE_SENSOR_LEFT_ONLY
        elif task_category == Task.TASK_TYPE_RIGHT_TURNING:
            dis_sensor_calculation = self.DISTANCE_SENSOR_RIGHT_ONLY
        
        filter_query = Q(**{ "obstacle_id": obs_task_score.obstacle_id })
        sensor_feed = SensorFeed.objects.filter(filter_query)
        result = self.__distance_sensor_result(dis_sensor_calculation, sensor_feed, obs_task_score)
        
        return result

    def __booleanTasksResult(self, ObsTaskScore:ObstacleTaskScore) -> bool:
        success_value = ObsTaskScore.task_metrics.success_value
        sensor_id = ObsTaskScore.task.sensor_id
        filter_query = Q(**{"%s" % sensor_id: success_value, "obstacle_id": ObsTaskScore.obstacle_id })
        return SensorFeed.objects.filter(filter_query).exists()
        