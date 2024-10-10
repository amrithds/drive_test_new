import os
import serial
import logging
RF_logger = logging.getLogger("RFLog")


def open_serial_port():
    try:
        ser = serial.Serial('/dev/serial0', 9600, timeout=1)
        RF_logger.info("Connected to /dev/serial0")
        return ser
    except serial.SerialException as e:
        RF_logger.info(f"Could not open port: {e}")
        return None

def read_from_serial(ser, max_lines=10):
    line_count = 0
    try:
        while True:
            try:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8', errors='replace').rstrip()
                    if line:
                        # Write to file and increase line count
                        with open('output.txt', 'a', encoding='utf-8') as f:
                            f.write(f"{line}\n")
                        line_count += 1
                        
                        # Check if we have written enough lines to clear the file
                        if line_count >= max_lines:
                            # Clear the file
                            open('output.txt','w').close()
                            line_count = 0  # Reset line count

            except Exception as e:
                print(f"Error reading from serial port: {e}")
                ser.close()
                ser = open_serial_port()
                if ser is None:
                    print("Failed to reconnect. Exiting.")
                    break
    except Exception as e:
        print(f"Error handling file: {e}")

ser = open_serial_port()
if ser is not None:
    read_from_serial(ser)
else:
    print("No valid serial port found. Exiting.")
