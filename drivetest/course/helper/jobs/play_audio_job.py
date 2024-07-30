from pwd import getpwnam
import pwd
import os
from django.core.cache import cache

import logging
report_logger = logging.getLogger("reportLog")

def playAudio():
    last_played = None
    
    while True:
        try:
            AUDIO_FILE = cache.get('AUDIO_FILE')
            if AUDIO_FILE != last_played:
                
                user = pwd.getpwuid(os.getuid())[0]
                uid = getpwnam(user).pw_uid
                
                os.system(f'XDG_RUNTIME_DIR=/run/user/{uid} mpg321 {AUDIO_FILE}')
                last_played = AUDIO_FILE
        except Exception as e:
            report_logger.exception("Error: "+str(e))