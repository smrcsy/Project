import socket, ssl, threading

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  
context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
#create socket
server = socket.socket()
#bind address and port

server.bind(("127.0.0.1",8000))
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
            pass
        if data == 'begin to send':
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
  


