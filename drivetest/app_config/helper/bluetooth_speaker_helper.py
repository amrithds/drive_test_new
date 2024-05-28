import os
from app_config.models import Config
def connect_bluetooth() -> bool:
    config_obj = Config.objects.filter(name='bluetooth speaker').first()
    if config_obj:
        os.system('bluetoothctl power on | bluetoothctl pairable on | bluetoothctl pair '+ config_obj.value)
        return True

    return False
