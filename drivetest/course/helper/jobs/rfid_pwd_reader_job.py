import django
django.setup()
import threading
from course.helper import start_session_helper
from course.models.obstacle_session_tracker import ObstacleSessionTracker
from course.models.obstacle_task_score import ObstacleTaskScore
from course.models.task import Task 
import copy
from course.models.session import Session
from django.conf import settings
from django.core.cache import cache
import logging
RF_logger = logging.getLogger("RFLog")
from report.helper import report_helper
import shlex
import subprocess
import time
import re
import ast

running_process = None
def start_subprocess(script_path, python_path):
    global running_process
    command = shlex.split(f'sudo {python_path} {script_path}')
    while True:
        running_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(10)
        if running_process.poll() is not None:
            RF_logger.info("Process terminated")
            break

def process_sensor_data(session, RF_ID_OBSTACLE_MAP):
    distance_ip = []
    OSTracker = None
    try:
        while True:
            lines = read_lines_from_file()
            if lines:
                for line in lines:
                    parts = line.split('=')
                    if len(parts) != 2:
                        RF_logger.error(f"Unexpected line format: {line}")
                        continue

                    left_part = parts[0].strip()
                    right_part = parts[1].strip()
                    left_numbers = left_part.split(':')

                    if len(left_numbers) != 2:
                        continue

                    distance = left_numbers[1].strip()
                    readRFID = right_part.strip()
                    RF_logger.info(f"readRFID: {readRFID}, distance: {distance}")

                    CURRENT_REF_ID = cache.get('CURRENT_REF_ID', None)

                    if readRFID in RF_ID_OBSTACLE_MAP:
                        print("start id triggered")
                        tempObstacleObj = RF_ID_OBSTACLE_MAP[readRFID]
                        cache.set('CURRENT_REF_ID', readRFID)
                        cache.set('COLLECT_SENSOR_INPUTS', True)

                        ObsTaskScores = ObstacleTaskScore.objects.filter(obstacle_id=tempObstacleObj.id)
                        for obs_task_score in ObsTaskScores:
                            if obs_task_score.task.category not in Task.BOOLEAN_TASKS and obs_task_score.ip_address != '0':
                                distance_ip = ast.literal_eval(obs_task_score.ip_address)

                        if OSTracker is None or OSTracker.obstacle_id != tempObstacleObj.id:
                            if session.mode == Session.MODE_TRAINING:
                                cache.set('AUDIO_FILE', str(settings.MEDIA_ROOT) + str(tempObstacleObj.audio_file))

                            previousOSTracker = copy.deepcopy(OSTracker)
                            OSTracker, _ = ObstacleSessionTracker.objects.get_or_create(obstacle=tempObstacleObj, session=session)

                            if previousOSTracker is not None and previousOSTracker.status == ObstacleSessionTracker.STATUS_IN_PROGRESS:
                                previousOSTracker.status = ObstacleSessionTracker.STATUS_COMPLETED
                                previousOSTracker.save()

                    if len(distance_ip) > 0:
                        if readRFID == distance_ip[0]:
                            cache.set('S0', distance)
                        elif readRFID == distance_ip[1]:
                            cache.set('S1', distance)
                        elif readRFID == distance_ip[2]:
                            cache.set('S10', distance)

            else:
                RF_logger.info("No data found in the file")
            time.sleep(1)

    except Exception as e:
        RF_logger.error(f"An unexpected error occurred: {e}")

def vehicle_location_sensor(session):
    global running_process

    try:
        with open('output.txt', 'w', encoding='utf-8') as f:
            pass  
        RF_logger.info('Init RFID PWD reader')

        
        RF_ID_OBSTACLE_MAP = start_session_helper.get_obstacle_mapping()

        
        script_path = '/home/super/driving_project/drive_test/drivetest/NRF24L01/transm.py'
        python_path = '/home/super/driving_project/drive_test/venv/bin/python3'

        
        subprocess_thread = threading.Thread(target=start_subprocess, args=(script_path, python_path))
        sensor_thread = threading.Thread(target=process_sensor_data, args=(session, RF_ID_OBSTACLE_MAP))

        
        subprocess_thread.start()
        sensor_thread.start()

        
        subprocess_thread.join()
        sensor_thread.join()

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

