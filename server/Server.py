import socket, ssl, threading
import mysql.connector
import os,sys
import time
import json
from datetime import datetime
def connectdb():
    print('connect to server')
    db = mysql.connector.connect(user = 'root',password = 'MINCSY417',
                                 host = 'localhost',database = 'projectdb')

    print('connected!')
    return db

db = connectdb()

def createtable(db): 
    cursor = db.cursor() 

    sql1 = """create table if not exists SPL_INFO(
             id int4 auto_increment primary key,
             name varchar(255),
             actualstarttime datetime(6),
             actualendtime datetime(6),
             starttime decimal(20,18),
             endtime decimal(20,18),
             length decimal(20,18),
             instrument varchar(255)
             )"""
    sql2 = """create table if not exists SPL_DTL(
              Id int4 auto_increment primary key,
              name varchar(255),
              EIC decimal(6,2),
              data json,
              instrument varchar(255)
              )"""
    # create table
    cursor.execute(sql1)
    cursor.execute(sql2)
    
createtable(db)

def insert(db,name,actual_start_time,actual_end_time,start_time,end_time,length,instrument,targets):
    cursor = db.cursor()
    sql = """insert into SPL_INFO(name,actualstarttime,actualendtime,starttime,endtime,length,instrument)
             values (%s,%s,%s,%s,%s,%s,%s);"""
    
    cursor.execute(sql,(name,actual_start_time,actual_end_time,start_time,end_time,length,instrument))
    for target in targets:
        target1 = target['target']
        del target['lowerLimit']
        del target['upperLimit']
        del target['target']
        sql2 = """insert into SPL_DTL(name,EIC,data,instrument)
                  values (%s,%s,%s,%s);"""
        cursor.execute(sql2,(name,target1,json.dumps(target),instrument))
    db.commit()


context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  
context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
#create socket
server = socket.socket()
#bind address and port

server.bind(("127.0.0.1",300))
#listen request
server.listen(5)

print("waiting for the client")

keyFiles = {'instrument1':'111','instrument2':'222','instrument3':'333'}

def checkUsername(username,conn):
    
    if username in keyFiles:
        conn.sendall('valid'.encode())
    else:
        conn.sendall('invalid'.encode())

def checkPassword(username,password,conn):
    

    if keyFiles[username]==password:
        conn.sendall('valid'.encode())                                                                                                                                                                                                                                                                                          
        return 'valid'
    else:
        conn.sendall('invalid'.encode())
        return 'invalid'
    
def receiveFile(conn):
    s = 'jsonfile'
    while True:
        data = conn.recv(1024).decode()
        
        if data == 'finish':
            print ('reach the end of file')
            with open('./' + s +'.json','r') as f:
                jsonFile = json.load(f)
            f.close()
            name = jsonFile['file name']
            actual_start_time = jsonFile['actual start time']
            actual_end_time = jsonFile['actual end time']
            start_time = jsonFile['start time']
            end_time = jsonFile['end time']
            length = jsonFile['length']
            instrument = jsonFile['instrument']
            targets = jsonFile['EIC']
            actual_start_time = datetime.strptime(actual_start_time, "%Y-%m-%d %H:%M:%S.%f")
            actual_end_time = datetime.strptime(actual_end_time, "%Y-%m-%d %H:%M:%S.%f")
            insert(db,name,actual_start_time,actual_end_time,start_time,end_time,length,instrument,targets)            
            pass
        elif data == 'begin to send':
            print ('create file')
            with open('./' + s +'.json', 'w') as f:
                pass
        elif data[0:9] == 'file_name':
            s = data[9: ]
        else:
            with open('./' + s +'.json', 'a') as f:
                f.write(data)

def connect(sock, addr):
    print ('Accept new connection from %s:%s...' % addr)
    connstream = context.wrap_socket(sock, server_side=True)
    
    while True:
        data = connstream.recv(1024).decode()

        if not data:
            continue

        elif data.startswith('username'):
            username=data.split(':')[-1]
            checkUsername(username,connstream)
        elif data.startswith('password'):
            userpasswd=data.split(':')[-1]
            result = checkPassword(username,userpasswd,connstream)
            if result == 'valid':
                break

                
    
            

    print ('receiving, please wait for a second ...')
    
        
    receiveFile(connstream)
    
    print ('receive finished')



while True:    
    conn,addr = server.accept()
    t = threading.Thread(target = connect, args = (conn,addr))
    t.start()  
  

