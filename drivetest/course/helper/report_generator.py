from course.models.obstacle_session_tracker import ObstacleSessionTracker
from singleton_decorator import singleton
from course.models.obstacle_task_score import ObstacleTaskScore
from course.models.obstacle import Obstacle
from report.models.session_report import SessionReport
from course.models.session import Session
from report.models.final_report import FinalReport 
from course.models.task import Task
from report.models.sensor_feed import SensorFeed
from django.db.models import Min, Q, Max
from report.helper import report_helper
import datetime
import logging

logger = logging.getLogger("reportLog")

@singleton
class ReportGenerator():
    DISTANCE_SENSOR_LEFT_ONLY = 0
    DISTANCE_SENSOR_RIGHT_ONLY = 1
    DISTANCE_SENSOR_LEFT_AND_RIGHT = 2
    DISTANCE_SENSOR_LEFT_AND_RIGHT_ZIG_ZAG = 3
    DISTANCE_SENSOR_BACK = 4

    def __init__(self, session: Session, resume: int=False) -> None:
        """init
        Args:
            session (Session): session object
        """
        self.session = session
        self.resume = resume
       
    def generateReport(self):
        """
        Generate report from session data feed
        """
        if not self.resume:
            self.__initializeSessionReport()

        while True:
            OSTrackers = ObstacleSessionTracker.objects.filter(session = self.session\
                        , report_status = ObstacleSessionTracker.STATUS_IN_PROGRESS)
            
            for OSTracker in OSTrackers:
                #SessionReport
                session_reports = SessionReport.objects.filter(obstacle_id=OSTracker.obstacle_id)
                
                for session_report in session_reports:
                    ObsTaskScore = ObstacleTaskScore.objects.get(obstacle_id=session_report.obstacle_id\
                                                      , task_id=session_report.task_id)

                    result = self.__getResult(ObsTaskScore)

                    if result is True:
                        print('result', result, ObsTaskScore.obstacle, ObsTaskScore.task)
                        session_report.result = SessionReport.RESULT_PASS
                        session_report.remark = ObsTaskScore.task_metrics.success_message
                    else:
                        session_report.result = SessionReport.RESULT_FAIL
                        session_report.remark = ObsTaskScore.task_metrics.failure_message
                    session_report.save()

                #when task is complted then stop generating report 
                if OSTracker.status == ObstacleSessionTracker.STATUS_COMPLETED:
                    OSTracker.report_status = ObstacleSessionTracker.STATUS_COMPLETED
                    OSTracker.save()

    def generateFinalReport(self):
        """
        Generate final report from session data feed
        """
        obstacles = Obstacle.objects.all()

        for obstacle in obstacles:
            final_report = FinalReport.objects.create(session=self.session, obstacle=obstacle, data={})
            session_task_reports = SessionReport.objects.filter(obstacle_id=obstacle.id).order_by('obstacle_id', 'task_id')
            #init obstacle level report
            data = []
            total_obs_score = 0
            total_score = 0
            for session_task_report in session_task_reports:
                task_report_json = {"task":session_task_report.task.name, "result" : session_task_report.result\
                               , "score": 0 , "remark" : session_task_report.remark }
                
                obs_task_score = ObstacleTaskScore.objects.get(obstacle_id=session_task_report.obstacle_id\
                                                               , task_id=session_task_report.task_id)
                
                if session_task_report.result == SessionReport.RESULT_PASS:
                    task_report_json['score'] = obs_task_score.score
                    total_obs_score += obs_task_score.score
                else:
                    if obs_task_score.is_mandatory:
                        final_report.result = FinalReport.RESULT_FAIL
                        final_report.save()

                total_score += obs_task_score.score
                data.append(task_report_json)
            
            final_report.total_score = total_score
            final_report.obtained_score = total_obs_score
            final_report.data = data
            final_report.obstacle_duration = report_helper.get_obstacle_duration(obstacle.id)
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
        task_obj = obs_task_score.task
        result = False

        if(len(sensor_ids)>2):
            hand_brake_sensor_id = sensor_ids[3]
            park_light_sensor_id = sensor_ids[4]

            #either parking light or hand brake is enabled
            filter = Q(obstacle_id= obs_task_score.obstacle_id) & Q(~Q(**{"%s" % hand_brake_sensor_id: 0}) | ~Q(**{"%s" % park_light_sensor_id: 0}))
            # ,or_(~Q(**{"%s" % reverse_sensor_id: '0'}),\ ~Q(**{"%s" % park_light_sensor_id: '0'}))
        else:
            filter = Q(obstacle_id= obs_task_score.obstacle_id)
        latest_sensor_feeds = SensorFeed.objects.filter(filter).order_by('-created_at')[:1]
        if latest_sensor_feeds:
            #choose which calculation logic to use
            dis_sensor_calculation = self.DISTANCE_SENSOR_LEFT_AND_RIGHT

            if task_obj.category == Task.TASK_TYPE_LEFT_PARKING:
                dis_sensor_calculation = self.DISTANCE_SENSOR_LEFT_ONLY
            elif task_obj.category == Task.TASK_TYPE_RIGHT_PARKING:
                dis_sensor_calculation = self.DISTANCE_SENSOR_RIGHT_ONLY
            elif task_obj.category == Task.TASK_TYPE_REVERSE_PARKING:
                dis_sensor_calculation = self.DISTANCE_SENSOR_BACK
            
            result = self.__distance_sensor_result(dis_sensor_calculation, latest_sensor_feeds, obs_task_score)
            print('result')
        return result
    
    def __distance_sensor_result(self, sensor_calculation: int, sensor_feeds: SensorFeed, obs_task_score:ObstacleTaskScore) -> bool:
        
        left_min_range = obs_task_score.task_metrics.left_min_range
        left_max_range = obs_task_score.task_metrics.left_max_range
        right_min_range = obs_task_score.task_metrics.right_min_range
        right_max_range = obs_task_score.task_metrics.right_max_range
        back_min_range = obs_task_score.task_metrics.back_min_range
        back_max_range = obs_task_score.task_metrics.back_max_range

        sensor_ids = obs_task_score.task.sensor_id.split(",")
        left_sensor_id = sensor_ids[0]
        right_sensor_id = sensor_ids[1]
        if(len(sensor_ids)>2):
            back_sensor_id = sensor_ids[2]
        else:
            back_sensor_id = "s10"

        result = False
        total_valid_count = 0
        REQUIRED_VALID_COUNT = 4
        ZIG_ZAG_LEFT_RESULT = 0
        ZIG_ZAG_RIGHT_RESULT = 0
        task = obs_task_score.task
        print('here : get result')
        for sensor_feed in sensor_feeds:
            left_sensor_val = getattr(sensor_feed, left_sensor_id)
            right_sensor_val = getattr(sensor_feed, right_sensor_id)
            back_sensor_val = getattr(sensor_feed, back_sensor_id)
            print("left_sensor_val",left_sensor_val,"right_sensor_val",right_sensor_val,"back_sensor_val",back_sensor_val)

            # reverse parking logic
            if sensor_calculation == self.DISTANCE_SENSOR_BACK:
                side_sensor_val = left_sensor_val if left_sensor_val else right_sensor_val
                if side_sensor_val:
                    if  left_min_range <= side_sensor_val and side_sensor_val <= left_max_range:
                        if back_sensor_val and back_min_range <= back_sensor_val and back_sensor_val <= back_max_range: 
                            total_valid_count += 1
                        else:
                            total_valid_count = 0

            elif sensor_calculation == self.DISTANCE_SENSOR_LEFT_ONLY:
                if  left_min_range <= left_sensor_val and left_sensor_val <= left_max_range:
                    total_valid_count += 1
                else:
                    total_valid_count = 0
            elif sensor_calculation == self.DISTANCE_SENSOR_RIGHT_ONLY:
                if right_min_range <= right_sensor_val and right_sensor_val  <= right_max_range:
                    total_valid_count += 1
                else:
                    total_valid_count = 0
            elif sensor_calculation == self.DISTANCE_SENSOR_LEFT_AND_RIGHT:
                
                if  left_min_range <= left_sensor_val and left_sensor_val <= left_max_range and \
                    right_min_range <= right_sensor_val and right_sensor_val  <= right_max_range:
                    total_valid_count += 1
                else:
                    total_valid_count = 0
            elif sensor_calculation == self.DISTANCE_SENSOR_LEFT_AND_RIGHT_ZIG_ZAG:
                if  left_min_range <= left_sensor_val and left_sensor_val <= left_max_range:
                    ZIG_ZAG_LEFT_RESULT += 1
                elif ZIG_ZAG_LEFT_RESULT < REQUIRED_VALID_COUNT:
                    ZIG_ZAG_LEFT_RESULT = 0
                
                if right_min_range <= right_sensor_val and right_sensor_val  <= right_max_range:
                    ZIG_ZAG_RIGHT_RESULT += 1
                elif ZIG_ZAG_RIGHT_RESULT < REQUIRED_VALID_COUNT:
                    ZIG_ZAG_RIGHT_RESULT = 0
            
            print("total_valid_count",total_valid_count)
            #break for parking criteria is met
            if total_valid_count == 1 and task.category in Task.PARKING_TYPES:
                result = True
                break
            #break if REQUIRED_VALID_COUNT is reached
            if (REQUIRED_VALID_COUNT == total_valid_count or (ZIG_ZAG_RIGHT_RESULT == REQUIRED_VALID_COUNT \
                                                                and ZIG_ZAG_RIGHT_RESULT == REQUIRED_VALID_COUNT)):
                result = True
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
        dis_sensor_calculation = self.DISTANCE_SENSOR_LEFT_AND_RIGHT
        
        task_category = obs_task_score.task.category

        dis_sensor_calculation = self.DISTANCE_SENSOR_LEFT_AND_RIGHT
        if task_category == Task.TASK_TYPE_LEFT_TURNING:
            dis_sensor_calculation = self.DISTANCE_SENSOR_LEFT_ONLY
        elif task_category == Task.TASK_TYPE_RIGHT_TURNING:
            dis_sensor_calculation = self.DISTANCE_SENSOR_RIGHT_ONLY
        elif task_category == Task.TASK_TYPE_DUAL_SENSOR_TURNING:
            dis_sensor_calculation = self.DISTANCE_SENSOR_LEFT_AND_RIGHT
        elif task_category == Task.TASK_TYPE_DUAL_SENSOR_TURNING_ZIG_ZAG:
            dis_sensor_calculation = self.DISTANCE_SENSOR_LEFT_AND_RIGHT_ZIG_ZAG
        
        filter_query = Q(**{ "obstacle_id": obs_task_score.obstacle_id })
        sensor_feed = SensorFeed.objects.filter(filter_query).order_by('created_at')
        result = self.__distance_sensor_result(dis_sensor_calculation, sensor_feed, obs_task_score)
        
        return result

    def __booleanTasksResult(self, ObsTaskScore:ObstacleTaskScore) -> bool:
        success_value = ObsTaskScore.task_metrics.success_value
        sensor_id = ObsTaskScore.task.sensor_id
        filter_query = Q(**{"%s" % sensor_id: success_value, "obstacle_id": ObsTaskScore.obstacle_id })
        return SensorFeed.objects.filter(filter_query).exists()
        
