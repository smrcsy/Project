from watchdog.observers import Observer
from watchdog.events import *
import mysql.connector
import os,sys
import time
import json

def connectdb():
    print('connect to server')
    db = mysql.connector.connect(user = 'root',password = 'MINCSY417',
                                 host = 'localhost',database = 'projectdb')

    print('connected!')
    return db

db = connectdb()

def createtable(db): 
    cursor = db.cursor()
    # !!!delete exist table
    cursor.execute("DROP TABLE IF EXISTS test")
    cursor.execute("DROP TABLE IF EXISTS data")
    sql = """create table test(
             id int4 auto_increment primary key,
             name varchar(255),
             starttime decimal(20,18),
             endtime decimal(20,18),
             length decimal(20,18),
             instrument varchar(255)
             )"""
    sql2 = """create table data(
              Id int4 auto_increment primary key,
              name varchar(255),
              EIC decimal(6,2),
              data json
              )"""
    # create test
    cursor.execute(sql)
    cursor.execute(sql2)
    
createtable(db)

def insert(db,name,start_time,end_time,length,instrument,targets):
    cursor = db.cursor()
    sql = """insert into test(name,starttime,endtime,length,instrument)
             values (%s,%s,%s,%s,%s);"""
    
    cursor.execute(sql,(name,start_time,end_time,length,instrument))
    for target in targets:
        target1 = target['target']
        del target['lowerLimit']
        del target['upperLimit']
        del target['target']
        sql2 = """insert into data(name,EIC,data)
                  values (%s,%s,%s);"""
        cursor.execute(sql2,(name,target1,json.dumps(target)))
    db.commit()

    
class FileEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)
    def on_created(self, event):
        path = event.src_path
        with open(path,'r') as f:
            jsonFile = json.load(f)
        f.close()
        name = jsonFile['file name']
        start_time = jsonFile['start time']
        end_time = jsonFile['end time']
        length = jsonFile['length']
        instrument = jsonFile['instrument']
        targets = jsonFile['EIC']
        insert(db,name,start_time,end_time,length,instrument,targets)

        
if __name__ == "__main__":
    observer = Observer()
    event_handler = FileEventHandler()
    observer.schedule(event_handler,r"C:\Users\csy60\Downloads\finalproject-master\finalproject-master",True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
            
            


'''
#print(json.dumps(jsonFile['EIC'][0]))




def select(db):
    cursor = db.cursor()
    sql = """SELECT doc -> '$.darkgreen' FROM firstTable"""
    cursor.execute(sql)
    for row in cursor:
        print(row)
#
#insert(db)
#select(db)
'''
