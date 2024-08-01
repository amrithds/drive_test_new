import django
django.setup()
from course.helper import start_session_helper
from course.models.obstacle_session_tracker import ObstacleSessionTracker
import copy
from course.models.session import Session
from django.conf import settings
from django.core.cache import cache
from course.helper import rf_id_helper
from course.helper.data_generator import read_rf_id_mock
import logging
RF_logger = logging.getLogger("RFLog")

def vehicle_location_sensor(session: Session):
    """
    reads RF ID contineously for changes and next RF ID
    """
    
    try:
        
        RF_logger.info('Init RFID reader')
        #get all obstacles
        RF_ID_OBSTACLE_MAP = start_session_helper.get_obstacle_mapping()
        
        #init
        RF_ID_reader = rf_id_helper.RFIDReader()
        OSTracker = None
        
        while(True):
            readRFID = RF_ID_reader.getInputFromRFID()
            
            #     #use for testing without RF_ID
            #     """
            #     # look  course.helper.data_generator import read_rf_id_mock
            #     # paste rf_id string in rf_id.txt
            #     """
            #readRFID = read_rf_id_mock()
            
            #uppercase
            readRFID = readRFID.upper()
            if len(readRFID) == 16:
                CURRENT_REF_ID = cache.get('CURRENT_REF_ID', None)
                
                if readRFID in RF_ID_OBSTACLE_MAP:
                    
                    tempObstacleObj = RF_ID_OBSTACLE_MAP[readRFID]
                    print(readRFID, CURRENT_REF_ID, tempObstacleObj)
                    cache.set('CURRENT_REF_ID', readRFID)
                    cache.set('COLLECT_SENSOR_INPUTS', True)
                    #create ObstacleSessionTracker
                    if OSTracker is None or OSTracker.obstacle_id != tempObstacleObj.id:
                        #play training audio
                        if session.mode == Session.MODE_TRAINING:
                            cache.set('AUDIO_FILE', str(settings.MEDIA_ROOT)+str(tempObstacleObj.audio_file))
                        
                        previousOSTracker = copy.deepcopy(OSTracker)
                        OSTracker,_ = ObstacleSessionTracker.objects.get_or_create(obstacle=tempObstacleObj\
                                                                    ,session=session)
                        
                        #check if start RFID of next obstacle is read before reading previous
                        #obstacles end RFID, then mark previous obstacle as completed
                        if previousOSTracker is not None and previousOSTracker.status == ObstacleSessionTracker.STATUS_IN_PROGRESS:
                            previousOSTracker.status = ObstacleSessionTracker.STATUS_COMPLETED
                            previousOSTracker.save()
                        
                elif CURRENT_REF_ID in RF_ID_OBSTACLE_MAP:
                    tempObstacleObj = RF_ID_OBSTACLE_MAP[CURRENT_REF_ID]
                    if tempObstacleObj.end_rf_id.upper() == readRFID:
                        print("end", readRFID)
                        cache.set('COLLECT_SENSOR_INPUTS', False)
                        OSTracker.status = ObstacleSessionTracker.STATUS_COMPLETED
                        OSTracker.save()
    except Exception as e:
        RF_logger.exception(e)