import binascii
import serial
from singleton_decorator import singleton
import os

@singleton
class RFIDReader():
    def __init__(self) -> None:
        try:
            self.port = '/dev/serial0'
            self.__createConnection()
        except serial.SerialException as e:
            print(f"Could not open port {self.port}: {e}")

    def getInputFromRFID(self, brand=None):
        """getInputFromRFID

        Args:
            rfid (_type_): rfid port object
            brand (_type_): Optional

        Returns:
            _type_: string
        """
        hex_string = ''
        try:
            if brand=='RADICAL' :
                s = self.RF_ID_port.readline()
                hex_string=s.decode('utf-8','ignore')[1:].strip()
            else:
                if self.RF_ID_port.in_waiting > 0:
                    hex_string = self.RF_ID_port.readline().decode('utf-8', errors='replace').strip()
                else:
                    hex_string = ''
        except Exception as e:
            print(f"Error reading from serial port: {e}")
            self.__createConnection()

        return hex_string
        
    def __createConnection(self):
        user = os.environ.get('USER')
        command = f"sudo chown {user}:{user} {self.port}"
        os.system(command)
        self.RF_ID_port = serial.Serial(self.port, 9600, timeout=1)
        print(f"Connected to {self.port}")