import binascii
import serial
from singleton_decorator import singleton
import os

@singleton
class RFIDReader():
    def __init__(self, port=None) -> None:
        """Supports /dev/serial0 and /dev/ttyUSB0 port connections

        Args:
            port (str, optional): _description_. Defaults to None.
        """
        try:
            if port is None:
                port = '/dev/ttyUSB0'
            
            self.RF_ID_port = None
            self.port = port
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
            if self.port=='/dev/serial0' :
                if self.RF_ID_port.in_waiting > 0:
                    hex_string = self.RF_ID_port.readline().decode('utf-8', errors='replace').strip()
                else:
                    hex_string = ''
            else:
                s = self.RF_ID_port.read(8)
                hex_string= binascii.hexlify(s).decode('utf-8')
        except Exception as e:
            print(f"Error reading from serial port: {e}")
            self.__createConnection()

        return hex_string
        
    def __createConnection(self):
        """
        serial port and ttyUSB port connection
        """
        if self.port == '/dev/ttyUSB0':
            self.RF_ID_port = rfid = serial.Serial(
                port=self.port,
                baudrate=115200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=.01
            )
        else:
            user = os.environ.get('USER')
            command = f"sudo chown {user}:{user} {self.port}"
            os.system(command)
            self.RF_ID_port = serial.Serial(self.port, 9600, timeout=1)
        
        print(f"Connected to {self.port}")