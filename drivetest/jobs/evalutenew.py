#!/usr/bin/env python3
import mysql.connector as mariadb
import re
import ast
import os
import sys


def Database():
        global conn, cursor,marks_status
        conn = mariadb.connect(host="localhost",user="root",password='rootpass',database="driver_test" )
        cursor = conn.cursor()

Database()
global obs_error_list,marks_status,cur_marks,total_marks,obs_marks,test_score,test_total,test_count,pass_count,chkInvLogic,chkCountLogic
total_marks=0
obs_marks=0
cur_marks=0
test_count=0
pass_count=0


sql="select sdt_pid,ifnull(Marks,'N') marks from terminal"
cursor.execute(sql)
rows=cursor.fetchone()
if rows is not None:
        sdtpid=rows[0]
        marks_status=rows[1]
        print(marks_status)
        os.system("kill -9 " + str(sdtpid))



if len(sys.argv)==2:
        testid = sys.argv[1]
        sql="select distinct test_id from mydata  where type like 'OBS%' and test_id=" +str(testid)
        cursor.execute(sql)
        rows=cursor.fetchone()
        if rows is not None:
                MyStat="Existing"
                
        else:
                sql="select (select COUNT(*) from mydata)-(select  count(*) from mydata_history where test_id=(select distinct test_id from mydata))"
                cursor.execute(sql)
                rows=cursor.fetchone()
                if rows is not None:
                    data=rows[0]
                    if data>0:
                        Database()
                        sql="delete from mydata_history where test_id=(select distinct test_id from mydata)"
                        cursor.execute(sql)
                        conn.commit()
                        #conn.close()
                        Database()
                        sql="insert into mydata_history select * from mydata"
                        cursor.execute(sql)
                        conn.commit()
                    else:
                        sql="delete from mydata"
                        cursor.execute(sql)
                        conn.commit() 
                        
                
                Database() 
                sql="insert into mydata select distinct * from mydata_history where test_id="+ str(testid)
                cursor.execute(sql)
                conn.commit()
        

sql ="select test_id,trainer,trainee  from mydata  group by test_id,trainer,trainee"
cursor.execute(sql)
rows=cursor.fetchone()

if rows is not None:

    Database()
    test_id=rows[0]
    trainer_id=rows[1]
    trainee_id=rows[2]
    sql ="delete from training_remarks where test_id=" + str(test_id)
    cursor.execute(sql)
    conn.commit()
    sql= "select distinct(type) from mydata where type like 'OBS%'"
    cursor.execute(sql)
    rows=cursor.fetchall()
    final_result = [list(i) for i in rows]
    #fruits = ast.literal_eval(final_result)
    
    count=0
    mytype=""
    test_score=0
    test_total=0
    while count < len(final_result ):
            mytype=str(final_result[count])
            mytype=mytype.replace("['",'')
            mytype=mytype.replace("']",'')
            
            print (mytype)
            
            sql ="select distinct (task_list) as task_list,obstacle from obstacle_master where short_name='"+ mytype+ "'"
            #print(sql)
            
            cursor.execute(sql)
            rows=cursor.fetchone()
            mydata=rows[0]
            myobstacle=rows[1]
            print (mydata)
            obs_error_list=[]
            #print (mydata)
            if len(mydata)>0:
                    
                    mydata=mydata.replace('|',',')
                    #print (mydata)
                    mydata=re.split(',',mydata)
                    #print (mydata)
                    
                    i=0
                    Final_status="PASS"
                    total_marks=0
                    obs_marks=0
                    cur_marks=0
                    Remarks=""
                    while i < len(mydata ):
                       print(i)
                       print(mydata[i])
                       sensor=mydata[i]
                       print ("sensor: ",sensor)
                       chkInvLogic=sensor[:1]
                       chkCountLogic=sensor[:2][1:]
                       print(chkCountLogic)
                       #print (chkInvLogic)
                       if chkCountLogic=="C":
                           chkCount=sensor[:1]
                           newsensor=sensor[(len(sensor)-1):]
                           task_name=sensor[:2]
                           print (chkCount,sensor[:2])
                       if chkCountLogic=="c":
                           chkCount=sensor[:1]
                           newsensor=sensor[(len(sensor)-1):]
                           task_name=sensor[:2]
                           print (chkCount,sensor[:2])
                       
                       if chkInvLogic=='-':
                           sensor=sensor[1:]
                           chkInvLogic='1'
                       else :
                           chkInvLogic='0'
                       print("sensor :=",sensor)
                       print(sensor[:1])
                       
                       if  sensor=='0' :
                               #sql="select ifnull(max(p0),12)  from mydata where    p0<=13 and type='"+ mytype +"'"
                               #sql="select GROUP_CONCAT(t.p0 ) from ( SELECT distinct p0 FROM `mydata`  where p0 <14  and p0!= 0 and type='"+ mytype +"' order by 1 limit 5) t"
                                   sql=" SELECT concat(cast(min(p0) as char(2)) ,'|',  cast(max(p0) as char(2))) FROM `mydata`  where  p0> 3 and type='"+ mytype +"' "
                                
                       elif chkCountLogic=='C':
                           #sensor=task_name
                           
                           sql="select case when ( count(*)+1)>="+chkCount + " then 1 else 0 end FROM mydata T1 WHERE  TYPE='" + mytype +"' AND p"+newsensor+"<>(SELECT p"+ newsensor +" from mydata T where TYPE='"+ mytype+"' and T.sl_no<T1.sl_no order by sl_no desc LIMIT 1)"
                       
                       elif chkCountLogic=='c':
                           #sensor=task_name
                           
                           sql="select case when ( count(*)+1)<"+chkCount + " then 1 else 0 end FROM mydata T1 WHERE  TYPE='" + mytype +"' AND p"+newsensor+"<>(SELECT p"+ newsensor +" from mydata T where TYPE='"+ mytype+"' and T.sl_no<T1.sl_no order by sl_no desc LIMIT 1)"
                       
                       elif sensor=='1' :
                               #sql="select ifnull(max(p1),2)   from mydata where  p1<=3 and type='"+ mytype +"'"
                                sql=" SELECT concat(cast(min(p1) as char(2)) ,'|',  cast(max(p1) as char(2))) FROM `mydata`  where p1>3 and type='"+ mytype +"'"
                       elif sensor=='10' :
                               #sql="select ifnull(max(p1),2)   from mydata where  p1<=3 and type='"+ mytype +"'"
                                sql=" SELECT concat(cast(min(p0) as char(2)) ,'|',  cast(max(p0) as char(2))) FROM `mydata`  where p0>3 and type='"+ mytype +"'"
                            #sql="select '5|5' from dual";
                       
                       
                       elif sensor=='8' :
                               #sql="select ifnull(max(p1),2)   from mydata where  p1<=3 and type='"+ mytype +"'"
                                sql="select min(p" + sensor + " )  from mydata where type='"+ mytype +"'"
    
                       
                       else:
                               sql="select max(p" + sensor + " )  from mydata where type='"+ mytype +"'"
                       print (sql)
                       
                       if marks_status=='Y':
                                       print ('chkCountLogic: -',chkCountLogic)
                                       if chkCountLogic=='C' or chkCountLogic=='c':
                                           newsensor=sensor
                                       else :
                                           newsensor='S'+sensor
                                       print("sensor :=",sensor)    
                                       sql_marks=" select fn_get_marks('" +mytype+"','" + newsensor+"')from dual"
                                       print(sql_marks)
                                       cursor.execute(sql_marks)
                                       rows=cursor.fetchone()
                                       if rows is not None:
                                               cur_marks=rows[0]
                                               print("cur marks")
                                               print (cur_marks)
                                               obs_marks=obs_marks + cur_marks
                                               test_total=test_total+cur_marks
                                               
    


                       print(sql)
                       cursor.execute(sql)
                       rows=cursor.fetchone()
                       if rows is not None:
                               myvalue= str(rows[0])
                               print (myvalue)
                       elif sensor=='1':
                               myvalue='0|11'
                       elif sensor=='0':
                               myvalue='0|11'
                       elif sensor=='10':
                               myvalue='0|11'
                       if sensor[:1]=='S':
                           sensor=sensor[(len(sensor)-1):]
                           #print (len(sensor)-1)
                           #print("sensor  hai :=",sensor)
                       print("mysensor :",sensor)
                       
                       if    sensor=='0'  or sensor=='1'      :
                               
                               sql="select fn_getResultSensor('S" +sensor +"','" + myvalue +"','" + mytype + "')"
                               
                       elif sensor=='10':
                           #sql="select fn_getResultSensorBK('S" +sensor +"','" + myvalue +"','" + mytype + "')"
                             sql="select fn_getResultSensor('S" +sensor +"','" + myvalue +"','" + mytype + "')"
        
                       else:
                               if myvalue=="":
                                   myvalue="0"
                               #print("chkInvLogic -----",chkInvLogic)
                               if chkInvLogic=='1':
                                   #print("Hello world")
                                   sensor="S-"+sensor
                               if chkCountLogic=='C' or chkCountLogic=='c':
                                   sensor=sensor
                               else:    
                                   sensor='S'+sensor
                                   
                               sql="select fn_getResult('"+sensor +"'," + myvalue +")"
                               print (sql)
                               
                       #print (myvalue)
                       
                                       
                            
                       
                       #print (sql)
                       cursor.execute(sql)
                       rows=cursor.fetchone()
                       print(marks_status)
                       #print(rows[0])
                       
                       
                       if rows[0]!='PASS'  and rows[0] is not None:
                             Final_status = 'FAIL'
                             Remarks=Remarks +  rows[0] + " | "
                             obs_error_list.append(rows[0])
                             cur_marks=0
                             
                       #print(rows[0])
                       
                       if marks_status=='Y':
                               total_marks=total_marks+cur_marks
                               test_score=test_score+cur_marks
                       i=i+1
                    print("Remarks -",Remarks)
                    print(obs_error_list) 
                    if  Remarks=="":
                            pass_count=pass_count+1
                    test_count=test_count+1   
            else:
                    Final_status="PASS"
                    Remarks=""
                    test_count=test_count+1
                    pass_count=pass_count+1


                    
            count=count+1
            print('Report  for :' + myobstacle)
            print ("Test ID :" + str(test_id))
            print( 'Status  : '+Final_status)
            if marks_status=='Y':
                    print ('Marks   : ' + str(total_marks) + ' / '+ str(obs_marks) )
            #Remarks=Remarks[:len(Remarks)-2]
            Remarks='|' .join(set(obs_error_list)) 
            print('Remarks  : ' +Remarks)
            #print('|' .join(set(obs_error_list)) )
            #sql="SELECT 1,round(((minute(timediff(max(case when `type`='TE' then creation_date end), max(case when `type`='TS' then creation_date end))) ) +((second(timediff(max(case when `type`='TE' then creation_date end), max(case when `type`='TS' then creation_date end))) )/60))*100)  tt FROM `mydata` WHERE type in ('TS','TE')"
            sql="SELECT 1,round(((minute(timediff(max(creation_date ), min(case when `type`='TS' then creation_date end))) ) +((second(timediff(max( creation_date ), min(case when `type`='TS' then creation_date end))) )/60))*100)  tt FROM `mydata` "
            cursor.execute(sql)
            rows=cursor.fetchone()
            tt=0
            if rows is not None:
                tt=rows[1]
            print(tt)
            if tt is None:
                sql="SELECT 1,round(((minute(timediff(max(creation_date ), min( creation_date ))) ) +((second(timediff(max( creation_date ), min(creation_date ))) )/60))*100)  tt FROM `mydata` "
                cursor.execute(sql)
                rows=cursor.fetchone()
                tt=0
                if rows is not None:
                    tt=rows[1]
            print(tt)
            
            
            sql="update traineedetails set `"+ mytype +"`='"+ Final_status  + "' ,time_taken="+ str(tt) +",test_count=" + str(test_count) +",pass_count=" + str(pass_count)+" where  TRAINER_ARMYID='" + trainer_id + "' and trainee_armyid='" + trainee_id + "' and test_id=" + str(test_id)
            print(sql)
            cursor.execute(sql)
            conn.commit()
            if marks_status=='Y':
                    
                    sql="insert into training_remarks (test_id,obstacle_type,status,remarks,marks,obs_marks) values ("+ str(test_id) + ",'" +  mytype + "','" +Final_status+"','" +  Remarks +"'," + str(total_marks) +","  +str(obs_marks) +")"
            else:
                    sql="insert into training_remarks (test_id,obstacle_type,status,remarks) values ("+ str(test_id) + ",'" +  mytype + "','" + Final_status + "','" +  Remarks +"')"
            print(sql)
            cursor.execute(sql)
            conn.commit()
    #print (mydata)
    print(' Total Marks : '+ str(test_score) + ' / ' + str(test_total) )
    print(test_count)
    print (pass_count)
    if marks_status=='Y':
            sql="update traineedetails set  marks="+ str(test_score)  + ",total_marks="+ str(test_total)+ ",test_count=" + str(test_count) +",pass_count=" + str(pass_count)+"  where  TRAINER_ARMYID='" + trainer_id + "' and trainee_armyid='" + trainee_id + "' and test_id=" + str(test_id)
            print(sql)
            
            cursor.execute(sql)
            conn.commit()
#             sql="insert into training_remarks (test_id,obstacle_type,status,remarks,Marks,obs_marks) values ("+ str(test_id) + ",'START POINT','PASS','',6,6)"
#             cursor.execute(sql)
#             conn.commit()
#             
            sql="insert into training_remarks (test_id,obstacle_type,status,remarks,Marks,obs_marks) values ("+ str(test_id) + ",'TOTAL MARKS','','',"+str(test_score)+",80)"
            cursor.execute(sql)
            conn.commit()
##            sql="delete from livefeed"
##            cursor.execute(sql)
##            conn.commit()
##            sql="insert into livefeed select * from livefeed_history where test_id="+str(test_id)
##            cursor.execute(sql)
##            conn.commit()
##
##            sql="delete from live_feed_detail"
##            cursor.execute(sql)
##            conn.commit()
##            sql="insert into live_feed_detail select * from live_feed_detail_history where test_id="+str(test_id)
##            cursor.execute(sql)
##            conn.commit()
##            
            
    
    
else:
        print("No Data Found")
    

#print(obs_error_list)