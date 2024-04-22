from django.core.management.base import BaseCommand
from django.utils import timezone
import serial
from course.models.session import Session
from course.models.obstacle import Obstacle
from course.models.sensor_feed import SensorFeed
from course.models.user import User
from course.helper import rf_id_helper

import concurrent.futures

class Command(BaseCommand):
    help = 'Start a session, listen to inputs'
    # global variables
    CURRENT_RF_ID=None
    COLLECT_SENSOR_INPUTS=False
    RF_ID_OBSTACLE_MAP = {}
    
    def add_arguments(self, parser):
        parser.add_argument('trainer_no', type=int, help='trainer number of user in session')
        parser.add_argument('trainee_no', type=int, help='trainee number of user in session')
        parser.add_argument('mode', type=int, help='session mode', choices=(0,1))

    def handle(self, *args, **kwargs):

        trainerID = kwargs['trainer_no']
        traineeID = kwargs['trainee_no']
        session_mode = int(kwargs['mode'])
 
        sessionObj = self.initialiseSession(trainerID,traineeID,session_mode)
        
        pool = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        
        pool.submit(self.readRFIDInputs)
        pool.submit(self.readSTMInputs)
        
        pool.shutdown(wait=True)
        
        print("Main thread continuing to run")


    
    def initialiseSession(self, trainerID, traineeID, session_mode ):
        trainer = User.objects.get(id=trainerID)
        trainee = User.objects.get(id=traineeID)
        #update session with in progress status
        sessionObj = Session.objects.create(trainer_no=trainer, trainee_no=trainee, mode=session_mode, status=Session.STATUS_IN_PROGRESS)
        #clear sensor table
        SensorFeed.objects.all().delete()
        return sessionObj



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

        #get all obstacles
        obstacleObjs = Obstacle.objects.all()

        #map refID and Obstacle obj
        
        for obstcaleObj in obstacleObjs:
            self.RF_ID_OBSTACLE_MAP[obstcaleObj.start_rf_id] = obstcaleObj
    
        print(self.RF_ID_OBSTACLE_MAP)
        while(True):
            readRFID = rf_id_helper.getInputFromRFID(rfid)
            if len(readRFID) == 16 and self.RF_ID_OBSTACLE_MAP[readRFID]:
                self.CURRENT_RF_ID = readRFID
                self.COLLECT_SENSOR_INPUTS = True

    
    def readSTMInputs(self):
        """
        reads STM for sensor inputs when READ_STM_FLAG is True
        """
        print('port before')
        arduino = serial.Serial(port='/dev/ttyACM0',  baudrate=115200,parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0.001 )
        once = True
        print('port init')
        lastSensorFeed = []

        while True:
            print('waiting for input')
            if arduino.in_waiting and self.COLLECT_SENSOR_INPUTS:
                data = arduino.readline().decode('utf-8').split(',')

                if data != lastSensorFeed:
                    ObstacleObj = self.RF_ID_OBSTACLE_MAP[self.CURRENT_RF_ID]
                    SensorFeed.objects.create(Obstacle=ObstacleObj, s1=data[0], s2=data[1], s3=data[2], s4=data[3],\
                                              s5=data[4], s6=data[5], s7=data[6], s8=data[7], s9=data[8], s10=data[9],\
                                            s11=data[10],s12=data[11], s13=data[12], s14=data[13], s15=data[14], s16=data[15],\
                                            s17=data[16], s18=data[17], s19=data[18])
                    lastSensorFeed = data

