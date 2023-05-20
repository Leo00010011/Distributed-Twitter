import socket
from socket import AF_INET, SOCK_STREAM
from threading import Thread

try:
    import util
    from server import Server
    from util import CLIENT, ENTRY_POINT, LOGGER,LOGIN_REQUEST, LOGIN_RESPONSE, NEW_LOGGER_RESPONSE, NEW_LOGGER_REQUEST
    import view
except:
    import API.util as util
    from API.server import Server
    from API.util import CLIENT, ENTRY_POINT, LOGGER,LOGIN_REQUEST, LOGIN_RESPONSE
    import API.view as view

class EntryPointServer(Server):

    def __init__(self) -> None:
        super().__init__()
        self.ID_actual = 0
        self.loggers_list = []
        self.entry_points = []
    

        

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
            type_msg = data_dict["type"]
            protocol = data_dict["proto"]
            data = data_dict["data"]
        except Exception as e:
            print(e)
            return
        
        if type_msg == CLIENT:
            if protocol == LOGIN_REQUEST:
                self.login_request_from_client(socket_client, addr_client, data)
        elif type_msg == ENTRY_POINT:
            pass
        elif type_msg == LOGGER:
            if protocol == LOGIN_RESPONSE:
                self.login_response_from_logger(socket_client, addr_client, data)
            elif protocol == NEW_LOGGER_REQUEST:
                self.new_logger_request_from_logger(socket_client, addr_client, data)
        else:
            pass

    def add_id_request(self):
        pass

#   ---------     RECV MESSAGE     -----------   #

    def login_request_from_client(self, socket_client, addr_client, data_dict):
        nick = data_dict['nick']
        password = data_dict['password']

        self.add_id_request()

        message = {
            'type': ENTRY_POINT,
            'proto': LOGIN_REQUEST,
            'nick': nick,
            'password': password,
            'ID_request': 0
        }

        self.login_request_to_logger()

    def login_response_from_logger(self, socket_client, addr_client, data_dict):
        pass

    def new_logger_request_from_logger(self, socket_client, addr_client, data_dict):
        IP_origin = data_dict['IP_origin']

        if IP_origin in self.loggers_list:
            return
        else:
            self.loggers_list.append(IP_origin)          




#   ---------     SEND MESSAGE     -----------   #

    def login_request_to_logger(self):
        pass

    def login_response_to_client(self):
        pass

    def new_logger_response_to_logger(self):
        pass
    
