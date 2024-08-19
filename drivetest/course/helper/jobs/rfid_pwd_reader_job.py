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
from NRF24L01.transm import read_from_serial
from NRF24L01.transm import open_serial_port
from report.helper import report_helper

def vehicle_location_sensor(session: Session):
    try:
        print('Init RFID PWD reader')
        #get all obstacles
        RF_ID_OBSTACLE_MAP = start_session_helper.get_obstacle_mapping()
        OSTracker = None
        ser = open_serial_port()
        if ser is not None:
            while(True):
                data = read_from_serial(ser)
                print("data",data)
                data = data.split(" : ")
                readRFID = data[0]
                distance = data[1]
                cache.set('DISTANCE', distance)
                CURRENT_REF_ID = cache.get('CURRENT_REF_ID', None)
                if readRFID in RF_ID_OBSTACLE_MAP:
                    tempObstacleObj = RF_ID_OBSTACLE_MAP[readRFID]
                    cache.set('CURRENT_REF_ID', readRFID)
                    cache.set('COLLECT_SENSOR_INPUTS', True)
                    if OSTracker is None or OSTracker.obstacle_id != tempObstacleObj.id:
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

                        if tempObstacleObj.end_rf_id == report_helper.get_obstacle_duration(tempObstacleObj.id):
                            cache.set('COLLECT_SENSOR_INPUTS', False)
                            OSTracker.status = ObstacleSessionTracker.STATUS_COMPLETED
                            OSTracker.save()

        else:
            print("No valid serial port found. Exiting.")
                
    except Exception as e:
        RF_logger.exception(e)
