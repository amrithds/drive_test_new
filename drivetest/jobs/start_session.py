import serial


rfid = serial.Serial(         port='/dev/ttyUSB0',  baudrate=115200,parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=.01 )
Arduino = serial.Serial(         port='/dev/ttyACM0',  baudrate=115200,parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0.001 )

print(rfid)
print(Arduino)