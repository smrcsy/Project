import socket, ssl, threading

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  
context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
#create socket
server = socket.socket()
#bind address and port

server.bind(("127.0.0.1",8000))
#listen request
server.listen(5)

keyFiles = {'instrument1':'111','instrument2':'222','instrument3':'333'}
def connect(sock, addr):
    print ('Accept new connection from %s:%s...' % addr)
    connstream = context.wrap_socket(sock, server_side=True)
    
    while True:
        data = connstream.recv(1024).decode()

        if not data:
            continue

        elif data.startswith('username'):
            username=data.split(':')[-1]
            if username in keyFiles:
                connstream.sendall('valid'.encode())
            else:
                connstream.sendall('invalid'.encode())
        elif data.startswith('password'):
            userpasswd=data.split(':')[-1]

            if keyFiles[username]==userpasswd:
                connstream.sendall('valid'.encode())
                #time.sleep(0.5)
                #connstream.sendall('%s broken connect with server'%time.strftime("%Y-%m-%d %X", time.localtime()))
                                                                                                                                                                                                                                                                          
                break
            else:
                connstream.sendall('invalid'.encode())
    connstream.send('Welcome from server!'.encode())
    print ('receiving, please wait for a second ...')
    while True:
        data = connstream.recv(1024).decode()
   
        if data == 'finish':
            print ('reach the end of file')
            break
        if data == 'begin to send':
            print ('create file')

            with open('./h.txt', 'w') as f:
                pass
        else:
            with open('./h.txt', 'a') as f:
                f.write(data)
                print('d')

    connstream.close()
    print ('receive finished')
    print ('Connection from %s:%s closed.' % addr)


while True:
    print("waiting for the client")
    conn,addr = server.accept()
    t = threading.Thread(target = connect, args = (conn,addr))
    t.start()  
  


