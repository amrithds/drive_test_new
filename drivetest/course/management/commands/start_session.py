from django.core.management.base import BaseCommand
from course.models.session import Session
from course.models.obstacle import Obstacle
from drivetest.report.models.sensor_feed import SensorFeed
from course.models.obstacle_session_tracker import ObstacleSessionTracker
from course.helper import start_session_helper
from course.helper.report_generator import ReportGenerator
from course.helper import rf_id_helper
from course.helper.STM_helper import STMReader
import copy
import concurrent.futures


import logging
RF_logger = logging.getLogger("RFlog")

sensor_logger = logging.getLogger("sensorLog")
report_logger = logging.getLogger("reportLog")

class Command(BaseCommand):
    help = 'Start a session, listen to inputs'
    # global variables
    CURRENT_RF_ID=None
    COLLECT_SENSOR_INPUTS=False
    RF_ID_OBSTACLE_MAP = {}
    SESSION = None
    
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
        resume = kwargs['resume']
        
        #session_id is optional during debug
        if kwargs["session_id"]:
            self.SESSION = Session.objects.get(id=kwargs["session_id"])
        else:
            self.SESSION = start_session_helper.createSession(trainer_id, trainee_id,session_mode, course_id)
        
        if not resume:
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
        try:
            report_generotor = ReportGenerator(self.SESSION)
            report_generotor.generateReport()
        except Exception as e:
            report_logger.exception("Error: "+str(e))

    def readRFIDInputs(self):
        """
        reads RF ID contineously for changes and next RF ID
        """
        try:
            
            print('Init RFID reader')
            #get all obstacles
            obstacleObjs = Obstacle.objects.all()

            #map refID and Obstacle obj
            for obstcaleObj in obstacleObjs:
                self.RF_ID_OBSTACLE_MAP[obstcaleObj.start_rf_id.upper()] = obstcaleObj
            
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

                        self.CURRENT_RF_ID = readRFID
                        self.COLLECT_SENSOR_INPUTS = True
                        #create ObstacleSessionTracker
                        if OSTracker is None or OSTracker.obstacle_id != tempObstacleObj.id:
                            previousOSTracker = copy.deepcopy(OSTracker)
                            OSTracker = ObstacleSessionTracker.objects.create(obstacle=tempObstacleObj\
                                                                        ,session=self.SESSION)
                            
                            #check if start RFID of next obstacle is read before reading previous
                            #obstacles end RFID, then mark previous obstacle as completed
                            if previousOSTracker is not None and previousOSTracker.status == ObstacleSessionTracker.STATUS_IN_PROGRESS:
                                previousOSTracker.status = ObstacleSessionTracker.STATUS_COMPLETED
                                previousOSTracker.save()
                            
                    elif self.CURRENT_RF_ID in self.RF_ID_OBSTACLE_MAP:
                        tempObstacleObj = self.RF_ID_OBSTACLE_MAP[self.CURRENT_RF_ID]
                        if tempObstacleObj.end_rf_id.upper() == readRFID:
                            print("end", readRFID)
                            self.COLLECT_SENSOR_INPUTS = False
                            OSTracker.status = ObstacleSessionTracker.STATUS_COMPLETED
                            OSTracker.save()
        except Exception as e:
            RF_logger.error("Error: "+str(e))
    
    def readSTMInputs(self):
        """
        reads STM for sensor inputs when READ_STM_FLAG is True
        """
        try:
            print('Init STM reader')
            STM_reader = STMReader()
            #STMreader =  DataGenerator.STMGenerator()
            lastSensorFeed = []
            
            while True:
                #if self.COLLECT_SENSOR_INPUTS:
                    # data = next(STMreader)
                    # print(self.COLLECT_SENSOR_INPUTS)
                    # print(data)
                if STM_reader.dataWaiting() and self.COLLECT_SENSOR_INPUTS:
                    data = STM_reader.getSTMInput()
                    print(data)
                    # conside data less than 19 as noise
                    if len(data) == 19 and data != lastSensorFeed and self.CURRENT_RF_ID in self.RF_ID_OBSTACLE_MAP:

                        ObstacleObj = self.RF_ID_OBSTACLE_MAP[self.CURRENT_RF_ID]

                        SensorFeed.objects.create(obstacle=ObstacleObj, s0=data[1], s1=data[2], s2=data[3], s3=data[4],\
                                                s4=data[5], s5=data[6], s6=data[7], s7=data[8], s8=data[9], s9=data[10],\
                                                s10=data[11],s11=data[12], s12=data[13], s13=data[14], s14=data[15], s15=data[16],\
                                                s16=data[17] )

                        lastSensorFeed = data
        except Exception as e:
            sensor_logger.exception('Error: '+str(e))
