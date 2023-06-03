import socket
from socket import AF_INET, SOCK_STREAM
from threading import Thread, Event
import hashlib


try:
    import util
    from server import Server
    from util import Stalker, Dispatcher
    from util import CHORD, CLIENT, ENTRY_POINT, LOGGER,LOGIN_REQUEST, LOGIN_RESPONSE, NEW_LOGGER_RESPONSE, NEW_LOGGER_REQUEST, CHORD_RESPONSE, GET_TOKEN, CHORD_REQUEST, ALIVE_REQUEST, ALIVE_RESPONSE, REGISTER_REQUEST, REGISTER_RESPONSE
    from util import TRANSFERENCE_REQUEST, TRANSFERENCE_RESPONSE, TRANSFERENCE_OVER, LOGOUT_REQUEST, LOGOUT_RESPONSE, REGISTER_RESPONSE, CHORD_PORT
    import view
    from threaded_server import MultiThreadedServer
except:
    import API.util as util
    from API.server import Server
    from API.util import Stalker, Dispatcher
    from API.util import CHORD, CLIENT, ENTRY_POINT, LOGGER,LOGIN_REQUEST, LOGIN_RESPONSE, NEW_LOGGER_RESPONSE, NEW_LOGGER_REQUEST, CHORD_RESPONSE, GET_TOKEN, CHORD_REQUEST, ALIVE_REQUEST, ALIVE_RESPONSE, REGISTER_REQUEST, REGISTER_RESPONSE
    from API.util import TRANSFERENCE_REQUEST, TRANSFERENCE_RESPONSE,TRANSFERENCE_OVER, LOGOUT_REQUEST, LOGOUT_RESPONSE, REGISTER_RESPONSE, CHORD_PORT
    import API.view as view
    from API.threaded_server import MultiThreadedServer


class LoggerServer(MultiThreadedServer):
    
    def __init__(self,port: int, task_max: int, thread_count: int, timout: int):

        MultiThreadedServer.__init__(self,port, task_max, thread_count, timout, LoggerServer.switch)

    def switch(id:int, task, event:Event, storage):
        '''
        Interprete y verificador de peticiones generales.
        Revisa que la estructura de la peticion sea adecuada,
        e interpreta la orden dada, redirigiendo el flujo de
        ejecucion interno del Server.
        ---------------------------------------
        `data_dict['type']`: Tipo de peticion
        '''
        print('Entre al switch logger')
        (socket_client, addr_client) = task
        data_bytes = socket_client.recv(1024)
        
        try:
            data_dict = util.decode(data_bytes)
            type_rqst = data_dict["type"]       
            proto_rqst = data_dict["proto"]
            print(data_dict)
        except Exception as e:
            print(e)
            return
        
        if type_rqst == ENTRY_POINT:
            if proto_rqst == LOGIN_REQUEST:
                LoggerServer.login_request(socket_client, addr_client, data_dict,storage)
            elif proto_rqst == NEW_LOGGER_RESPONSE: 
                pass #TODO 
            elif proto_rqst == ALIVE_REQUEST:
                LoggerServer.alive_request(socket_client, addr_client, data_dict)
            elif proto_rqst == REGISTER_REQUEST:
                LoggerServer.register_request(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == LOGOUT_REQUEST:
                LoggerServer.logout_request(socket_client, addr_client, data_dict,storage)
        
        elif type_rqst == LOGGER:
            if proto_rqst == CHORD_RESPONSE:
                LoggerServer.chord_response(socket_client, addr_client, data_dict,storage)
            elif proto_rqst == LOGIN_REQUEST:
                LoggerServer.get_token(socket_client, addr_client, data_dict)
            elif proto_rqst in  (LOGIN_RESPONSE,REGISTER_RESPONSE, LOGIN_RESPONSE): 
                LoggerServer.set_data(socket_client, addr_client, data_dict,storage)
            elif proto_rqst == REGISTER_REQUEST:
                LoggerServer.get_register(socket_client, addr_client, data_dict)
            elif proto_rqst == TRANSFERENCE_REQUEST:
                LoggerServer.data_transfer_request(socket_client, addr_client, data_dict)
            elif proto_rqst == TRANSFERENCE_RESPONSE:
                LoggerServer.data_transfer_response(socket_client, addr_client, data_dict)
            elif proto_rqst == TRANSFERENCE_OVER:
                LoggerServer.data_transfer_over(socket_client, addr_client, data_dict)
            elif proto_rqst == LOGOUT_REQUEST:
                LoggerServer.get_logout(socket_client, addr_client, data_dict)
        
        else: 
            pass
        #TODO error de tipo
        

    def register_request(socket_client, addr_client, data_dict, storage):
        '''
        Registrar a un usuario en la red social
        ------------------------------------
        `data_dict['name']`: Nombre de usuario
        `data_dict['nick']`: Alias de usuario
        `data_dict['password']`: Contrasenna
        '''
  
        #pedir un evento para m\'aquina de estado 
        state = storage.insert_state()

        #Hay que usar Chord para ver quien tiene a ese Nick
        nick = data_dict['nick']
        data = {
                "type" : LOGGER,
                "proto": CHORD_REQUEST,
                "hash": nick,
                "ID_request": state.id
        } #Construir la peticion del chord

        skt = socket.socket(AF_INET,SOCK_STREAM)
        skt.connect(('127.0.0.1',8023))
        skt.send(util.encode(data))
        
        w = state.hold_event.wait(5)
        state = storage.get_state(state.id)
        storage.delete_state(state.id)

        if w:
            #Escribirle al server que tiene al usuario
            state2 = storage.get_state()
            data = {
                "type": LOGGER,
                "proto": REGISTER_REQUEST,
                "nick": data_dict["nick"],
                "password": data_dict["password"],
                "ID_request": state2.id,
            }
            skt = socket.socket(AF_INET,SOCK_STREAM)
            skt.connect((state.desired_data['IP'],8023))
            skt.send(util.encode(data))

            w = state2.event_holder.wait(5)
            state = storage.get_state(state2.id)
            storage.delete_state(state.id)
            
            if w:
                #reenviar mensaje de autenticacion
                try:
                    socket_client.send(util.encode(state.desired_data))
                    socket_client.close()
                except:
                    pass

        data = {
                    'type':LOGGER,
                    'proto': REGISTER_RESPONSE,
                    'succesed': False,
                    'token': None,
                    'error': 'Something went wrong in the network connection',
           }
        socket_client.send(util.encode(data))
        socket_client.close()
    
    def login_request(socket_client, addr_client, data_dict, storage):
        '''
        Solicitud de inicio de sesion de usuario
        -------------
        `data_dict['nick']`: Nick
        `data_dict['password']`: Contrasenna
        '''
        #pedir un evento para m\'aquina de estado
        print('Entre al loggin request') 
        state = storage.insert_state()

        #Hay que usar Chord para ver quien tiene a ese Nick
        nick = data_dict['nick']
        data = {
                "type" : LOGGER,
                "ptoto": CHORD_REQUEST,
                "Hash": nick,
                "ID_request": state.id
        } #Construir la peticion del chord
        
        skt = socket.socket(AF_INET,SOCK_STREAM)
        skt.connect(('127.0.0.1',CHORD_PORT))
        skt.send(util.encode(data))
        print('mande el chord')
        
        w = state.hold_event.wait(5)
        state = storage.get_state(state.id)
        storage.delete_state(state.id)
        if w:
            print('chord seteado')
            #Escribirle al server que tiene al usuario
            state2 = storage.get_state()
            data = {
                "type": LOGGER,
                "proto": LOGIN_REQUEST,
                "nick": data_dict["nick"],
                "password": data_dict["password"],
                "ID_request": state2.id,
            }
            skt = socket.socket(AF_INET,SOCK_STREAM)
            skt.connect((state.desired_data['IP'],8023))
            skt.send(util.encode(data))

            w = state2.event_holder.wait(5)
            state = storage.get_state(state2.id)
            storage.delete_state(state.id)
            
            if w:
                #reenviar mensaje de autenticacion
                try:
                   socket_client.send(util.encode(state.desired_data))
                   socket_client.close()
                   return
                except:
                    pass
        print('chord wait terminado')
        data = {
                'type':LOGGER,
                'proto': LOGIN_RESPONSE,
                'succesed': False,
                'token': None,
                'error': 'Something went wrong in the network connection',
           }
        socket_client.send(util.encode(data))
        socket_client.close()

    def logout_request(socket_client, addr_client, data_dict, storage):
        state = storage.insert_state()

        #Hay que usar Chord para ver quien tiene a ese Nick
        nick = data_dict['nick']
        data = {
                "type" : LOGGER,
                "ptoto": CHORD_REQUEST,
                "Hash": nick,
                "ID_request": state.id
        } #Construir la peticion del chord
        
        skt = socket.socket(AF_INET,SOCK_STREAM)
        skt.connect(('127.0.0.1',8023))
        skt.send(util.encode(data))
        
        w = state.hold_event.wait(5)
        state = storage.get_state(state.id)
        storage.delete_state(state.id)
        
        if w:
            #Escribirle al server que tiene al usuario
            state2 = storage.get_state()
            data = {
                "type": LOGGER,
                "proto": LOGOUT_REQUEST,
                "nick": data_dict["nick"],
                "password": data_dict["password"],
                "ID_request": state2.id,
            }
            skt = socket.socket(AF_INET,SOCK_STREAM)
            skt.connect((state.desired_data['IP'],8023))
            skt.send(util.encode(data))

            w = state2.event_holder.wait(5)
            state = storage.get_state(state2.id)
            storage.delete_state(state.id)
            
            if w:
                #reenviar mensaje de autenticacion
                try:
                   socket_client.send(util.encode(state.desired_data))
                   socket_client.close()
                except:
                    pass

        data = {
                'type':LOGGER,
                'proto': LOGOUT_RESPONSE,
                'succesed': False,
                'token': None,
                'error': 'Something went wrong in the network connection',
           }
        socket_client.send(util.encode(data))
        socket_client.close()

    def chord_response(socket_client, addr_client, data_dict, storage):
        '''
        Contactar directamente con el Logger que contiene el loggeo de un usuario 
        -------------
        `data_dict['IP']`: IP al que escribir
        `data_dict['IDrequest']`: Configuracion del ususario
        '''

        state = storage.get_state(data_dict['IDrequest'])
        

        data = {
            "IP": data_dict['IP'],
        }
        state.desired_data = data
        socket_client.close()
        state.hold_event.set()

    def get_register(socket_client, addr_client, data_dict):
        '''
        Registrar al usuario
        -------------
        `data_dict['nick']`: Nick
        `data_dict['Password']`: Password
        `data_dict['name']`: Name
        ''' 
        nick = data_dict['nick']
        
        if view.CheckUserAlias(nick) in None:
            password = data_dict["password"]
            name = data_dict['name']
            try: 
                view.CreateUser(name, nick, hashlib.sha1(bytes(password)).hexdigest(), hashlib.sha1(bytes(nick)).hexdigest())
                data = {
                    'type': LOGGER,
                    'proto': REGISTER_RESPONSE,
                    'succesed': True,
                    'error': None,
                    'ID_request': data_dict['ID_request']
                }
            except:
                data = {
                    'type': LOGGER,
                    'proto': REGISTER_RESPONSE,
                    'succesed': False,
                    'error': 'Error trying to register',
                    'ID_request': data_dict['ID_request']
                }
        else:
            data = {
                    'type': LOGGER,
                    'proto': REGISTER_RESPONSE,
                    'succesed': False,
                    'error': 'User Nick must be unique',
                    'ID_request': data_dict['ID_request']
                }
        
        socket_client.send(util.encode(data))
        socket_client.close()  

    def set_data(socket_client, addr_client, data_dict, storage):
        Id = data_dict["ID_request"]
        state = storage.get_state(Id)
   
        state.desired_data = data_dict
        state.hold_event.set()
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
            Token = view.LogIn(nick,hashlib.sha1(bytes(password)).hexdigest())
            if Token:
                data={
                    'type': LOGGER,
                    'proto': LOGIN_RESPONSE,
                    'succesed': True,
                    'token': Token,
                    'error': None,
                    'ID_request': data_dict['ID_request']
                }
            else:
                data={
                    'type': LOGGER,
                    'proto': LOGIN_RESPONSE,
                    'succesed': False,
                    'token': None,
                    'error': "Invalid nick or password",
                    'ID_request': data_dict['ID_request']
                }     
        except:
                data={
                    'type': LOGGER,
                    'proto': LOGIN_RESPONSE,
                    'succesed': False,
                    'token': None,
                    'error': "User not register",
                    'ID_request': data_dict['ID_request']
                }
        
        socket_client.send(util.encode(data))
        socket_client.close()

    def get_logout(socket_client, addr_client, data_dict):
        nick = data_dict["nick"]
        token = data_dict["token"]
        if view.CheckToken(token, nick):
            if view.RemoveToken(nick, token):
                data ={
                    'type':LOGGER,
                    'proto': LOGOUT_REQUEST,
                    'succesed': True,
                    'error': None
                }
            else:
                data ={
                    'type':LOGGER,
                    'proto': LOGOUT_REQUEST,
                    'succesed': False,
                    'error': "Error removing login"
                }
        else:
            data = {
                    'type':LOGGER,
                    'proto': LOGOUT_REQUEST,
                    'succesed': False,
                    'error': "Invalid user session data"
                }
        
        socket_client.send(util.encode(data))
        socket_client.close()

    def alive_request(socket_client, addr_client, data_dict):
        data = {
            'type': LOGGER,
            'proto': ALIVE_RESPONSE
        }
        socket_client.send(util.encode(data))
        socket_client.close()

    def data_transfer_request(socket_client, addr_client, data_dict):
        """
        Peticion de transferencia de datos
        datadict['number']: Numero de bloques enviados y recibidos
        datadict['chord_id']: Nuemro a partir del cual buscar
        """

        number = data_dict['number']
        hash_limit = data_dict['chord_id']

        user_data = view.GetUserPaswordRange(hash_limit, (number+1) * 10,10)
        data = {
            'type': LOGGER,
            'proto': TRANSFERENCE_RESPONSE,
            'number': number +1,
            'chord_id': hash_limit
        }

        i = 0
        for user in user_data:
            data[f"name_{i}"] = user.name
            data[f'password_{i}'] = user.password
            data[f"nick_{i}"] = user.alias
            i+=1
        
        if i < 10:
            data['over'] = True
        else: 
            data['over'] = False

        socket_client.send(util.encode(data))
        socket_client.close()

    def data_transfer_response(socket_client, addr_client, data_dict):        
        
        for i in range(10):
            name = data_dict.get(f'name_{i}', None)
            password = data_dict.get(f'password_{i}', None)
            nick = data_dict.get(f'nick_{i}', None)

            if name is None or password is None or nick is None: break

            view.CreateUser(name, nick, password, hashlib.sha1(bytes(nick)).hexdigest())

        if data_dict['over']:
            data = {
                'type': LOGGER,
                'proto': TRANSFERENCE_OVER,
                'chord_id': data_dict['chord_id'],
                'replication': False
            }
        else:
            data = {
                'type': LOGGER,
                'proto': TRANSFERENCE_REQUEST,
                'chord_id': data_dict['chord_id'],
                'number':data_dict['number']
            }
        socket_client.send(util.encode(data))
        socket_client.close()
            
    def data_transfer_over(socket_client, addr_client, data_dict):
        if not data_dict['replication']:
            limit  = data_dict['chord_id']
            view.DeleteUserRange(limit)
        
        socket_client.close()


          