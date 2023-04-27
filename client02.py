import socket
from socket import AF_INET, SOCK_STREAM

class Client():

    def __init__(self, host, port) -> None:
        self.HOST = host
        self.PORT = port

        self.runing = False
        

    def login(self, user):
        self.msg_server(f"usuario {user}")
        
    def msg_server(self, message= "Hello World!"):
        self.runing = True

        s = socket.socket(AF_INET, SOCK_STREAM)
        s.connect((self.HOST, self.PORT))        
        s.send(bytes(message, 'utf-8'))        
        data = s.recv(128)
        print(data.decode())        
        s.close()
        self.runing = False
