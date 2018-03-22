import socket, ssl
address='127.0.0.1'   
port=8000   
       
s = socket.socket()

ssl_sock = ssl.wrap_socket(s,ca_certs="cert.pem",cert_reqs=ssl.CERT_REQUIRED)  
ssl_sock.connect(('127.0.0.1',8000))

def checkUsername():
    while True:
        username = input('please input your username:')
        ssl_sock.sendall(('username:' + username).encode())
        recv = ssl_sock.recv(1024).decode()
        if recv == 'valid':
            break
        else:
            print('Wrong username, please try again')
            continue
def checkPassword():
    while True:
        password = input('please input your password:')
        ssl_sock.sendall(('password:' + password).encode())
        recv = ssl_sock.recv(1024).decode()
        if recv == 'valid':
            break
        else:
            print('Wrong username, please try again')
            continue
        
checkUsername()
checkPassword()

print(ssl_sock.recv(1024).decode())
ssl_sock.send('begin to send'.encode())   

with open('./h.txt', 'r') as f:
    for data in f:
        ssl_sock.send(data.encode())
    print ('sended !')
    ssl_sock.send('finish'.encode()) 
ssl_sock.close()

