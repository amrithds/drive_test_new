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
from app_config.models import Config
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
            input_from_rfid = RF_ID_reader.getInputFromRFID()

            if input_from_rfid == '':
                continue
            #     #use for testing without RF_ID
            #     """
            #     # look  course.helper.data_generator import read_rf_id_mock
            #     # paste rf_id string in rf_id.txt
            #     """
            #readRFID = read_rf_id_mock()
            
            #uppercase
            input_from_rfid = input_from_rfid.upper()

            readRFID, distance = parse_rf_id(input_from_rfid)
            RF_logger.info(f'readRFID: {readRFID}, distance: {distance}')
            if len(readRFID) >= 3:
                update_distance_cache(readRFID, distance)
                CURRENT_REF_ID = cache.get('CURRENT_REF_ID', None)
                
                if readRFID in RF_ID_OBSTACLE_MAP:
                    
                    tempObstacleObj = RF_ID_OBSTACLE_MAP[readRFID]
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


def parse_rf_id(input_from_rfid):
    parsed_values = input_from_rfid.split(',')
    readRFID = ''
    distance = 0
    if len(parsed_values) == 2:
        distance = int(parsed_values[1].strip())
        readRFID = str(parsed_values[0].strip())
    return readRFID, distance

def update_distance_cache(sensor_node,distance):
    def update_sensor_cache(sensor_type):
        """
        Updates cache for a specific sensor type (LEFT, RIGHT, or BACK)
        Args:
            sensor_type (str): The type of sensor (LEFT, RIGHT, or BACK)
        """
        cache_key = f'{sensor_type}_DISTANCE_SENSORS'
        if cache.get(cache_key, None) is not None:
            sensor = Config.objects.filter(name=cache_key).first()
            if sensor:
                sensor_values = tuple(sensor.value.split(','))
                cache.set(cache_key, sensor_values)
    
    # update left distance cache if cache is not set
    if cache.get('LEFT_DISTANCE_SENSORS', None) is not None:
        update_sensor_cache('LEFT')
    if cache.get('RIGHT_DISTANCE_SENSORS', None) is not None:
        update_sensor_cache('RIGHT')
    if cache.get('BACK_DISTANCE_SENSORS', None) is not None:
        update_sensor_cache('BACK')
    
    # update distance cache based on sensor node
    if sensor_node in cache.get('LEFT_DISTANCE_SENSORS'):
        cache.set('LEFT_DISTANCE', distance)
    elif sensor_node in cache.get('RIGHT_DISTANCE_SENSORS'):
        cache.set('RIGHT_DISTANCE', distance)
    elif sensor_node in cache.get('BACK_DISTANCE_SENSORS'):
        cache.set('BACK_DISTANCE', distance)
        