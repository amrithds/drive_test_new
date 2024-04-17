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
        # sessionWorkflowThread = threading.Thread(target=self.sessionWorkflow())

        #active obstacle
        currentObstacle = None
        # flag for start/stop collecting sessor inputs
        collect_sessor = False

        # #while(rfid.is_open == True):
        
        #         #if a start rfid is read
        #         if rfIDObstacleMap[readRFID]:
        #             currentObstacle = rfIDObstacleMap[readRFID]

        #     #getInputFromRFID(rfid, "RADICAL")
        
            # print(currentObstacle)

        
        # time = timezone.now().strftime('%X')
        # self.stdout.write("It's now %s" % time)
    
    def initialiseSession(self, trainerID, traineeID, session_mode ):
        trainer = User.objects.get(id=trainerID)
        trainee = User.objects.get(id=traineeID)
        #update session with in progress status
        sessionObj = Session.objects.create(trainer_no=trainer, trainee_no=trainee, mode=session_mode, status=Session.STATUS_IN_PROGRESS)
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
        rfIDObstacleMap = {}
        for obstcaleObj in obstacleObjs:
            rfIDObstacleMap[obstcaleObj.start_rf_id] = {'object': obstcaleObj, "collect_sessor": False}
    

        while(True):
            readRFID = rf_id_helper.getInputFromRFID(rfid)
            if len(readRFID) == 16 and rfIDObstacleMap[readRFID]:
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
        while True:
            if once:
                print(self.CURRENT_RF_ID, self.COLLECT_SENSOR_INPUTS)
                once=False
            if arduino.in_waiting and self.COLLECT_SENSOR_INPUTS:
                data = arduino.readline().decode('utf-8').split(',')
                print(data)
                print('-------')
