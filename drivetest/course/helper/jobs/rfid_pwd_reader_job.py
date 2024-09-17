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
from report.helper import report_helper
import shlex
import subprocess
import time
import re

running_process = None

def vehicle_location_sensor(session: Session):
    global running_process
    try:
        print('Init RFID PWD reader')
        # Get all obstacles
        RF_ID_OBSTACLE_MAP = start_session_helper.get_obstacle_mapping()
        OSTracker = None

        script_path = '/home/admin/driving_project/drivetest/NRF24L01/transm.py'
        python_path = '/home/admin/driving_project/venv/bin/python3'
        command = shlex.split(f'sudo {python_path} {script_path}')
        
        # Start the subprocess and set the global variable
        running_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        try:
            while True:
                if running_process.poll() is not None:
                    print("Process terminated")
                    break

                lines = read_lines_from_file()
                if lines:
                    for line in lines:
                        #print(line)
                        data = line.split(" : ")
                        #print("data",data)

                        if len(data) == 2:
                            readRFID = extract_number(data[0])
                            distance = data[1].strip()
                            print("readRFID", readRFID)
                            #print("distance", distance)
                            
                            # Update cache with distance
                            cache.set('DISTANCE', distance)
                            CURRENT_REF_ID = cache.get('CURRENT_REF_ID', None)

                            if readRFID in RF_ID_OBSTACLE_MAP:
                                tempObstacleObj = RF_ID_OBSTACLE_MAP[readRFID]
                                cache.set('CURRENT_REF_ID', readRFID)
                                cache.set('COLLECT_SENSOR_INPUTS', True)

                                # Check if obstacle has changed
                                if OSTracker is None or OSTracker.obstacle_id != tempObstacleObj.id:
                                    if session.mode == Session.MODE_TRAINING:
                                        cache.set('AUDIO_FILE', str(settings.MEDIA_ROOT) + str(tempObstacleObj.audio_file))

                                    previousOSTracker = copy.deepcopy(OSTracker)
                                    OSTracker, _ = ObstacleSessionTracker.objects.get_or_create(
                                        obstacle=tempObstacleObj,
                                        session=session
                                    )

                                    # Mark the previous obstacle as completed if needed
                                    if previousOSTracker is not None and previousOSTracker.status == ObstacleSessionTracker.STATUS_IN_PROGRESS:
                                        previousOSTracker.status = ObstacleSessionTracker.STATUS_COMPLETED
                                        previousOSTracker.save()

                                    # Check obstacle end RFID
                                    if report_helper.get_obstacle_duration(tempObstacleObj.id)!=None and int(tempObstacleObj.end_rf_id) >= report_helper.get_obstacle_duration(tempObstacleObj.id):
                                        cache.set('COLLECT_SENSOR_INPUTS', False)
                                        OSTracker.status = ObstacleSessionTracker.STATUS_COMPLETED
                                        OSTracker.save()

                else:
                    RF_logger.info("No data found in the file")
                time.sleep(1)
        
        except Exception as e:
            RF_logger.error(f"An unexpected error occurred: {e}")

        finally:
            # Ensure the process is terminated
            if running_process and running_process.poll() is None:
                RF_logger.info("Terminating the process...")
                running_process.terminate()  # Attempt a soft termination
                try:
                    running_process.wait(timeout=5)  # Wait up to 5 seconds for termination
                except subprocess.TimeoutExpired:
                    RF_logger.info("Process did not terminate in time. Killing the process...")
                    running_process.kill()  # Forcefully kill the process
                    running_process.wait()  # Wait for the process to exit
            RF_logger.info("Subprocess terminated.")
    
    except Exception as e:
        RF_logger.error(f"An unexpected error occurred: {e}")

def read_lines_from_file(filename='output.txt'):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:
                    yield line
    except FileNotFoundError:
        RF_logger.error(f"File '{filename}' not found.")
    except IOError as e:
        RF_logger.error(f"An error occurred while reading the file: {e}")


def extract_number(s):
    s = s.strip()
    if s.isdigit():
        return s
    match = re.search(r'\d+', s)
    if match:
        return match.group()
    return None
