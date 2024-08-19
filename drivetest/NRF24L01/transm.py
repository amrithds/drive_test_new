import serial
import time

# List of potential serial ports
ports = ['/dev/ttyS0', '/dev/ttyAMA0', '/dev/ttyUSB0']

def open_serial_port():
    for port in ports:
        try:
            ser = serial.Serial(port, 9600, timeout=1)
            print(f"Connected to {port}")
            return ser
        except serial.SerialException as e:
            print(f"Could not open port {port}: {e}")
    return None

# Function to read from the serial port with error handling
def read_from_serial(ser):
    while True:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                #print(f"Received: {line}")
                return line  # Return the data read from the serial port
        except Exception as e:
            print(f"Error reading from serial port: {e}")
            ser.close()
            ser = open_serial_port()
            if ser is None:
                print("Failed to reconnect. Exiting.")
                break

