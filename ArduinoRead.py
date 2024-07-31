#!/usr/bin/env python3

import serial
import binascii
import re
import mysql.connector as mariadb
import sys
import time
import os

arduino_port = serial.Serial(         port='/dev/ttyACM0',  baudrate=115200,parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0.001 )
while True:
    if arduino_port.in_waiting:
        print(arduino_port.readline().decode('utf-8').split(','))
                
        
