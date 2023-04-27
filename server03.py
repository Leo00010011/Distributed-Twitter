import socket
from socket import AF_INET, SOCK_STREAM
from threading import Thread
import utils
from utils import MSG_TO_SERVER, CLIENT_PASIVE_LISTEN_SUBSCRIBE, CLIENT_PASIVE_LISTEN_UNSUBSCRIBE
from utils import PORT_GENERAL

class Server():

    def __init__(self) -> None:
        self.HOST = "0.0.0.0"
        self.PORT = PORT_GENERAL
        self.socket_server = None

        self.runing = False        
        
        self.list_clients_pasive_listen  = {}

    def general_listen(self):
        if self.runing:
            return
        self.runing = True
        s = socket.socket(family= AF_INET, type= SOCK_STREAM)
        self.socket_server = s
        s.bind((self.HOST, self.PORT))
        s.listen(1)

        while self.runing:
            (socket_client, addr_client) = s.accept()
            data = socket_client.recv(1024)
            self.switch(socket_client, addr_client, data)
            

    def switch(self, socket_client, addr_client, data_bytes):
        '''
        Interprete y verificador de peticiones generales.
        Revisa que la estructura de la peticion sea adecuada,
        e interpreta la orden dada, redirigiendo el flujo de
        ejecucion interno del Server.
        '''
        data_dict = utils.decode(data_bytes)
        type_rqst = data_dict["type"]
        if type_rqst == MSG_TO_SERVER:
            if "msg" not in data_dict.keys():
                print("Peticion tipo MSG_TO_SERVER mal estruturada.")
                return
            self.msg_to_server(socket_client,addr_client, data_dict)
        elif type_rqst == CLIENT_PASIVE_LISTEN_SUBSCRIBE:
            self.client_pasive_listen_subscribe(socket_client, addr_client)
        elif type_rqst == CLIENT_PASIVE_LISTEN_UNSUBSCRIBE:
            self.client_pasive_listen_unsubscribe(socket_client, addr_client)
        
    def msg_to_server(self, socket_client, addr_client, data_dict):
        '''
        Mensaje directo al servidor, desde un cliente. Imprime el mensaje en la
        consola del Servidor, mostrando el IP:PORT del cliente y el mensaje.
        '''
        print("Conexion establecida con:\n"+
            f"Cliente:{addr_client[0]}\n"+
            f"Puerto:{addr_client[1]}\n"+
            f"Mensaje:{data_dict['msg']}")
        socket_client.send(b"OK")
        socket_client.close()

    def client_pasive_listen_subscribe(self, socket_client: socket.socket, addr_client):
        self.list_clients_pasive_listen[addr_client] = socket_client
        print(f"Cliente {addr_client[0]}:{addr_client[1]} subscrito")
        socket_client.send(b"SUBOK")
        print        

    def client_pasive_listen_unsubscribe(self, socket_client, addr_client):
        client = self.list_clients_pasive_listen.pop(addr_client[0], None)
        if client is None:
            print(f"El Cliente {client[0]}:{client[1]} no estaba subscrito")
        else:
            client[1].close()
            print(f"El Cliente {client[0]}:{client[1]} eliminado subscrito")        
        socket_client.send(b"UNSUBOK")

    def msg(self):        
        for addr_client, socket_client in self.list_clients_pasive_listen.items():            
            socket_client.send(b"Hola desde el server")


    def stop(self):
        self.runing = False
        self.socket_server.close()

