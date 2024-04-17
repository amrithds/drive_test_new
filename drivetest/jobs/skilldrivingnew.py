#!/usr/bin/env python3

import serial
import binascii
import re
import mysql.connector as mariadb
import sys
import time
import os
import resetArduino as rst






#trainer1 = sys.argv[1]
#trainee1=sys.argv[2]
#obschk=sys.argv[3].upper()



global myMode,mySpeaker,gearstart,gear_stat ,Check,pp0,pp1,pp2,pp3,pp4,pp5,pp6,pp7,pp8,prv_obs_type,obs_type,stat,final_result,obs_no,obstacle_cond,obs_chk_count,obs_end_card,testid,vehicleno,end_obs_card,obs_count,obs_test,obs_cond
global rfidbrand
global time_status,sess_start,gear_start_time,gear_end_time,minGearChange,Live_Status,Mode
minGearChange=1
#trainer1 = 'asas'
#trainee1='1213'
#obschk='29,30'
obs_type=""
t_obs_type=""
prv_obs_type=""
time_status=1
sdtpid=os.getpid()


#print (obstacle_cond)
rfid = serial.Serial(         port='/dev/ttyUSB0',  baudrate=115200,parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=.01 )
Arduino = serial.Serial(         port='/dev/ttyACM0',  baudrate=115200,parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0.001 )
#dis = serial.Serial(         port='/dev/ttyAMA0',  baudrate=115200,parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0.001 )
def delay():
   time.sleep(1)

delay()

global ndata0,ndata1,ndata2

# read_count=15
# read_length=0
# while read_count>0 and read_length==0:
#     ndata0 =aurdino0.readline()
#     read_count=read_count-1
#     read_length=len(ndata0)
#  
# read_count=15
# read_length=0
# while read_count>0 and read_length==0:
#     ndata1=aurdino1.readline()
#     read_count=read_count-1
#     read_length=len(ndata1)
# 
# read_count=15
# read_length=0
# while read_count>0 and read_length==0:
#     ndata2 =aurdino2.readline()
#     read_count=read_count-1
#     read_length=len(ndata2)
# 
# 
# 
# #print(mydata1)
# if len(ndata1) >15 and len(ndata1) <=20:
#     dis=aurdino1
# #print(mydata0)
# if len(ndata0) >15 and len(ndata0) <=20:
#     dis=aurdino0
# #print(mydata2)
# if len(ndata2) >15 and len(ndata2) <=20:
#     dis=aurdino2
# 
# #print(mydata1)
# if len(ndata1) >=20:
#     analog=aurdino1
# #print(mydata0)
# if len(ndata0) >=20:
#     analog=aurdino0
# #print(mydata2)
# if len(ndata2) >=20:
#     analog=aurdino2
#     
# 
# #print(mydata1)
# if len(ndata1) ==0:
#     rfid=aurdino1
# #print(mydata0)
# if len(ndata0) ==0:
#     rfid=aurdino0
# #print(mydata2)
# if len(ndata2) ==0:
#     rfid=aurdino2
    
def Database():
        global conn, cursor
        conn = mariadb.connect(host="localhost",user="root",password='F2s@btm2',database="sensors" )
        cursor = conn.cursor()

Database()
sql="update terminal set sdt_pid="+ str(sdtpid)
cursor.execute(sql)
conn.commit()

sql ="select sess_stat,pid  from ses_start"
cursor.execute(sql)
print (sql)
rows=cursor.fetchone()
if rows is not None:
    session=rows[0]
    print (session)
    if session==1 or session=='1':
        skilldriveMode="Old"
    else :
        skilldriveMode="New"
        sql='delete from mydata_history where test_id=(select max(test_id) from mydata)'
        cursor.execute(sql)
        conn.commit()        
        
        sql="insert into mydata_history select * from mydata"
        cursor.execute(sql)
        conn.commit()
        sql='delete from mydata'
        cursor.execute(sql)
        conn.commit()        
        sql='truncate table mydata'
        cursor.execute(sql)
        conn.commit()


print(skilldriveMode)


sql ="select count(*) cnt from mydata"
cursor.execute(sql)
global myMode,mySpeaker
rows=cursor.fetchone()
if rows is not None:


        sql='select vehicle_no,test_id,live_status,mode,bluetooth_speaker from terminal'
        cursor.execute(sql)
        rows=cursor.fetchone()
        if rows is not None:
                vehicleno=rows[0]
                testid=rows[1]+1
                Live_Status=rows[2]
                myMode=rows[3]
                mySpeaker=rows[4]
                if myMode=='L':
                      os.system('bluetoothctl power on |   bluetoothctl connect ' + mySpeaker)
                sql= 'update terminal set test_id=test_id  '
                cursor.execute(sql)
                conn.commit()

        else:
                print('Pls contact Administrator')
                quit()
                exit()
        print(vehicleno)
        sql="update ses_start set sess_stat=1 ,test_id="+  str(testid)
        cursor.execute(sql)
        conn.commit()
        sql="update terminal set test_id="+  str(testid)
        cursor.execute(sql)
        conn.commit()
      
      
        
        

        sql="select trainer_army_no,trainee_army_no,case when length(obs_list)=0 then 'ALL' else obs_list end,sess_stat from ses_start"
        cursor.execute(sql)
        rows=cursor.fetchone()
        
        if rows is not None:
                trainer1=rows[0]
                trainee1=rows[1]
                obschk=rows[2]
        if obschk=="ALL":
                obstacle_cond=""
        else:
                obstacle_cond=" where slno in (" + obschk +")"        


        
print (trainer1)
print (trainee1)

if Live_Status=='Y':
    sql="delete from livefeed_history where test_id =(SELECT max(a.test_id) FROM `livefeed` a)"
    cursor.execute(sql)
    conn.commit()

    sql="insert into livefeed_history SELECT a.* FROM `livefeed` a"
    cursor.execute(sql)
    conn.commit()
    sql="update livefeed set test_id=" +str(testid) +", TS='',TE='', OBS_1='',OBS_2='',OBS_3='',OBS_4='',OBS_5='',OBS_6='',OBS_7='',OBS_8='',OBS_9='' , OBS_10='' , OBS_11='',OBS_12='',OBS_13='',OBS_14='',OBS_15='',OBS_16='',OBS_17='',OBS_18='',OBS_19='',OBS_20='',OBS_21='',OBS_22='',OBS_23='',OBS_24='',OBS_25='',OBS_26='',OBS_27='',OBS_28='',OBS_29='',OBS_30='',last_obs='',last_init_time=null"
    cursor.execute(sql)
    conn.commit()
    sql="delete from  live_feed_detail_history where test_id= (SELECT max(a.test_id) FROM `live_feed_detail` a)"
    cursor.execute(sql)
    conn.commit()
    sql="insert into live_feed_detail_history SELECT a.* FROM `live_feed_detail` a"
    cursor.execute(sql)
    conn.commit()
    sql="update live_feed_detail set test_id="+ str(testid)+",left_dist='0',right_dist='0',back_dist='0', `left_indicator`='0', `right_indicator`='0', `horn`='0', `left_dist`='0', `right_dist`='0', `back_dist`='0', `parking_light`='0', `break`='0', `hand_break`='0', `exuast_break`='0',dist_nego_status='0'"
    cursor.execute(sql)
    conn.commit()


    ##sql=" select * from traineedetails where trainer_armyid='" + trainer1 + "' and trainee_armyid='" + trainee1 + "' and test_id="+ str(testid)
    ##print(sql)
    ##cursor.execute(sql)
    ##rows=cursor.fetchone()
    ##if rows is  None:
    ##        sql="insert into traineedetails (trainer_armyid,trainee_armyid,test_id) values ('" + trainer1 + "','" + trainee1 +"',"+ str(testid) +")"
    ##        cursor.execute(sql)
    ##        conn.commit()
sql="update traineedetails set test_id="+  str(testid) + "  where test_id=0 "
cursor.execute(sql)
conn.commit()

#rst.reset()

print("Hello World!")


def ini_data():
        global rfidbrand,myMode,mySpeaker,gearstart,gear_stat,Check,pp0,pp1,pp2,pp3,pp4,pp5,pp6,pp7,pp8,pp9,pp10,pp11,pp12,pp13,pp14,pp15,pp16,final_result,obs_chk_count,obs_chk_count,obs_end_card,testid,vehicleno,end_obs_card,obs_count,obs_test,obs_cond
        rfidbrand='SECUREYE'

        #rfidbrand='RADICAL'

        Check='0'
        pp0=0
        pp1=0
        pp2='0'
        pp3='0'
        pp4='0'
        pp5='0'
        pp6='0'
        pp7='0'
        pp8='0'
        pp9='0'
        pp10=0
        pp11='0'
        pp12='0'
        pp13='0'
        pp14='0'
        pp15='0'
        pp16='0'
        Database()
        sql=" select slno,obstacle,short_name,start_uid,end_uid,0 status,sensor_status,audio_name from obstacle_master " +obstacle_cond
        cursor.execute(sql)
        rows=cursor.fetchall()
        sl=0
        final_result = [list(i) for i in rows]
        
        
                
       
               
  
        
ini_data()
obs_chk_count=0
obs_end_card=""
obs_start_card=""
gearstart="N"
gear_stat=0
cp4=0
sess_start="Start"
while(rfid.is_open == True) and sess_start=="Start":

#     sql ="select sess_stat,pid  from ses_start"
#     cursor.execute(sql)
#     print (sql)
#     rows=cursor.fetchone()
#     if rows is not None:
#         session=rows[0]
#         print (session)
#         if session==2 or session=='2':
#             sess_start="Stop"
#             rfid.close()
         #conn.close()   


    
    #print(rfidbrand)
    if rfidbrand=='RADICAL' :
        s = rfid.readline()
        hex_string=s.decode('utf-8','ignore')[1:].strip()
        #print(hex_string)
    
    else:
        s = rfid.read(8)
        hex_string= binascii.hexlify(s).decode('utf-8','ignore')
    #if len(hex_string)==16:
   
   
    b=1
    cp0=cp1=cp10='0'
    obs_start='N'
    obs_chk_count=0
    while   b==1 and sess_start=="Start": #obs_chk_count<= len(final_result):
            
            count = 0
            Database()
            sql ="select sess_stat,pid  from ses_start"
            cursor.execute(sql)
            #print (sql)
            rows=cursor.fetchone()
            if rows is not None:
                session=rows[0]
                #print ("session :",session)
                if session==2 or session=='2':
                    sess_start="Stop"
                    rfid.close()
                    #dis.close()
                    os.system('python3 /var/www/html/evalutenew.py') 
            while (count < len(final_result) and  obs_start=='N'  and sess_start=="Start"):
                #print(final_result[0][3].upper(),hex_string.upper()[1:])
                Database()
                sql ="select sess_stat,pid  from ses_start"
                cursor.execute(sql)
                #print (sql)
                rows=cursor.fetchone()
                if rows is not None:
                    session=rows[0]
                    #print ("session :",session)
                    if session==2 or session=='2':
                        sess_start="Stop"
                        rfid.close()
                        #dis.close()
                        os.system('python3 /var/www/html/evalutenew.py')
                        exit(0)
                  
                cursor.close()
                if final_result[count][3].upper()==hex_string.upper()   and final_result[count][5]==0 and ((final_result[count][2]=="TE" and obs_chk_count>1) or final_result[count][2]!="TE"):
                    obs_type=final_result[count][2]
                    t_obs_type=obs_type
                    obs_no=final_result[count][0]
                    final_result[count][5]=1 
                    myAudio_name=final_result[count][7]
                    obs_start_card=final_result[count][3].upper()
                    obs_end_card=final_result[count][4]
                    
                    print (obs_type)
                    print(obs_start_card)
                    if (len(obs_end_card)==0 or obs_end_card is None) and len(obs_start_card)>0 and cp4==0 and ( gear_stat==0  or gear_stat==2):
                       obs_type=""
                    if (len(obs_end_card)==0 or obs_end_card is None) and len(obs_start_card)>0 and cp4==33 and gear_stat==1:
                
                        obs_type=t_obs_type
                        obs_start='Y'
                        #obs_type=""

                      #  #print("I am Waiting")
                        #time.sleep(25)
                    
    #                 if (final_result[count][2]=="TE" and obs_chk_count>0) or final_result[count][2]!="TE":
                    obs_chk_count=obs_chk_count+1
                    obs_start='Y'
                    #print(myMode)
                    if myMode=='L':
                      os.system('python3 /var/www/html/client.py play-' + myAudio_name)
                
                    if Live_Status=='Y':
                        if obs_type!="" :
                            with open("/var/www/html/dd5/inp_file", "w") as f:
                                f.write("start"+"|"+ obs_type)
                            Database()
                            if obs_type=='TE':
                                sql="update livefeed set " + obs_type +" = 'JAI HIND'"
                            else:
                                sql="update livefeed set " + obs_type +" = 'STARTED',last_obs='"+obs_type+"',last_init_time=sysdate()"
                            cursor.execute(sql)
                            conn.commit()
                            conn.close()
                        
                else:
                    obs_type=""
                    
                    
                
                    
                count=count+1
 
            if  (len(obs_start_card)>0  and  (len(obs_end_card)==0 or obs_end_card is None))  and gearstart=='N' :
                    gearstart='Y'
                    gear_stat=0
               
            if(len(obs_start_card)>0  and  (obs_end_card is None or len( obs_end_card)==0) ) and  cp4=='33' :
                 gearstart='Y'
                 gear_stat=0
                 obs_type=t_obs_type
                   
            if(len(obs_start_card)>0  and  (obs_end_card is None or len( obs_end_card)==0) ) and gearstart=='Y' and cp4=='33' and gear_stat==0 :
                gear_stat=1
                obs_type=t_obs_type
                gear_start_time=time.time()
                #final_result[count][5]=1
                #t_obs_type=""
               # if obs_type!="":
                if Live_Status=='Y':
                    Database()
                    sql="update livefeed set " + obs_type +" = 'STARTED',last_obs='"+obs_type+"',last_init_time=sysdate() where "+ obs_type+"=''"
                    print(sql)
                    cursor.execute(sql)
                    conn.commit()
                    conn.close()
                    with open("/var/www/html/dd5/inp_file", "w") as f:
                            f.write("start"+"|"+ obs_type)
                
               
            if gear_stat==1 and  gearstart=='Y' and  cp4=='0'  and (len(obs_start_card)>0  and  (len(obs_end_card)==0 or obs_end_card is None))  :
               gear_end_time=time.time()
               #if int(gear_end_time-gear_start_time)>minGearChange:
               
               #print(obs_type)
               if Live_Status=='Y':
                   if obs_type!=""  :
                        Database()
                        print(obs_type)
                        sql="update livefeed set " + obs_type +" = 'COMPLETED'"
                        cursor.execute(sql)
                        conn.commit()                    
                        conn.close()
                        with open("/var/www/html/dd5/inp_file", "w") as f:
                            f.write("stop"+"|"+ obs_type)
                   if t_obs_type!=""  :
                        Database()
                        print(obs_type)
                        sql="update livefeed set " + t_obs_type +" = 'COMPLETED'"
                        cursor.execute(sql)
                        conn.commit()                    
                        conn.close()
                        with open("/var/www/html/dd5/inp_file", "w") as f:
                            f.write("stop"+"|"+ obs_type)

               gear_stat=1   #gear_stat=2
               gearstart='N' # gearstart='N'
               obs_start='Y' #obs_start='N'

               stat='OFF' #stat='OFF'
               
               obs_chk_count=obs_chk_count+1
               sen_status=final_result[count-1][6]
               #rst.reset()

            mydata =Arduino.readline()
            #mydata2=analog.readline()
#             if len(mydata1) >1 :
#                 print("dis ",mydata1)
#             if len(mydata2)>1:
#                 print("analog ",mydata2)
            commacount = 0
            commacount1 = 0
            for i in mydata.decode('utf-8','ignore') : 
                  if i == ',': 
                      commacount = commacount + 1
          #print (commacount)
                   
            if commacount==18:
                mydata=re.split(',',mydata.decode('utf-8','ignore'))


                   
                
                cp0=mydata[1]
                cp1=mydata[2]  
                cp2=mydata[3] 
                cp3=mydata[4]
                cp4=mydata[5]
                cp5=mydata[6]
                cp6=mydata[7]
                cp7=mydata[8]
                cp8=mydata[9]
                cp9=mydata[10]
                cp10=mydata[11]
                cp11=mydata[12]
                cp12=mydata[13]
                
#                 if  cp5=='34' and cp6=='35':
#                      cp12='40'
#                      cp5='0'
#                      cp6='0'
#                 else:
#                      cp12='0'
#                      
                
                cp13=mydata[14]
                #print(cp5,cp6,cp12,cp13)
                cp14=mydata[15]
                cp15=mydata[16]
                cp16=mydata[17]
                #print(cp13,cp14,cp15,cp16)
                
                
                #print ("["+ cp0 + "','"  +cp1 + "','"  +cp2 + "','"  +cp3 + "','"  +cp4 + "','"  +cp5 + "','"  +cp6 + "','"  +cp7 + "','" +cp8 +"','" + cp9 + "','"+ cp10 + "','"+cp11 + "','"+cp12 + "','"+cp13 + "','"+cp14 + "','"+cp15 + "','"+cp16 +"]")
                if cp10.strip()=='p':
                    cp10='0'
                #print(cp0+","+cp1 +"," +cp2 +","+ cp3 +","+cp4+","+cp5+","+cp6+","+cp7+","+cp8+","+cp9+","+cp10+","+cp11+","+ cp12)    
            
                
                
                if obs_type=="TE" or obs_type=="TS":
                       if obs_type=="TE":
                           print("time End")
                       else:
                           print("Time Start")
                       time_status=0
                       #time.sleep(2)
                       stat="OFF"
                       obs_stat="N"
                       if obs_type=="TE":
                           
                           rfid.close()
                           dis.close()
                           analog.close()
                           exit(1)
                           
                           
                
                   
                if cp0==pp0 and cp1==pp1 and cp2==pp2 and cp3==pp3 and cp4==pp4 and cp5==pp5 and cp6==pp6 and cp7==pp7 and cp8==pp8   and cp9==pp9 and cp10==pp10 and cp11==pp11  and cp12==pp12 and cp13==pp13 and cp14==pp14 : # and cp15==pp15 and cp16==pp16:           
                    
                        p=1
                elif len(cp0) >4 or  len(cp1) >4 or len(cp3) >2 or  len(cp4) >2 or len(cp5) >2 or len(cp6) >2 or len(cp7) >2 or len(cp8) >2 or len(cp9) >2 or len(cp10) >4 or len(cp11) >2 or len(cp12) >2:
                    p='0'
                else:
                    Database()
                    #sql="insert into mydata (trainer,trainee,type,p0,p1,p2,p3,p4,p5,p6,p7,p8) values ('" +trainer1+"','"+ trainee1+"','"+ obs_type +"','"+ cp0 + "','"  +cp1 + "','"  +cp2 + "','"  +cp3 + "','"  +cp4 + "','"  +cp5 + "','"  +cp6 + "','"  +cp7 + "','" +cp8 + "')"
                    #print(sql)
                    #print ("["+ cp0 + "','"  +cp1 + "','"  +cp2 + "','"  +cp3 + "','"  +cp4 + "','"  +cp5 + "','"  +cp6 + "','"  +cp7 + "','" +cp8 +"','" + cp9 + "','"+ cp10 + "','"+cp11 +"','" +"']")
                    
                    try:
                        c0=int(cp0)
                    except ValueError:
                        c0=0
                    cp0=str(c0)
                    
                    try:
                        c1=int(cp1)
                    except ValueError:
                        c1=0
                    cp1=str(c1)
                    
                    
                    try:
                        c10=int(cp10)
                    except ValueError:
                        c10=0
                    cp10=str(c10)
                    
                    sql="insert into mydata (test_id,vehicle_no,trainer,trainee,type,p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16) values (" + str(testid)+ ",'" +vehicleno+"','" +trainer1+"','"+ trainee1+"','"+ obs_type +"','"+ cp0 + "','"  +cp1 + "','"  +cp2 + "','"  +cp3 + "','"  +cp4 + "','"  +cp5 + "','"  +cp6 + "','"  +cp7 + "','" +cp8 +"','" + cp9 + "','" + cp10 + "','"+cp11 +"','"+ cp12+"','"+cp13 +"','"+ cp14+"','"+ cp15 +"','"+ cp16+"')"
                    print ("["+ cp0 + "','"  +cp1 + "','"  +cp2 + "','"  +cp3 + "','"  +cp4 + "','"  +cp5 + "','"  +cp6 + "','"  +cp7 + "','" +cp8 +"','" + cp9 + "','"+ cp10 + "','"+cp11 + "','"+cp12 + "','"+cp13 + "','"+cp14 + "','"+cp15 + "','"+cp16 +"]")
                    #print (sql)
                    if len(obs_type)>2 or gear_stat==2:
                        cursor.execute(sql)
                        conn.commit()
                        sql=""
                    #conn.close()
                    
                    
                    
                    if Live_Status=='Y':
                        if  obs_type=='OBS_1':
                            sql="update live_feed_detail set horn=fn_getResultlive1('S5',(select max(p5) from mydata where type='OBS_1')), left_dist=fn_getResultlive('S0','21','OBS_1'), parking_light=fn_getResultlive1('S2',(select max(p2) from mydata where type='OBS_1')), right_indicator=fn_getResultlive1('S7',(select max(p7) from mydata where type='OBS_1'))  , left_indicator=fn_getResultlive1('S6',(select max(p6) from mydata where type='OBS_1'))   where short_name='OBS_1'"
                            sql1="update live_feed_detail set dist_nego_status=left_dist    where short_name='OBS_1'"


                        if obs_type=='OBS_2':
                           sql="  update live_feed_detail set back_dist=fn_getResultliveBK('S10','21','OBS_2'),left_dist=fn_getResultlive('S0','21','OBS_2'), parking_light=fn_getResultlive1('S2',(select max(p2) from mydata where type='OBS_2')), left_indicator=fn_getResultlive1('S6',(select max(p6) from mydata where type='OBS_2'))  where short_name='OBS_2' "
                           sql1="update live_feed_detail set dist_nego_status= left_dist*back_dist    where short_name='OBS_2'"
                        

                        if obs_type=='OBS_3':
                            sql="update live_feed_detail set horn=fn_getResultlive1('S5',(select max(p5) from mydata where type='OBS_3')),left_dist=fn_getResultlive('S0','21','OBS_3'), right_indicator=fn_getResultlive1('S7',(select max(p7) from mydata where type='OBS_3')), left_indicator=fn_getResultlive1('S6',(select max(p6) from mydata where type='OBS_3')) , parking_light=fn_getResultlive1('S2',(select max(p2) from mydata where type='OBS_3'))  where short_name='OBS_3'"
                            sql1="update live_feed_detail set dist_nego_status=left_dist    where short_name='OBS_3'"


                        if obs_type=='OBS_4':
                            sql="update live_feed_detail set left_dist=fn_getResultlive('S0','21','OBS_4'), right_dist=fn_getResultlive('S1','21','OBS_4'), left_indicator=fn_getResultlive1('S6',(select max(p6) from mydata where type='OBS_4')) where short_name='OBS_4'"
                            sql1="update live_feed_detail set dist_nego_status= left_dist*right_dist    where short_name='OBS_4'"

                        if obs_type=='OBS_5':
                            #sql="update live_feed_detail set back_dist=fn_getResultlive('S10','21','OBS_5'), parking_light=fn_getResultlive1('S2',(select min(p2) from mydata where type='OBS_5')), left_dist=fn_getResultlive('S0','21','OBS_5'), left_indicator=case when fn_getResultlive1('S7',(select max(p7) from mydata where type='OBS_5')) =0 then fn_getResultlive1('S6',(select max(p6)  from mydata where type='OBS_5')) else 0 end where short_name='OBS_5'"
                            sql="  update live_feed_detail set back_dist=fn_getResultliveBK('S10','21','OBS_5'),left_dist=fn_getResultlive('S0','21','OBS_5'), parking_light=fn_getResultlive1('S2',(select max(p2) from mydata where type='OBS_5')), left_indicator=fn_getResultlive1('S6',(select max(p6) from mydata where type='OBS_5'))  where short_name='OBS_5' "
                            sql1="update live_feed_detail set dist_nego_status= left_dist*back_dist    where short_name='OBS_5'"

                        if obs_type=='OBS_6':
                            sql="update live_feed_detail set left_dist=fn_getResultlive('S0','21','OBS_6'), parking_light=fn_getResultlive1('S2',(select max(p2) from mydata where type='OBS_6')),  left_indicator=fn_getResultlive1('S6',(select max(p6) from mydata where type='OBS_6'))  where short_name='OBS_6'"
                            sql1="update live_feed_detail set dist_nego_status=left_dist    where short_name='OBS_6'"

                        if obs_type=='OBS_7':
                            sql="update live_feed_detail set break=fn_getResultlive1('S9',(select max(p9) from mydata where type='OBS_7')), exuast_break=fn_getResultlive1('S8',(select max(p8) from mydata where type='OBS_7')), right_indicator=fn_getResultlive1('S7',(select max(p7) from mydata where type='OBS_7')) ,left_dist=fn_getResultlive('S0','21','OBS_7') where short_name='OBS_7'"
                            sql1="update live_feed_detail set dist_nego_status= left_dist    where short_name='OBS_7'"

                        if obs_type=='OBS_8':
                            sql="update live_feed_detail set left_dist=fn_getResultlive('S0','21','OBS_8'), right_dist=fn_getResultlive('S1','21','OBS_8'),break=fn_getResultlive1('S9',(select max(p9) from mydata where type='OBS_8'))  where short_name='OBS_8'"
                            sql1="update live_feed_detail set dist_nego_status= left_dist*right_dist    where short_name='OBS_8'"

                        if obs_type=='OBS_9':
                            
                            sql="update live_feed_detail set right_dist=fn_getResultlive('S1','21','OBS_9'), right_indicator=fn_getResultlive1('S7',(select max(p7) from mydata where type='OBS_9')) where short_name='OBS_9'"
                            sql1="update live_feed_detail set dist_nego_status=right_dist    where short_name='OBS_9'"
                        if len(sql)>5:
                            #print (sql)
                            cursor.execute(sql)
                            conn.commit()
                            #cursor.execute(sql1)
                            conn.commit()
                        
                        conn.close()                    
                        
                    
#                     print(obs_type)
#                     
#                     print(cp4)
#                     print (gearstart)
#                     print (gear_stat)
#                     print(obs_start)
                    if obs_type=="TE" or obs_type=="TS":
                       print("time End")
                       time_status=0
                       #time.sleep(2)
                       obs_start="N"
                       obs_type=""
                       if obs_type=="TE":
                           
                           aurdino0.close()
                           aurdino1.close()
                           aurdino2.close()
                           
                      
                    pp0=cp0
                    pp1=cp1
                    pp2=cp2
                    pp3=cp3
                    pp4=cp4
                    pp5=cp5
                    pp6=cp6
                    pp7=cp7
                    pp8=cp8
                    pp9=cp9
                    pp10=cp10
                    pp11=cp11
                    pp12=cp12
                    pp13=cp13
                    pp14=cp14
                    pp15=cp15
                    pp16=cp16
                    
        
#             s = rfid.read(8)
#             hex_string = binascii.hexlify(s).decode('utf-8','ignore')
#             
            if rfidbrand=='RADICAL' :
                s = rfid.readline()
                hex_string=s.decode('utf-8','ignore')[1:].strip()
                #print(hex_string)
    
            else:
                s = rfid.read(8)
                hex_string= binascii.hexlify(s).decode('utf-8','ignore')
    
            
            
            if (obs_end_card==hex_string.upper() and obs_start=='Y'  and len(hex_string)>0) or ( obs_start=='N' and obs_end_card is None and gearstart=='S'  and gear_stat==2 and cp4==0 ):
                #rst.reset()
                if Live_Status=='Y':
                    if obs_type!=""  :
                        Database()
                        sql="update livefeed set " + obs_type +" = 'COMPLETED'"
                        cursor.execute(sql)
                        conn.commit()
                        conn.close()
                        with open("/var/www/html/dd5/inp_file", "w") as f:
                            f.write("stop"+"|"+ obs_type)
                    
#                 obs_start="N"
#                 obs_type=""

#                 #obs_chk_count=obs_chk_count+1
            if obs_start=='N' and len(obs_end_card)==0  and gearstart=='S'  and gear_stat==2 :
                    gearstart='N'
                    gear_stat=0
                  #  obs_start='N'
                   # obs_type=""
                    #rst.reset()
            if obs_start=='Y'   and len(hex_string)>0 and  obs_start_card.upper()!=hex_string.upper() and   obs_end_card.upper() != hex_string.upper():
                mycount=0
                #print (mycount)
                #print (hex_string.upper())
                #print(len(final_result))
                while ( len(final_result) > mycount ):
                  
                    #print ( mycount)    
                    if final_result[mycount][3].upper()==hex_string.upper() and final_result[mycount][5]==0 :
                        obs_start='N'
                        #print (hex_string.upper())
                        
                        #rst.reset()
                        
                        #rst.reset()
                        if Live_Status=='Y':
                            if obs_type!=""  :
                                Database()
                                sql="update livefeed set " + obs_type +" = 'COMPLETED'"
                                cursor.execute(sql)
                                conn.commit()
                                conn.close()
                                with open("/var/www/html/dd5/inp_file", "w") as f:
                                   f.write("stop"+"|"+ obs_type)
                                
                        obs_type=""
                        break
                    pp1=pp2=400
                    mycount=mycount+1
                #time.sleep(1)
#             #if     obs_start=='N'  and len(hex_string)==16 :
                
os.system('python3 /var/www/html/evalutenew.py')                
     
