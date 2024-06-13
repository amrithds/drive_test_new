from django.core.management.base import BaseCommand
from course.models.session import Session
from course.models.obstacle import Obstacle
from report.models.sensor_feed import SensorFeed
from course.models.obstacle_session_tracker import ObstacleSessionTracker
from course.helper import start_session_helper
from course.helper.report_generator import ReportGenerator
from course.helper import rf_id_helper
from course.helper.STM_helper import STMReader
from course.models.obstacle_task_score import ObstacleTaskScore
from course.models.task import Task 
import copy
import concurrent.futures
from django.conf import settings
from app_config.helper import bluetooth_speaker_helper
from course.helper.vehicle_sensor import VehicleSensor
from app_config.models import Config
import os
import json 
import threading
from pwd import getpwnam
import pwd

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
    VEHICLE_SENSORS_RFID = 'RFID'
    VEHICLE_SENSORS_TCP = 'TCP'
    VEHICLE_SENSORS = ('RFID', 'TCP')
    OBS_TASK_IP_ADDRESS = {}
    
    def add_arguments(self, parser):
        parser.add_argument('-i','--trainer', type=int, help='trainer number of user in session')
        parser.add_argument('-s','--trainee', type=int, help='trainee number of user in session')
        parser.add_argument('-m', '--mode', type=int, help='session mode', choices=(0,1))
        parser.add_argument('-c', '--course', type=str, help='course name EX: apr_2024' )
        parser.add_argument('-ses', '--session_id', type=int, help='session id')
        parser.add_argument('-r', '--resume', type=int, help='resume interupted process? 0/1', default=0)


    def handle(self, *args, **kwargs):

        trainer_id = kwargs['trainer']
        trainee_id = kwargs['trainee']
        session_mode = int(kwargs['mode'])
        course_id = kwargs['course']
        self.RESUME = kwargs['resume']
        
        #session_id is optional during debug
        if kwargs["session_id"]:
            self.SESSION = Session.objects.get(id=kwargs["session_id"])
        else:
            self.SESSION = start_session_helper.createSession(trainer_id, trainee_id,session_mode, course_id)
        
        # connect bluetooth
        if bluetooth_speaker_helper.connect_bluetooth():
            report_logger.info('Bluetooth connected')
        else:
            report_logger.error('Bluetooth unable to connect')

        if not self.RESUME:
            #clean data from last session
            start_session_helper.initialiseSession()
        
        try:
            app_config = Config.objects.get(name='LOCATION_SENSOR')
            sensor_type = app_config.value
        except Exception as e:
            sensor_type = self.VEHICLE_SENSORS_RFID
        
        pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        
        if sensor_type == self.VEHICLE_SENSORS_RFID:
            pool.submit(self.read_location_inputs)
        else:
            pool.submit(self.read_vehicle_sensor)
        pool.submit(self.readSTMInputs)
        pool.submit(self.generateReport)
        pool.submit(self.playAudio)
        
        pool.shutdown(wait=True)

    def playAudio(self):
        last_played = None
        
        while True:
            try:
                if self.AUDIO_FILE != last_played:
                    
                    user = pwd.getpwuid(os.getuid())[0]
                    uid = getpwnam(user).pw_uid
                    #uid = uid_parsed[1].split('(')[0]
                    report_logger.error(uid)
                    os.system(f'XDG_RUNTIME_DIR=/run/user/{uid} paplay {self.AUDIO_FILE}')
                    last_played = self.AUDIO_FILE
            except Exception as e:
                report_logger.exception("Error: "+str(e))

    def generateReport(self):
        """
            Generate temp reports.
        """
        print('Report generator...')
        #initialise session report
        try:
            report_generotor = ReportGenerator(self.SESSION, self.RESUME)
            report_generotor.generateReport()
        except Exception as e:
            report_logger.exception("Error: "+str(e))

    def read_vehicle_sensor(self):
        RF_logger.info("IP based sensor")
        obstacles = Obstacle.objects.all()
        
        #get all obstacles
        self.RF_ID_OBSTACLE_MAP = start_session_helper.get_obstacle_mapping()
        OSTracker = None
        completed_obstacles= {}
        while True:
            try:
                for ip_address in self.RF_ID_OBSTACLE_MAP:
                    # print(self.RF_ID_OBSTACLE_MAP)
                    if ip_address not in completed_obstacles and VehicleSensor.IP_in_range(ip_address):
                        print("ip_address",ip_address)
                        tempObstacleObj = self.RF_ID_OBSTACLE_MAP[ip_address]
                        print("obstacle name",tempObstacleObj)
                        self.CURRENT_REF_ID = ip_address
                        self.COLLECT_SENSOR_INPUTS = True
                        #create ObstacleSessionTracker
                        # print("obstacle id",tempObstacleObj.id)

                        ObsTaskScores = ObstacleTaskScore.objects.filter(obstacle_id=tempObstacleObj.id)
                        for obs_task_score in ObsTaskScores:
                            if obs_task_score.task.category in Task.PARKING_TYPES:
                                self.OBS_TASK_IP_ADDRESS = obs_task_score.ip_address
                        if OSTracker is None or OSTracker.obstacle_id != tempObstacleObj.id:
                            #play training audio
                            if self.SESSION.mode == Session.MODE_TRAINING:
                                self.AUDIO_FILE = self.AUDIO_LOCATION+str(tempObstacleObj.audio_file)
                            
                            previousOSTracker = copy.deepcopy(OSTracker)
                            OSTracker,_ = ObstacleSessionTracker.objects.get_or_create(obstacle=tempObstacleObj\
                                                                        ,session=self.SESSION)
                            
                            #complete preious obscale when new IP is read
                            if previousOSTracker is not None and previousOSTracker.status == ObstacleSessionTracker.STATUS_IN_PROGRESS:
                                completed_obstacles[ip_address] = 1
                                previousOSTracker.status = ObstacleSessionTracker.STATUS_COMPLETED
                                previousOSTracker.save()
                            sensor_logger.info("completed_obstacles",completed_obstacles)
                            sensor_logger.info(len(completed_obstacles),len(self.RF_ID_OBSTACLE_MAP))
                            if len(completed_obstacles) == len(self.RF_ID_OBSTACLE_MAP):
                                break
            except Exception as e:
                RF_logger.exception(e)

    def read_location_inputs(self):
        """
        reads RF ID contineously for changes and next RF ID
        """
        try:
            
            RF_logger.info('Init RFID reader')
            #get all obstacles
            self.RF_ID_OBSTACLE_MAP = start_session_helper.get_obstacle_mapping()
            
            #init
            RF_ID_reader = rf_id_helper.RFIDReader()
            OSTracker = None
            
            #rf_id_gen = DataGenerator.RFIDGenerator()
            while(True):
                readRFID = RF_ID_reader.getInputFromRFID()
                #readRFID = next(rf_id_gen)
                
                #uppercase
                readRFID = readRFID.upper()
                if len(readRFID) == 16:
                    if readRFID in self.RF_ID_OBSTACLE_MAP:
                        print(readRFID)
                        tempObstacleObj = self.RF_ID_OBSTACLE_MAP[readRFID]

                        self.CURRENT_REF_ID = readRFID
                        self.COLLECT_SENSOR_INPUTS = True
                        #create ObstacleSessionTracker
                        if OSTracker is None or OSTracker.obstacle_id != tempObstacleObj.id:
                            #play training audio
                            if self.SESSION.mode == Session.MODE_TRAINING:
                                self.AUDIO_FILE = self.AUDIO_LOCATION+str(tempObstacleObj.audio_file)
                            
                            previousOSTracker = copy.deepcopy(OSTracker)
                            OSTracker,_ = ObstacleSessionTracker.objects.get_or_create(obstacle=tempObstacleObj\
                                                                        ,session=self.SESSION)
                            
                            #check if start RFID of next obstacle is read before reading previous
                            #obstacles end RFID, then mark previous obstacle as completed
                            if previousOSTracker is not None and previousOSTracker.status == ObstacleSessionTracker.STATUS_IN_PROGRESS:
                                previousOSTracker.status = ObstacleSessionTracker.STATUS_COMPLETED
                                previousOSTracker.save()
                            
                    elif self.CURRENT_REF_ID in self.RF_ID_OBSTACLE_MAP:
                        tempObstacleObj = self.RF_ID_OBSTACLE_MAP[self.CURRENT_REF_ID]
                        if tempObstacleObj.end_rf_id.upper() == readRFID:
                            print("end", readRFID)
                            self.COLLECT_SENSOR_INPUTS = False
                            OSTracker.status = ObstacleSessionTracker.STATUS_COMPLETED
                            OSTracker.save()
        except Exception as e:
            RF_logger.exception(e)
    
    def readSTMInputs(self):
        """
        reads STM for sensor inputs when READ_STM_FLAG is True
        """
        try:
            sensor_logger.info('Init STM reader')
            STM_reader = STMReader()
            #STMreader =  DataGenerator.STMGenerator()
            lastSensorFeed = []
            
            while True:
                #if self.COLLECT_SENSOR_INPUTS:
                    # data = next(STMreader)
                    # print(self.COLLECT_SENSOR_INPUTS)
                    # print(data)
                
                if self.COLLECT_SENSOR_INPUTS:
                    data = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]  
                    if STM_reader.dataWaiting():
                        data = STM_reader.getSTMInput()
                        sensor_logger.info(data)
                    if self.OBS_TASK_IP_ADDRESS:
                        addrs = json.loads(self.OBS_TASK_IP_ADDRESS)
                        for key, value in addrs.items():
                            for ip_address in value:
                                distance_val = VehicleSensor.distance_ip_addrs(ip_address)
                                # print("distance_val",distance_val)
                                if key=='s0':
                                    data[1] = int(distance_val)
                                if key=='s1':
                                    data[2] = int(distance_val)
                                if key=='s10':
                                    data[11] = int(distance_val)
                    # conside data less than 19 as noise
                    if len(data) == 19 and data != lastSensorFeed and self.CURRENT_REF_ID in self.RF_ID_OBSTACLE_MAP:

                        ObstacleObj = self.RF_ID_OBSTACLE_MAP[self.CURRENT_REF_ID]

                        SensorFeed.objects.create(obstacle=ObstacleObj, s0=data[1], s1=data[2], s2=data[3], s3=data[4],\
                                                s4=data[5], s5=data[6], s6=data[7], s7=data[8], s8=data[9], s9=data[10],\
                                                s10=data[11],s11=data[12], s12=data[13], s13=data[14], s14=data[15], s15=data[16],\
                                                s16=data[17] )

                        lastSensorFeed = data
        except Exception as e:
            sensor_logger.exception('Error: '+str(e))
