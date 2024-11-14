import django
django.setup()
from course.helper import start_session_helper
from report.models.sensor_feed import SensorFeed
from course.helper.STM_helper import STMReader
from django.core.cache import cache

import logging

sensor_logger = logging.getLogger("sensorLog")
def readSTMInputs():
    """
    reads STM for sensor inputs when READ_STM_FLAG is True
    """
    try:
        sensor_logger.info('Init STM reader')
        STM_reader = STMReader()
        #STMreader =  DataGenerator.STMGenerator()
        lastSensorFeed = []
        RF_ID_OBSTACLE_MAP = start_session_helper.get_obstacle_mapping()
        while True:
            #if self.COLLECT_SENSOR_INPUTS:
                # data = next(STMreader)
                # print(self.COLLECT_SENSOR_INPUTS)
                # print(data)
            
            if cache.get('COLLECT_SENSOR_INPUTS'):
                if STM_reader.dataWaiting():
                    data = STM_reader.getSTMInput()
                    CURRENT_REF_ID = cache.get('CURRENT_REF_ID')
                    
                    sensor_logger.info(data)
                    # conside data less than 19 as noise
                    if len(data) == 19 and data != lastSensorFeed and CURRENT_REF_ID in RF_ID_OBSTACLE_MAP:

                        ObstacleObj = RF_ID_OBSTACLE_MAP[CURRENT_REF_ID]

                        SensorFeed.objects.create(obstacle=ObstacleObj, s0=data[1], s1=data[2], s2=data[3], s3=data[4],\
                                                s4=data[5], s5=data[6], s6=data[7], s7=data[8], s8=data[9], s9=data[10],\
                                                s10=data[11],s11=data[12], s12=data[13], s13=data[14], s14=data[15], s15=data[16],\
                                                s16=data[17] )

                        lastSensorFeed = data
    except Exception as e:
        sensor_logger.exception('Error: '+str(e))