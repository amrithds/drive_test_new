#!/usr/bin/env python3

import serial
import binascii
import re
import mysql.connector as mariadb
import sys
import time
import os


sdtpid=os.getpid()


rfid = serial.Serial( 
        port='/dev/ttyUSB0',    
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=.01
    )

#aurdino = serial.Serial(         port='/dev/ttyACM1',  baudrate=115200,parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=.01 )

def Database():
        global conn, cursor
        conn = mariadb.connect(host="localhost",user="root",password='F2s@btm2',database="sensors" )
        cursor = conn.cursor()

Database()
sql="update display_rfid_data set pid="+ str(sdtpid)
cursor.execute(sql)
conn.commit()
a=1
while(rfid.is_open == True):
    
    s = rfid.read(8)
    
    hex_string= binascii.hexlify(s).decode('utf-8')
    #print(hex_string)
    if len(hex_string.upper())==16 :
       sql="update display_rfid_data set rfid='"+ hex_string.upper()+"'"
       print(hex_string)
       cursor.execute(sql)
       conn.commit()
       
    
