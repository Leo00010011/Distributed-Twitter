import socket
from socket import AF_INET, SOCK_STREAM
from threading import Thread


try:
    import util
    from server import Server
    from util import Stalker, Dispatcher
    from util import CHORD, CLIENT, ENTRY_POINT, LOGGER,LOGIN_REQUEST, LOGIN_RESPONSE, NEW_LOGGER_RESPONSE, NEW_LOGGER_REQUEST, CHORD_RESPONSE, GET_TOKEN, CHORD_REQUEST, ALIVE_REQUEST, ALIVE_RESPONSE, REGISTER_REQUEST, REGISTER_RESPONSE
    import view
    from threaded_server import MultiThreadedServer
except:
    import API.util as util
    from API.server import Server
    from API.util import Stalker, Dispatcher
    from API.util import CHORD, CLIENT, ENTRY_POINT, LOGGER,LOGIN_REQUEST, LOGIN_RESPONSE, NEW_LOGGER_RESPONSE, NEW_LOGGER_REQUEST, CHORD_RESPONSE, GET_TOKEN, CHORD_REQUEST, ALIVE_REQUEST, ALIVE_RESPONSE, REGISTER_REQUEST, REGISTER_RESPONSE
    import API.view as view
    from API.threaded_server import MultiThreadedServer


class LoggerServer(MultiThreadedServer):
    
    def __init__(self,port: int, task_max: int, thread_count: int, timout: int, parse_func):

        MultiThreadedServer.__init__(self,port, task_max, thread_count, timout, LoggerServer.switch)
        self.ID  = 0
        self.list_clients_pasive_listen = {}


    def switch(id:int, task: tuple[socket,object], event:Event):
        '''
        Interprete y verificador de peticiones generales.
        Revisa que la estructura de la peticion sea adecuada,
        e interpreta la orden dada, redirigiendo el flujo de
        ejecucion interno del Server.
        ---------------------------------------
        `data_dict['type']`: Tipo de peticion
        '''
        (socket_client, addr_client) = task
        data_byte = socket_client.recv(1024)
        
        try:
            data_dict = util.decode(data_bytes)
            type_rqst = data_dict["type"]       
            proto_rqst = data_dict["proto"]
        except Exception as e:
            print(e)
            return
        
        if type_rqst == ENTRY_POINT:
            if proto_rqst == LOGIN_REQUEST:
                LoggerServer.login_request(socket_client, addr_client, data_dict)
            elif proto_rqst == NEW_LOGGER_RESPONSE: 
                pass #TODO 
            elif proto_rqst == ALIVE_REQUEST:
                pass #TODO
            elif proto_rqst == REGISTER_REQUEST:
                pass #TODO
        
        elif type_rqst == LOGGER:
            if proto_rqst == CHORD_RESPONSE:
                LoggerServer.chord_response(socket_client, addr_client, data_dict)
            elif proto_rqst == LOGIN_REQUEST:
                LoggerServer.get_token(socket_client, addr_client, data_dict)
            elif proto_rqst == LOGIN_RESPONSE: 
                LoggerServer.set_token(socket_client, addr_client, data_dict)
        
        else: 
            pass
        #TODO error de tipo
        

    def sign_up(socket_client, addr_client, data_dict):
        '''
        Registrar a un usuario en la red social
        ------------------------------------
        `data_dict['name']`: Nombre de usuario
        `data_dict['nick']`: Alias de usuario
        `data_dict['password']`: Contrasenna
        '''
  
        nick = data_dict['nick']        
        hashed = hash(nick)
        
   
        name = data_dict['name']
        password = data_dict['password']
        if view.CreateUser(name= name, alias=nick, password= password):
            return True
        else:
            #Algun tipo de error de alias ya existente
            pass
    
    def login_request(socket_client, addr_client, data_dict):
        '''
        Solicitud de inicio de sesion de usuario
        -------------
        `data_dict['nick']`: Nick
        `data_dict['password']`: Contrasenna
        '''
        #Guardar el cliente para cuando este la respuesta
        self.list_clients_pasive_listen[self.ID] = (socket_client, addr_client, data_dict)


        #Hay que usar Chord para ver quien tiene a ese Nick
        nick = data_dict['nick']
        data = {
                "type" : LOGGER,
                "ptoto": CHORD_REQUEST,
                "Hash": hash(nick),
                "ID_request": self.ID,
                "IP": self.socket_server
        } #Construir la peticion del chord
  

        self.ID +=1
        #Mandar el mensaje para iniciar el chord a la direccion que atiende esos pedidos
        self.chord_socket.send(util.encode(data))
    
    def chord_response(socket_client, addr_client, data_dict):
        '''
        Contactar directamente con el Logger que contiene el loggeo de un usuario 
        -------------
        `data_dict['IP']`: IP al que escribir
        `data_dict['IDrequest']`: Configuracion del ususario
        '''

        IDrequest = data_dict["ID_request"]
        _,_, info = self.list_clients_pasive_listen.get(IDrequest)
        
        data = {
            "type": LOGGER,
            "proto": LOGIN_REQUEST,
            "nick": info["nick"],
            "password": info["password"],
            "ID_request": self.socket_server,
        }

        socket_client.send(util.encode(dict))
        socket_client.close()

    def get_token(socket_client, addr_client, data_dict):
        '''
        Loggear al usuario
        -------------
        `data_dict['nick']`: Nick
        `data_dict['Password']`: Password
        ''' 
        nick = data_dict["nick"]
        password = data_dict["password"]
        try:
            Token = view.LogIn(nick, password)
            if Token:
                dict ={
                    'type': LOGGER,
                    'proto': LOGIN_RESPONSE,
                    'succesed': True,
                    'token': Token,
                    'error': None,
                    'ID_request': data_dict['ID_request']
                }
            else:
                dict ={
                    'type': LOGGER,
                    'proto': LOGIN_RESPONSE,
                    'succesed': False,
                    'token': None,
                    'error': "Invalid nick or password",
                    'ID_request': data_dict['ID_request']
                }     
        except:
                dict ={
                    'type': LOGGER,
                    'proto': LOGIN_RESPONSE,
                    'succesed': False,
                    'token': None,
                    'error': "User not register",
                    'ID_request': data_dict['ID_request']
                }
        socket_client.send(util.encode(dict))
        socket_client.close()

    def set_token(socket_client, addr_client, data_dict):
        
        Id = data_dict["ID_request"]
        try:
           socket,_,_ =  self.list_clients_pasive_listen.pop(Id)
           dict = {
            'type':LOGGER,
            'proto': LOGIN_RESPONSE,
            'succesed': data_dict['succesed'],
            'token': data_dict['token'],
            'error':data_dict['error'],
           }
           socket.send(util.encode(dict))
           socket.close()
        except:
            pass
    
    def alive_request(socket_client, addr_client, data_dict):
        dict = {
            'type': LOGGER,
            'proto': ALIVE_RESPONSE,
        }
        socket_client.send(util.encode(dict))
        socket_client.close()


class DataServer():
    def share_info(socket_client, addr_client, data_dict):
        hash_limit = data_dict['logger_id']
          