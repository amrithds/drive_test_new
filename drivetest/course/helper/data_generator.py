import time
import os

class DataGenerator():
    RFID = 0
    STM = 1

    @classmethod
    def RFIDGenerator(cls):
        rfIds = ['dsadsadsadsadsad'
                 ,'ffffffffffffffff'
                 ,'sdadasdadasdadaa'
                 ,'sdadasdadasdadab']

        for rfId in rfIds:
            yield rfId
            time.sleep(15)

    @classmethod
    def STMGenerator(cls):
        STMInputs = [
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,31,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,32,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,33,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,34,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,35,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,36,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,37,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,38,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,39,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,40,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,41,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,42,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        ]
        for i in range(len(STMInputs)):
            yield STMInputs[i]
            time.sleep(2)


def read_rf_id_mock():
    f = open(os.path.dirname(os.path.realpath(__file__))+"/rf_id.txt", "r")
    return f.read()