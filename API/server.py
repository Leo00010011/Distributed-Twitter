import socket
from socket import AF_INET, SOCK_STREAM
from threading import Thread

try:
    import util
    from util import PORT_GENERAL
    import view
except:
    import API.util as util
    from API.util import PORT_GENERAL
    import API.view as view
class Server():

    def __init__(self) -> None:
        self.HOST = "0.0.0.0"
        self.PORT = PORT_GENERAL
        

    def general_listen(self):
        if self.runing:
            return
        self.runing = True
        s = socket.socket(family= AF_INET, type= SOCK_STREAM)
        self.socket_server = s
        s.bind((self.HOST, self.PORT))
        s.listen(1) #TODO Considerar en cambiar este numero

        while self.runing:
            (socket_client, addr_client) = s.accept()
            data = socket_client.recv(1024)
            t = Thread(target=self.switch_no_sign, args= [socket_client, addr_client, data])
            t.start()
            

    def switch(self, socket_client, addr_client, data_bytes):
        '''
        Interprete y verificador de peticiones generales.
        Revisa que la estructura de la peticion sea adecuada,
        e interpreta la orden dada, redirigiendo el flujo de
        ejecucion interno del Server.
        ---------------------------------------
        `data_bytes['type']`: Tipo de peticion
        '''
        try:
            data_dict = util.decode(data_bytes)        
            type_rqst = data_dict["type"]
        except Exception as e:
            print(e)
            return
        
        #TODO
        # Implementar la seleccion de que accion realizar
        raise NotImplementedError()
        
