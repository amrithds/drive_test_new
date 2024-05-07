from django.core.management.base import BaseCommand
import serial
from course.models.session import Session
from course.models.obstacle import Obstacle
from course.models.sensor_feed import SensorFeed
from course.models.obstacle_session_tracker import ObstacleSessionTracker
from course.models.obstacle_task_score import ObstacleTaskScore
from report.models.session_report import SessionReport
from course.helper import start_session_helper
from course.helper import rf_id_helper
from course.helper.report_generator import ReportGenerator

import concurrent.futures

import logging
RF_logger = logging.getLogger("RFlog")

sensor_logger = logging.getLogger("sensorLog")

class Command(BaseCommand):
    help = 'Start a session, listen to inputs'
    # global variables
    CURRENT_RF_ID=None
    COLLECT_SENSOR_INPUTS=False
    RF_ID_OBSTACLE_MAP = {}
    SESSION = None
    
    def add_arguments(self, parser):
        parser.add_argument('-i','--trainer_no', type=int, help='trainer number of user in session')
        parser.add_argument('-s','--trainee_no', type=int, help='trainee number of user in session')
        parser.add_argument('-m', '--mode', type=int, help='session mode', choices=(0,1))
        parser.add_argument('-c', '--course', type=str, help='course name EX: apr_2024' )
        parser.add_argument('-ses', '--session_id', type=int, help='session id')


    def handle(self, *args, **kwargs):

        trainerID = kwargs['trainer_no']
        traineeID = kwargs['trainee_no']
        session_mode = int(kwargs['mode'])
        course_id = kwargs['course']
        
        #session_id is optional during debug
        if kwargs["session_id"]:
            self.SESSION = Session.objects.get(id=kwargs["session_id"])
        else:
            self.SESSION = start_session_helper.createSession(trainerID,traineeID,session_mode, course_id)
        
        #clean data from last session
        start_session_helper.initialiseSession()
        pool = concurrent.futures.ThreadPoolExecutor(max_workers=3)
        
        pool.submit(self.readRFIDInputs)
        pool.submit(self.readSTMInputs)
        pool.submit(self.generateReport)
        
        pool.shutdown(wait=True)


    def generateReport(self):
        """
            Generate temp reports.
        """
        print('Report generator...')
        #initialise session report
        report_generotor = ReportGenerator(self.SESSION)
        report_generotor.generateReport()

    def readRFIDInputs(self):
        """
        reads RF ID contineously for changes and next RF ID
        """
        rfid = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=.01
        )
        print('Init RFID reader')
        #get all obstacles
        obstacleObjs = Obstacle.objects.all()

        #map refID and Obstacle obj
        
        for obstcaleObj in obstacleObjs:
            self.RF_ID_OBSTACLE_MAP[obstcaleObj.start_rf_id] = obstcaleObj
        
        #init 
        OSTracker = None
        while(True):
            readRFID = rf_id_helper.getInputFromRFID(rfid)
            #uppercase
            readRFID = readRFID.upper()
            if len(readRFID) == 16:
                if readRFID in self.RF_ID_OBSTACLE_MAP:
                    print(readRFID)
                    tempObstacleObj = self.RF_ID_OBSTACLE_MAP[readRFID]

                    self.CURRENT_RF_ID = readRFID
                    self.COLLECT_SENSOR_INPUTS = True
                    #create ObstacleSessionTracker
                    
                    OSTracker = ObstacleSessionTracker.objects.create(obstacle=tempObstacleObj\
                                                                       ,session=self.SESSION)
                elif self.CURRENT_RF_ID in self.RF_ID_OBSTACLE_MAP:
                    print("end", readRFID)
                    tempObstacleObj = self.RF_ID_OBSTACLE_MAP[self.CURRENT_RF_ID]
                    if tempObstacleObj.end_rf_id == readRFID:
                        self.COLLECT_SENSOR_INPUTS = False
                        OSTracker.status = ObstacleSessionTracker.STATUS_COMPLETED
                        OSTracker.save()
    
    def readSTMInputs(self):
        """
        reads STM for sensor inputs when READ_STM_FLAG is True
        """
        print('port before')
        arduino = serial.Serial(port='/dev/ttyACM0',  baudrate=115200,parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0.001 )
        print('port init')
        lastSensorFeed = []

        while True:
            if arduino.in_waiting and self.COLLECT_SENSOR_INPUTS:
                data = arduino.readline().decode('utf-8').split(',')

                if data != lastSensorFeed:
                    print(self.CURRENT_RF_ID, self.CURRENT_RF_ID)
                    ObstacleObj = self.RF_ID_OBSTACLE_MAP[self.CURRENT_RF_ID]
                    
                    SensorFeed.objects.create(Obstacle=ObstacleObj, s0=data[1], s1=data[2], s2=data[3], s3=data[4],\
                                            s4=data[5], s5=data[6], s6=data[7], s7=data[8], s8=data[9], s9=data[10],\
                                            s10=data[11],s11=data[12], s12=data[13], s13=data[14], s14=data[15], s15=data[16],\
                                            s16=data[17] )
                    lastSensorFeed = data

