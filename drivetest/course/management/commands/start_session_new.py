from django.core.management.base import BaseCommand
from course.models.session import Session
from course.models.obstacle import Obstacle

from course.models.obstacle_session_tracker import ObstacleSessionTracker
from course.helper import start_session_helper
from course.helper import cache_helper
from course.helper.report_generator import ReportGenerator
from course.helper.data_generator import read_rf_id_mock
from course.helper import rf_id_helper
from course.helper import STM_helper
from course.models.obstacle_task_score import ObstacleTaskScore
from course.models.task import Task 

from django.conf import settings
from app_config.helper import bluetooth_speaker_helper
from course.helper.vehicle_sensor import VehicleSensor
from app_config.models import Config
import os
import json 

from concurrent.futures import ProcessPoolExecutor
from course.helper.jobs import rf_id_reader_job
from course.helper.jobs import read_STM_job
from course.helper.jobs import report_job


import logging
RF_logger = logging.getLogger("RFLog")

sensor_logger = logging.getLogger("sensorLog")
report_logger = logging.getLogger("reportLog")



class Command(BaseCommand):
    help = 'Start a session, listen to inputs'
    # global variables
    CURRENT_REF_ID=None
    COLLECT_SENSOR_INPUTS=False
    RF_ID_OBSTACLE_MAP = {}
    SESSION = None
    AUDIO_LOCATION = str(settings.MEDIA_ROOT)
    RESUME=False
    AUDIO_FILE=None

    def add_arguments(self, parser):
        parser.add_argument('-i','--trainer', type=int, help='trainer number of user in session')
        parser.add_argument('-s','--trainee', type=int, help='trainee number of user in session')
        parser.add_argument('-m', '--mode', type=int, help='session mode', choices=(0,1))
        parser.add_argument('-c', '--course', type=str, help='course name EX: apr_2024' )
        parser.add_argument('-ses', '--session_id', type=int, help='session id')
        parser.add_argument('-r', '--resume', type=int, help='resume interupted process? 0/1', default=0)

    def handle(self, *args, **kwargs):
        self.RESUME = kwargs['resume']
        
        #session_id is optional during debug
        session_mode = None
        if kwargs["session_id"]:
            self.SESSION = Session.objects.get(id=kwargs["session_id"])
            session_mode = self.SESSION.mode
        else:
            trainer_id = kwargs['trainer']
            trainee_id = kwargs['trainee']
            session_mode = int(kwargs['mode'])
            course_id = kwargs['course']
            self.SESSION = start_session_helper.createSession(trainer_id, trainee_id,session_mode, course_id)
        
        #cache keys
        CACHE_KEYS = ('CURRENT_REF_ID', 'COLLECT_SENSOR_INPUTS', 'AUDIO_FILE')
        

        if not self.RESUME:
            #clean data from last session
            start_session_helper.initialiseSession()

            #reset cache
            cache_helper.delete_cache(CACHE_KEYS)

        executor = ProcessPoolExecutor(4)
        
        rf_id_reader = executor.submit(rf_id_reader_job.vehicle_location_sensor, self.SESSION)
        STM_reader = executor.submit(read_STM_job.readSTMInputs)
        report = executor.submit(report_job.report_generator, self.SESSION, self.RESUME)

        print('here')
    




