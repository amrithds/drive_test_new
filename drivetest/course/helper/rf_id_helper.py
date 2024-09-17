import binascii
import serial
from singleton_decorator import singleton

@singleton
class RFIDReader():
    def __init__(self) -> None:
        self.RF_ID_port = rfid = serial.Serial(
                port='/dev/ttyUSB0',
                baudrate=115200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=.01
            )

    def getInputFromRFID(self, brand=None):
        """getInputFromRFID

        Args:
            rfid (_type_): rfid port object
            brand (_type_): Optional

        Returns:
            _type_: string
        """
        hex_string = ''
        
        if brand=='RADICAL' :
            s = self.RF_ID_port.readline()
            hex_string=s.decode('utf-8','ignore')[1:].strip()
        else:
            s = self.RF_ID_port.read(8)
            hex_string= binascii.hexlify(s).decode('utf-8')
        return hex_string