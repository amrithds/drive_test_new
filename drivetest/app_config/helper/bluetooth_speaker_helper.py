import os
from app_config.models import Config
def connect_bluetooth():
    config_obj = Config.objects.get(name='bluetooth speaker')
    os.system('bluetoothctl power on |   bluetoothctl connect '+ config_obj.value)
