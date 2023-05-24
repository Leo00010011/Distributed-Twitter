import socket
from socket import AF_INET, SOCK_STREAM
from threading import Thread

try:
    import util
    from server import Server
    from util import Stalker, Dispatcher
    from util import CLIENT, ENTRY_POINT, LOGGER,LOGIN_REQUEST, LOGIN_RESPONSE, NEW_LOGGER_RESPONSE, NEW_LOGGER_REQUEST
    import view
except:
    import API.util as util
    from API.server import Server
    from API.util import Stalker, Dispatcher
    from API.util import CLIENT, ENTRY_POINT, LOGGER,LOGIN_REQUEST, LOGIN_RESPONSE
    import API.view as view

class EntryPointServer(Server):

    def __init__(self):
        Server.__init__(self)
        self.ID_actual = 0
        self.loggers_list = []
        self.entry_points = []
        self.dispatcher = Dispatcher()
        self.stalker = Stalker(ENTRY_POINT)

        

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

#   ---------     RECV MESSAGE     -----------   #

    def login_request_from_client(self, socket_client, addr_client, data_dict):
        nick = data_dict['nick']
        password = data_dict['password']

        id  = self.dispatcher.insert_petition(0)

        message = {
            'type': ENTRY_POINT,
            'proto': LOGIN_REQUEST,
            'nick': nick,
            'password': password,
            'ID_request': id
        }
        try:
            new_data_dict = self.login_request_to_logger(message)
            if new_data_dict['succesed'] == False:
                msg = {
                    'type': ENTRY_POINT,
                    'proto': LOGIN_RESPONSE,
                    'succesed': False,
                    'token': None,
                    'error': 'No existe'
                }
            else :
                msg = {
                    'type': ENTRY_POINT,
                    'proto': LOGIN_RESPONSE,
                    'succesed': True,
                    'token': new_data_dict['token'],
                    'error': None
                }
        except Exception as e:
            msg = {
                'type': ENTRY_POINT,
                'proto': LOGIN_RESPONSE,
                'succesed': False,
                'token': None,
                'error': 'Conexion cerrada'
            }            
        socket_client.send(util.encode(msg))
        socket_client.close()        
        


    def login_response_from_logger(self, socket_client, addr_client, data_dict):
        # Esto no lo deb'ia recibir abiertamente.
        self.dispatcher.extract_petition(data_dict['id_request'])
        msg = {
                'type': ENTRY_POINT,
                'proto': LOGIN_RESPONSE,
                'succesed': False,
                'token': None,
                'error': 'Socket equivocado'
            } 
        socket_client.send(util.encode(msg))
        socket_client.close()   

    def new_logger_request_from_logger(self, socket_client, addr_client, data_dict):
        IP_origin = data_dict['IP_origin']

        self.stalker.update_IP(addr_client)




#   ---------     SEND MESSAGE     -----------   #

    def login_request_to_logger(self, data_dict):
        s = socket.socket(AF_INET, SOCK_STREAM)
        s.connect((self.HOST, 8040))
        data_bytes = util.encode(data_dict)
        s.send(data_bytes)        
        new_data_bytes = s.recv(1024)
        s.close()
        new_data = util.decode(new_data_bytes)
        
        return new_data

    def login_response_to_client(self):
        pass

    def new_logger_response_to_logger(self):
        pass
    
