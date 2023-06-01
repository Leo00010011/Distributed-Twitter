import socket
from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread, Event
import random as rand

try:
    import util
    from threaded_server import MultiThreadedServer
    from server import Server
    from util import Stalker, Dispatcher
    from util import CLIENT, ENTRY_POINT, LOGGER,LOGIN_REQUEST, LOGIN_RESPONSE, NEW_LOGGER_RESPONSE, NEW_LOGGER_REQUEST, REGISTER_RESPONSE, REGISTER_REQUEST
    import view
except:
    import API.util as util
    from API.threaded_server import MultiThreadedServer
    from API.server import Server
    from API.util import Stalker, Dispatcher
    from API.util import CLIENT, ENTRY_POINT, LOGGER,LOGIN_REQUEST, LOGIN_RESPONSE, NEW_LOGGER_RESPONSE, NEW_LOGGER_REQUEST, REGISTER_RESPONSE, REGISTER_REQUEST
    import API.view as view
    
class EntryPointServerTheaded(MultiThreadedServer):

    def __init__(self, port: int, task_max: int, thread_count: int, timeout: int, parse_func):
        super().__init__(port, task_max, thread_count, timeout, parse_func)
        self.stalker_loggers = Stalker(ENTRY_POINT)                        

    def dispatcher(self):
        l = self.stalker_loggers.list
        i = rand.randint(0,min(len(l),5))
        return self.stalker_loggers[i][1]

    def switch(self, id:int,task: tuple[socket,object],event:Event):

        try:
            data_bytes = socket.recv(1024)
            data_dict = util.decode(data_bytes)
            type_msg = data_dict["type"]
            protocol = data_dict["proto"]
            data = data_dict["data"]
        except Exception as e:
            print(e)
            return
        
        if type_msg == CLIENT:
            if protocol == LOGIN_REQUEST:
                self.login_request_from_client(id, task, event, data)
        elif type_msg == ENTRY_POINT:
            pass
        elif type_msg == LOGGER:
            if protocol == LOGIN_RESPONSE:
                self.login_response_from_logger(id, task, event, data)
            elif protocol == NEW_LOGGER_REQUEST:
                self.new_logger_request_from_logger(socket_client, addr_client, data)
        else:
            pass

    def login_request_from_client(self, id:int,task: tuple[socket,object],event:Event, data: dict):        

        nick = data['nick']
        password = data['password']

        state = self.storage.insert_state()
        message = {
            'type': ENTRY_POINT,
            'proto': LOGIN_REQUEST,
            'nick': nick,
            'password': password,
            'id_request': state.id
        }

        s = socket.socket(AF_INET, SOCK_STREAM)
        ip_logger = self.dispatcher()
        s.connect((ip_logger, 8040))
        data_bytes = util.encode(message)
        s.send(data_bytes)
        new_data_bytes = s.recv(1024)
        s.close()

        if event.wait(10):
            state = self.storage.get_state(state.id)
            if state is None:
                #TODO ver que pasa aqui !!!!!!!!!!
                task[0].close()
                return

            if state.desired_data['succesed']:
                msg = {
                    'type': ENTRY_POINT,
                    'proto': LOGIN_RESPONSE,
                    'succesed': True,
                    'token': state.desired_data['token'],
                    'error': None
                }
            else:
                msg = {
                    'type': ENTRY_POINT,
                    'proto': LOGIN_RESPONSE,
                    'succesed': False,
                    'token': None,
                    'error': state.desired_data['error']
                }
        else:
            msg = {
                'type': ENTRY_POINT,
                'proto': LOGIN_RESPONSE,
                'succesed': False,
                'token': None,
                'error': 'Tiempo de espera agotado.'
            }

        task[0].send(util.encode(msg))
        task[0].close()
        self.storage.delete_state(state.id)

    def login_response_from_logger(self, id:int,task: tuple[socket,object],event:Event, data: dict):

        self.stalker_loggers.update_IP(task[1][0])
        state = self.storage.get_state(data['id_request'])
        task[0].close()
        state.desired_data = data
        state.hold_event.set()

    def register_request_from_client(self, id:int,task: tuple[socket,object],event:Event, data: dict):        

        name = data['name']
        nick = data['nick']
        password = data['password']

        state = self.storage.insert_state()
        message = {
            'type': ENTRY_POINT,
            'proto': REGISTER_REQUEST,
            'name': name,
            'nick': nick,
            'password': password,
            'id_request': state.id
        }

        s = socket.socket(AF_INET, SOCK_STREAM)
        ip_logger = self.dispatcher()
        s.connect((ip_logger, 8040))
        data_bytes = util.encode(message)
        s.send(data_bytes)
        new_data_bytes = s.recv(1024)
        s.close()

        if event.wait(10):
            state = self.storage.get_state(state.id)
            if state is None:
                #TODO ver que pasa aqui !!!!!!!!!!
                task[0].close()
                return

            if state.desired_data['succesed']:
                msg = {
                    'type': ENTRY_POINT,
                    'proto': REGISTER_RESPONSE,
                    'succesed': True,                    
                    'error': None
                }
            else:
                msg = {
                    'type': ENTRY_POINT,
                    'proto': LOGIN_RESPONSE,
                    'succesed': False,                    
                    'error': state.desired_data['error']
                }
        else:
            msg = {
                'type': ENTRY_POINT,
                'proto': LOGIN_RESPONSE,
                'succesed': False,                
                'error': 'Tiempo de espera agotado.'
            }

        task[0].send(util.encode(msg))
        task[0].close()
        self.storage.delete_state(state.id)

    def register_response_from_logger(self, id:int,task: tuple[socket,object],event:Event, data: dict):

        self.stalker_loggers.update_IP(task[1][0])
        state = self.storage.get_state(data['id_request'])
        task[0].close()
        state.desired_data = data
        state.hold_event.set()


    def new_logger_request_from_logger(self, id:int,task: tuple[socket,object],event:Event, data: dict):

        IP_origin = data['IP_origin']
        self.stalker_loggers.extract_IP(task[1][0])
        ip_logger = self.stalker_loggers.recommended_dir()
        self.stalker_loggers.update_IP(task[1][0])

        msg = {
                'type': ENTRY_POINT,
                'proto': NEW_LOGGER_RESPONSE,
                'ip': ip_logger
            }
        
        task[0].send(util.encode(msg))
        task[0].close()
        


