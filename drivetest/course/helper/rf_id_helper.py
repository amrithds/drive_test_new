import binascii
import serial
from singleton_decorator import singleton

@singleton
class RFIDReader():
    def __init__(self) -> None:
        try:
            port = '/dev/serial0'
            self.RF_ID_port = serial.Serial(port, 9600, timeout=1)
            print(f"Connected to {port}")
        except serial.SerialException as e:
            print(f"Could not open port {port}: {e}")

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
            if self.RF_ID_port.in_waiting > 0:
                hex_string = self.RF_ID_port.readline().decode('utf-8', errors='replace').strip()
            else:
                hex_string = ''
        return hex_string