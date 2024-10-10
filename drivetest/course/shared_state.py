import subprocess
import logging
logger = logging.getLogger("reportLog")

running_process = None

def set_running_process(process):
    global running_process
    logger.info('Setting running process: %s', process.pid if process else 'None')
    running_process = process
    logger.info('Current running process after setting: %s', running_process)


def terminate_process():
    global running_process
    logger.info("Current running process: %s", running_process)
    if running_process:
        poll_result = running_process.poll()
        logger.info("Process poll result: %s", poll_result)
        if poll_result is None:
            running_process.terminate()
            logger.info("Process terminated")
            try:
                running_process.wait(timeout=5)
                logger.info("Process terminated gracefully")
            except subprocess.TimeoutExpired:
                logger.info("Process killed due to timeout")
                running_process.kill()  # Forcefully kill the process
        else:
            logger.info("Process is already terminated or finished")
    else:
        logger.info("No running process to terminate")
