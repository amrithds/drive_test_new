import serial
class STMReader():
    def __init__(self) -> None:
        self.arduino_port = self.connect_STM_reader()


    def connect_STM_reader(self):
        return serial.Serial(port='/dev/ttyACM0',  baudrate=115200,parity=serial.PARITY_NONE, \
                                      stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0.001)

    def dataWaiting(self) -> bool:
        try:
            return self.arduino_port.in_waiting
        except Exception as e:
            self.arduino_port = self.connect_STM_reader()
    
    def getSTMInput(self):
        """Read stm inputs

        Returns:
            _type_: _description_
        """
        return self.arduino_port.readline().decode('utf-8').split(',')