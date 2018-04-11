import socket, ssl
from watchdog.observers import Observer
from watchdog.events import *
import os,sys
import time


address='127.0.0.1'   
port=8000   
       
client = socket.socket()

client = ssl.wrap_socket(client,ca_certs="cert.pem",cert_reqs=ssl.CERT_REQUIRED)  
client.connect(('127.0.0.1',8000))

def usernameResult():
    while True:
        username = input('please input your username:')
        client.sendall(('username:' + username).encode())
        recv_msg = client.recv(1024).decode()
        if recv_msg == 'valid':
            break
        else:
            print('Wrong username, please try again')
            continue
def passwordResult():
    while True:
        password = input('please input your password:')
        client.sendall(('password:' + password).encode())
        recv_msg = client.recv(1024).decode()
        if recv_msg == 'valid':
            break
        else:
            print('Wrong username, please try again')
            continue
        
usernameResult()
passwordResult()

def sendFile(file):
    #print(client.recv(1024).decode())
    client.send('begin to send'.encode())   
    print('Begin !')
    with open(file, 'r') as f:
        for data in f:
            client.send(data.encode())

        client.send('finish'.encode())
        print ('Finish !')
class FileEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)
    def on_created(self, event):
        path = event.src_path
        sendFile(path)
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

