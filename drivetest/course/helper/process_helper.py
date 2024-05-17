import psutil

def is_process_active(pid) -> bool:
    """check if process is active

    Args:
        pid (_type_): process id

    Returns:
        bool:
    """
    try:
        process = psutil.Process(pid)
    except psutil.Error as error:  # includes NoSuchProcess error
        return False
    if psutil.pid_exists(pid) and process.status() not in (psutil.STATUS_DEAD, psutil.STATUS_ZOMBIE):
        return True
    return False

def stop_process(pid) -> bool:
    """Terminate a process

    Args:
        pid (_type_): _description_

    Returns:
        bool: _description_
    """
    try:
        p = psutil.Process(pid)
        p.terminate()
    except Exception as e:
        return False