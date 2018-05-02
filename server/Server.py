import socket, ssl, threading
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
    #cursor.execute("DROP TABLE IF EXISTS test")
    #cursor.execute("DROP TABLE IF EXISTS data")
    sql = """create table if not exists test(
             id int4 auto_increment primary key,
             name varchar(255),
             actualstarttime varchar(255),
             actualendtime varchar(255),
             starttime decimal(20,18),
             endtime decimal(20,18),
             length decimal(20,18),
             instrument varchar(255)
             )"""
    sql2 = """create table if not exists data(
              Id int4 auto_increment primary key,
              name varchar(255),
              EIC decimal(6,2),
              data json
              )"""
    # create test
    cursor.execute(sql)
    cursor.execute(sql2)
    
createtable(db)

def insert(db,name,actual_start_time,actual_end_time,start_time,end_time,length,instrument,targets):
    cursor = db.cursor()
    sql = """insert into test(name,actualstarttime,actualendtime,starttime,endtime,length,instrument)
             values (%s,%s,%s,%s,%s,%s,%s);"""
    
    cursor.execute(sql,(name,actual_start_time,actual_end_time,start_time,end_time,length,instrument))
    for target in targets:
        target1 = target['target']
        del target['lowerLimit']
        del target['upperLimit']
        del target['target']
        sql2 = """insert into data(name,EIC,data)
                  values (%s,%s,%s);"""
        cursor.execute(sql2,(name,target1,json.dumps(target)))
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
    a = 0
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
            insert(db,name,actual_start_time,actual_end_time,start_time,end_time,length,instrument,targets)            
            pass
        elif data == 'begin to send':
            print ('create file')
            a += 1
            s = str(a)
            with open('./' + s +'.json', 'w') as f:
                pass
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

                
    
            
    #connstream.send('Welcome from server!'.encode())
    print ('receiving, please wait for a second ...')
    
        
    receiveFile(connstream)
    
    #connstream.close()
    print ('receive finished')
    print ('Connection from %s:%s closed.' % addr)


while True:    
    conn,addr = server.accept()
    t = threading.Thread(target = connect, args = (conn,addr))
    t.start()  
  

