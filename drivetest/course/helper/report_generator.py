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
from django.db import connection
from django.db.models import Q

logger = logging.getLogger("reportLog")

@singleton
class ReportGenerator():
    DISTANCE_SENSOR_LEFT_ONLY = 0
    DISTANCE_SENSOR_RIGHT_ONLY = 1
    DISTANCE_SENSOR_LEFT_AND_RIGHT = 2
    DISTANCE_SENSOR_LEFT_AND_RIGHT_ZIG_ZAG = 3
    DISTANCE_SENSOR_BACK = 4

    LEFT_SENSOR_SQL = "select min(id) from (SELECT id, s0,s1,s10, CASE WHEN LEAD(s0) OVER (ORDER BY id asc) \
            BETWEEN {left_min_range} and {left_max_range} THEN TRUE ELSE FALSE END AS in_range_1, CASE WHEN LEAD(s0,2) OVER (ORDER BY id asc) \
            BETWEEN {left_min_range} and {left_max_range} THEN TRUE ELSE FALSE END AS in_range_2, CASE WHEN LEAD(s0,3) OVER (ORDER BY id asc) \
            BETWEEN {left_min_range} and {left_max_range} THEN TRUE ELSE FALSE END AS in_range_3 FROM report_sensor_feed where obstacle_id = {obstacle_id} {min_id_criteria} \
            ORDER BY ID ASC) \
            a where s0 BETWEEN {left_min_range} and {left_max_range} and in_range_1 and in_range_2 and in_range_3;"
        
    RIGHT_SENSOR_SQL = "select min(id) from (SELECT id, s0,s1,s10, CASE WHEN LEAD(s1) OVER (ORDER BY id asc) \
        BETWEEN {right_min_range} and {right_max_range} THEN TRUE ELSE FALSE END AS in_range_1, CASE WHEN LEAD(s1,2) OVER (ORDER BY id asc) \
        BETWEEN {right_min_range} and {right_max_range} THEN TRUE ELSE FALSE END AS in_range_2, CASE WHEN LEAD(s1,3) OVER (ORDER BY id asc) \
        BETWEEN {right_min_range} and {right_max_range} THEN TRUE ELSE FALSE END AS in_range_3 FROM report_sensor_feed where obstacle_id = {obstacle_id} {min_id_criteria} \
        ORDER BY ID ASC ) \
        a where s1 BETWEEN {right_min_range} and {right_max_range} and in_range_1 and in_range_2 and in_range_3;"

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
                session_reports = SessionReport.objects.exclude(~Q(task__category=Task.TASK_TYPE_BOOLEAN_ALL_SUCCESS), result=SessionReport.RESULT_PASS).filter(obstacle_id=OSTracker.obstacle_id)
                
                for session_report in session_reports:
                    
                    ObsTaskScore = ObstacleTaskScore.objects.get(obstacle_id=session_report.obstacle_id\
                                                      , task_id=session_report.task_id)

                    result = self.__getResult(ObsTaskScore)

                    if result is True and session_report.result == SessionReport.RESULT_FAIL:
                        session_report.result = SessionReport.RESULT_PASS
                        session_report.remark = ObsTaskScore.task_metrics.success_message
                        session_report.save()
                    elif session_report.result == SessionReport.RESULT_PASS:
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
        if task_category in Task.BOOLEAN_TASKS:
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
        else:
            filter = Q(obstacle_id= obs_task_score.obstacle_id)
        latest_sensor_feeds = SensorFeed.objects.filter(filter).order_by('-created_at')[:5000]
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
            #default back sensor
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
        
        task_category = obs_task_score.task.category
       
        if task_category == Task.TASK_TYPE_LEFT_TURNING:
            return self.__turn_with_one_sensor_result(obs_task_score, 1)
        elif task_category == Task.TASK_TYPE_RIGHT_TURNING:
            return self.__turn_with_one_sensor_result(obs_task_score, 2)
        elif task_category == Task.TASK_TYPE_DUAL_SENSOR_TURNING:
            return self.__turn_with_left_right_sensor(obs_task_score)
        elif task_category == Task.TASK_TYPE_DUAL_SENSOR_TURNING_ZIG_ZAG:
            return self.__zig_zag_turn_result(obs_task_score)
        elif task_category == Task.TASK_TYPE_FIGURE_OF_EIGHT:
            return self.__figure_of_eight_result(obs_task_score)
        
        return False
    
    def __turn_with_one_sensor_result(self, obs_task_score: ObstacleTaskScore, sensor_type: int):
        """Result using Left/Right sensor value

        Args:
            obs_task_score (ObstacleTaskScore): _description_
            sensor_type (int): 
            1 : Left
            2 : right

        Returns:
            _type_: _description_
        """

        obstacle_id = obs_task_score.obstacle_id

        with connection.cursor() as cursor:
            def execute_raw_sql(sql: str):
                """
                execute raw query
                """
                cursor.execute(sql)
                result = cursor.fetchone()
                return result[0]

            # left sensor result
            sql = ''
            if sensor_type == 1:
                left_min_range = obs_task_score.task_metrics.left_min_range
                left_max_range = obs_task_score.task_metrics.left_max_range
                sql = self.LEFT_SENSOR_SQL.format(obstacle_id=obstacle_id, min_id_criteria='', left_min_range=left_min_range,\
                                                                left_max_range=left_max_range)
            else:
                right_min_range = obs_task_score.task_metrics.right_min_range
                right_max_range = obs_task_score.task_metrics.right_max_range
                sql = self.RIGHT_SENSOR_SQL.format(obstacle_id=obstacle_id, min_id_criteria='', left_min_range=left_min_range,\
                                                                left_max_range=left_max_range)
            min_id = execute_raw_sql(sql)
            if min_id:
                return True
            
        return False


    
    def __turn_with_left_right_sensor(self, obs_task_score: ObstacleTaskScore):
        """Both  left and right sensors should be in range while turning

        Args:
            obs_task_score (ObstacleTaskScore): _description_
        """
        left_min_range = obs_task_score.task_metrics.left_min_range
        left_max_range = obs_task_score.task_metrics.left_max_range
        right_min_range = obs_task_score.task_metrics.right_min_range
        right_max_range = obs_task_score.task_metrics.right_max_range
        obstacle_id = obs_task_score.obstacle_id

        sql = "select min(id) from (SELECT id, s0,s1,s10, CASE WHEN LEAD(s0) OVER (ORDER BY id asc) \
            BETWEEN {left_min_range} and {left_max_range} THEN TRUE ELSE FALSE END AS left_in_range_1, CASE WHEN LEAD(s0,2) OVER (ORDER BY id asc) \
            BETWEEN {left_min_range} and {left_max_range} THEN TRUE ELSE FALSE END AS left_in_range_2, CASE WHEN LEAD(s0,3) OVER (ORDER BY id asc) \
            BETWEEN {left_min_range} and {left_max_range} THEN TRUE ELSE FALSE END AS left_in_range_3, \
            CASE WHEN LEAD(s1) OVER (ORDER BY id asc) \
            BETWEEN {right_min_range} and {right_max_range} THEN TRUE ELSE FALSE END AS right_in_range_1, CASE WHEN LEAD(s0,2) OVER (ORDER BY id asc) \
            BETWEEN {right_min_range} and {right_max_range} THEN TRUE ELSE FALSE END AS right_in_range_2, CASE WHEN LEAD(s0,3) OVER (ORDER BY id asc) \
            BETWEEN {right_min_range} and {right_max_range} THEN TRUE ELSE FALSE END AS right_in_range_3 \
            FROM report_sensor_feed where obstacle_id = {obstacle_id} \
            ORDER BY ID ASC) \
            a where s0 BETWEEN {left_min_range} and {left_max_range}  and left_in_range_1 and left_in_range_2 and left_in_range_3 \
            and s1 BETWEEN {right_min_range} and {right_max_range} and right_in_range_1 and right_in_range_2 and right_in_range_3;".format(\
                left_min_range=left_min_range, left_max_range=left_max_range, right_min_range=right_min_range, right_max_range=right_max_range, obstacle_id=obstacle_id\
            )
        
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchone()
            min_id = result[0]
            print(str(sql)+'........')
            if min_id:
                return True
            
        return False
    
    def __zig_zag_turn_result(self, obs_task_score: ObstacleTaskScore):
        """Get result for zig zag turning

        Args:
            obs_task_score (ObstacleTaskScore): _description_

        Returns:
            Bool: _description_
        """
        left_min_range = obs_task_score.task_metrics.left_min_range
        left_max_range = obs_task_score.task_metrics.left_max_range
        right_min_range = obs_task_score.task_metrics.right_min_range
        right_max_range = obs_task_score.task_metrics.right_max_range
        obstacle_id = obs_task_score.obstacle_id

        

        with connection.cursor() as cursor:
            def execute_raw_sql(sql: str):
                """
                execute raw query
                """
                cursor.execute(sql)
                result = cursor.fetchone()
                return result[0]

            # turn right first and then left
            min_id = execute_raw_sql(self.LEFT_SENSOR_SQL.format(obstacle_id=obstacle_id, min_id_criteria='', left_min_range=left_min_range,\
                                                            left_max_range=left_max_range))
            
            if min_id:
                min_id = execute_raw_sql(self.RIGHT_SENSOR_SQL.format(obstacle_id=obstacle_id,min_id_criteria=f'and id > {min_id}', \
                                                                 right_min_range=right_min_range,right_max_range=right_max_range))
                
                if min_id:
                    return True
            
            # turn left first and then right
            min_id = execute_raw_sql(self.RIGHT_SENSOR_SQL.format(obstacle_id=obstacle_id, min_id_criteria='',\
                                                             right_min_range=right_min_range,right_max_range=right_max_range))
            
            if min_id:
                min_id = execute_raw_sql(self.LEFT_SENSOR_SQL.format(obstacle_id=obstacle_id,min_id_criteria=f'and id > {min_id}' , \
                                                                    left_min_range=left_min_range,left_max_range=left_max_range))
                
                if min_id:
                    return True
                

            return False
           
    
    def __figure_of_eight_result(self, obs_task_score: ObstacleTaskScore):
        """Result for  figure of 8 driving

        Args:
            obs_task_score (ObstacleTaskScore): _description_

        Returns:
            Bool: _description_
        """
        left_min_range = obs_task_score.task_metrics.left_min_range
        left_max_range = obs_task_score.task_metrics.left_max_range
        right_min_range = obs_task_score.task_metrics.right_min_range
        right_max_range = obs_task_score.task_metrics.right_max_range
        obstacle_id = obs_task_score.obstacle_id
        
        
        with connection.cursor() as cursor:
            def execute_raw_sql(sql: str):
                """
                execute raw query
                """
                cursor.execute(sql)
                result = cursor.fetchone()
                return result[0]

            # if vehicle move right -> left -> right -> left
            min_id = execute_raw_sql(self.LEFT_SENSOR_SQL.format(obstacle_id=obstacle_id, min_id_criteria='', left_min_range=left_min_range,\
                                                            left_max_range=left_max_range))
            
            if min_id:
                min_id = execute_raw_sql(self.RIGHT_SENSOR_SQL.format(obstacle_id=obstacle_id,min_id_criteria=f'and id > {min_id}', \
                                                                 right_min_range=right_min_range,right_max_range=right_max_range))
            
                if min_id:
                    min_id = execute_raw_sql(self.LEFT_SENSOR_SQL.format(obstacle_id=obstacle_id,min_id_criteria=f'and id > {min_id}' , \
                                                                    left_min_range=left_min_range,left_max_range=left_max_range))
                    
                    if min_id:
                        min_id = execute_raw_sql(self.RIGHT_SENSOR_SQL.format(obstacle_id=obstacle_id, min_id_criteria=f'and id > {min_id}', \
                                                                         right_min_range=right_min_range,right_max_range=right_max_range))
                        
                        if min_id:
                            return True
            
            # if vehicle move left -> right -> left -> right
            min_id = execute_raw_sql(self.RIGHT_SENSOR_SQL.format(obstacle_id=obstacle_id, min_id_criteria='',\
                                                             right_min_range=right_min_range,right_max_range=right_max_range))
            
            if min_id:
                min_id = execute_raw_sql(self.LEFT_SENSOR_SQL.format(obstacle_id=obstacle_id,min_id_criteria=f'and id > {min_id}' , \
                                                                    left_min_range=left_min_range,left_max_range=left_max_range))
                
                if min_id:
                    min_id = execute_raw_sql(self.RIGHT_SENSOR_SQL.format(obstacle_id=obstacle_id, min_id_criteria=f'and id > {min_id}', \
                                                                         right_min_range=right_min_range,right_max_range=right_max_range))
                    
                    if min_id:
                        min_id = execute_raw_sql(self.LEFT_SENSOR_SQL.format(obstacle_id=obstacle_id,min_id_criteria=f'and id > {min_id}' , \
                                                                    left_min_range=left_min_range,left_max_range=left_max_range))
                        
                        if min_id:
                            return True
            
            return False

    def __booleanTasksResult(self, obs_task_score:ObstacleTaskScore) -> bool:
        """Boolean task result

        Args:
            obs_task_score (ObstacleTaskScore): _description_

        Returns:
            bool: _description_
        """
        task_category = obs_task_score.task.category
        sensor_id = obs_task_score.task.sensor_id
        print('here')
        #if task is boolean all success then failure should not be present
        if task_category == Task.TASK_TYPE_BOOLEAN:
            value = obs_task_score.task_metrics.success_value
            filter_query = Q(**{"%s" % sensor_id: value, "obstacle_id": obs_task_score.obstacle_id })
            return SensorFeed.objects.filter(filter_query).exists()
        else:
            value = obs_task_score.task_metrics.failure_value
            filter_query = Q(**{"%s" % sensor_id: value, "obstacle_id": obs_task_score.obstacle_id })
            print(SensorFeed.objects.filter(filter_query).query)
            if SensorFeed.objects.filter(filter_query).count():
                return False
            return True