import socket
from socket import AF_INET, SOCK_STREAM
from threading import Thread
import utils
from utils import MSG_TO_SERVER, CLIENT_PASIVE_LISTEN_SUBSCRIBE, CLIENT_PASIVE_LISTEN_UNSUBSCRIBE
from utils import PORT_GENERAL

class Client():

    def __init__(self) -> None:
        self.HOST = None

        self.subscribe = False  
        self.socket_pasive_listen = None      
        
    def conn_server(self, ip_server):
        self.HOST = ip_server

    def msg_to_server(self, message= "Hello World!"):
        s = socket.socket(AF_INET, SOCK_STREAM)
        s.connect((self.HOST, PORT_GENERAL))

        data_dict ={
            "type": MSG_TO_SERVER,
            "msg": message
        }
        data_bytes = utils.encode(data_dict)
        s.send(data_bytes)
        data = s.recv(128)
        print(data.decode())
        s.close()

    def client_pasive_listen_subscribe(self):
        s = socket.socket(AF_INET, SOCK_STREAM)
        s.connect((self.HOST, PORT_GENERAL))

        data_dict ={
            "type": CLIENT_PASIVE_LISTEN_SUBSCRIBE,            
        }
        data_bytes = utils.encode(data_dict)
        s.send(data_bytes)
        data = s.recv(128)
        print(data.decode())
        if data.decode() == "SUBOK":
            print("Subscrito con exito")
            t = Thread(target= self.pasive_listen, args=[s])
            t.start()
            return

    def client_pasive_listen_unsubscribe(self):
        s = socket.socket(AF_INET, SOCK_STREAM)
        s.connect((self.HOST, PORT_GENERAL))

        data_dict ={
            "type": CLIENT_PASIVE_LISTEN_UNSUBSCRIBE,            
        }
        data_bytes = utils.encode(data_dict)
        s.send(data_bytes)
        data = s.recv(128)
        if data.decode() == "UNSUBOK":
            print("Unsubscrito con exito")            
            self.socket_pasive_listen.close()
            self.socket_pasive_listen = None

    def pasive_listen(self, socket: socket.socket):
        self.socket_pasive_listen = socket

        while socket is not None:
            try:
                data = socket.recv(1024)
                if not data:
                    break
                print("Mensaje recibido pasivamente")
                print(data.decode())
            except:
                pass

          
