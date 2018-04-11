#This code is used for monitoring d file and coverting to mzml file and get stats
#use watchdog to monitor folder
from watchdog.observers import Observer
from watchdog.events import *
import time
import re
import os
from os.path import join, getsize
import sys
import numpy as np
import pymzml
import matplotlib.pyplot as plt
import json
import socket, ssl

address='127.0.0.1'   
port=8000   
       
client = socket.socket()

client = ssl.wrap_socket(client,ca_certs="cert.pem",cert_reqs=ssl.CERT_REQUIRED)  
client.connect(('0.tcp.ngrok.io',12337))

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
    print(file)
    with open(file, 'r') as f:
        for data in f:
            client.send(data.encode())

        client.send('finish'.encode())
        print ('Finish !')
class FileEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)
     
     #get the size of a folder   
    def getdirsize(self,dir):
        size=0
        for root, dirs, files in os.walk(dir):
            size+= sum([getsize(join(root, name)) for name in files])
        return size
    
    def produceJson(self,mzmlName):
        jfile_path=r"C:\Users\csy60\project\json"        
        jfile_pathname=jfile_path+"\\"+mzmlName.split('.')[0]+".json"
        f=open(jfile_pathname,'a')
        f.close
        print(1)
        js={}#create a empty dict for json data
        js['file name']=mzmlName
        
        msrun = pymzml.run.Reader(mzmlName, obo_version = '3.71.0') 
        times = msrun['TIC'].mz
        intensities = msrun['TIC'].i
        length =  max(times) - min(times)
        js['start time']=min(times)
        js['end time']=max(times)
        js['length']=length
        js['instrument']=' '#how to get instrument???
        
        msrun = pymzml.run.Reader(mzmlName, obo_version = '3.71.0')
        eicTargets = [100, 200, 300] # user defined
        eicTol = 0.03 # user defined
        results = []
        for eicTarget in eicTargets:
            results.append( {
                'target': eicTarget,
                'RTs' : [], # list to hold retention times
                'ints' :  [], # list to hold intensities
                'lowerLimit' : eicTarget - eicTol,
                'upperLimit' : eicTarget + eicTol
                }
            )
        
        for spectrum in msrun:
            try:
                time = spectrum['scan start time']
            except:
                break 
            mzs = np.asarray(spectrum.mz,dtype=np.float64)
            ints = np.asarray(spectrum.i,dtype=np.float64) 
            for target in results:
                lowerLimit = target['lowerLimit']
                upperLimit = target['upperLimit']
                mask = np.where( (mzs > lowerLimit) & (mzs < upperLimit) ) 
                eicInts = ints[mask]
                target['RTs'].append(time)
                target['ints'].append(np.sum(eicInts))
        for target in results:
            plt.plot(target['RTs'], target['ints'])
        #plt.show()
        js['EIC']=results
        #print(js)
        js_final=json.dumps(js)
        #print(js_final)
        file=open(jfile_pathname,'w')
        file.write(js_final)
        file.close()
        sendFile(jfile_pathname)
        
            

#when new files/folders come in        
    def on_created(self, event):
       # print "log file %s changed!" % event.src_path
        s=event.src_path
        if s.endswith('.d'):
            convertname=s.replace("\\","\\\\")
            size_list=[]
            while True:
                foldersize=self.getdirsize(s)
                size_list.append(foldersize)
                print (size_list)
                
                if len(size_list)>2:
                    #print size_list[len(size_list)-1]
                    #print size_list[len(size_list)-3]
                    if size_list[len(size_list)-1]==size_list[len(size_list)-3]:                   
                        print ("size of folder doesn't change")
                        break
                #every 5 minutes    
                time.sleep(1)    
                
            #put mzml file in the file that contain this code file        
            cmd="msconvert " +convertname+ r" -o C:\Users\csy60\project\input"
            print(convertname)
            os.system(cmd)
            
            dName=convertname.split("\\")[len(convertname.split("\\"))-1]
            mzmlName=dName.replace(".d",".mzml")
            print(mzmlName)
            #wait for json file produced
            time.sleep(20)
            #when convert to mzml, produce json file
            #self.produceJson("pbQC009.mzML")#change it to mzmlName
            self.produceJson(mzmlName)


"""
        if event.is_directory:
            print("directory created:{0}".format(event.src_path))
        else:
            print("file created:{0}".format(event.src_path))
"""        
"""
#when remove files/folers
    def on_moved(self, event):
       if event.is_directory:
            print("directory moved from {0} to {1}".format(event.src_path,event.dest_path))
        else:
            print("file moved from {0} to {1}".format(event.src_path,event.dest_path))

    def on_deleted(self, event):
        if event.is_directory:
            print("directory deleted:{0}".format(event.src_path))
        else:
            print("file deleted:{0}".format(event.src_path))

    def on_modified(self, event):
        if event.is_directory:
            print("directory modified:{0}".format(event.src_path))
        else:
            print("file modified:{0}".format(event.src_path))
"""    
    

if __name__ == "__main__":
    observer = Observer()
    event_handler = FileEventHandler()
    observer.schedule(event_handler,r"C:\Users\csy60\project\input",True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
