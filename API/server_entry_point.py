import socket
from socket import AF_INET, SOCK_STREAM
from threading import Thread, Event
import random as rand
import time

try:
    import util
    from threaded_server import MultiThreadedServer    
    from util import Stalker, Dispatcher
    from util import PORT_GENERAL_ENTRY, PORT_GENERAL_LOGGER
    from util import CLIENT, ENTRY_POINT, LOGGER,LOGIN_REQUEST, LOGIN_RESPONSE,\
        NEW_LOGGER_RESPONSE, NEW_LOGGER_REQUEST, REGISTER_RESPONSE, REGISTER_REQUEST,\
        CREATE_TWEET_REQUEST, CREATE_TWEET_RESPONSE, PROFILE_REQUEST, PROFILE_RESPONSE,\
        FOLLOW_REQUEST,FOLLOW_RESPONSE, LOGOUT_REQUEST, LOGOUT_RESPONSE, ALIVE_REQUEST,\
        ALIVE_RESPONSE, ADD_LOGGER, REMOVE_LOGGER, ADD_ENTRY, REMOVE_ENTRY
except:
    import API.util as util
    from API.threaded_server import MultiThreadedServer    
    from API.util import Stalker, Dispatcher
    from API.util import PORT_GENERAL_ENTRY, PORT_GENERAL_LOGGER
    from API.util import CLIENT, ENTRY_POINT, LOGGER,LOGIN_REQUEST, LOGIN_RESPONSE,\
        NEW_LOGGER_RESPONSE, NEW_LOGGER_REQUEST, REGISTER_RESPONSE, REGISTER_REQUEST,\
        CREATE_TWEET_REQUEST, CREATE_TWEET_RESPONSE, PROFILE_REQUEST, PROFILE_RESPONSE,\
        FOLLOW_REQUEST,FOLLOW_RESPONSE, LOGOUT_REQUEST, LOGOUT_RESPONSE, ALIVE_REQUEST,\
        ALIVE_RESPONSE, ADD_LOGGER, REMOVE_LOGGER, ADD_ENTRY, REMOVE_ENTRY
    
class EntryPointServerTheaded(MultiThreadedServer):

    def __init__(self, port: int, task_max: int, thread_count: int, timeout: int):
        super().__init__(port, task_max, thread_count, timeout, self.switch)
        self.stalker_loggers = Stalker(LOGGER)
        self.stalker_entrys = Stalker(ENTRY_POINT)  
        self.verbose = True
        self.execute_pending_tasks = False
        self.stalking_entrys = False
        self.stalking_loggers = False
        self.executing = False
        self.pending_tasks = {}
        self.my_ip = socket.gethostbyname(socket.gethostname())

        with open('entrys.txt', 'r') as ft:
            for ip in ft.read().split(sep='\n'):
                if ip == self.my_ip:
                    continue
                self.stalker_entrys.update_IP(ip)
                self.pending_tasks[ip] = []
        

    def start(self):
        self.end_event.clear()
        t1 = Thread(target= self.start_server) 
        t2 = Thread(target= self.send_pending_tasks, args= [self.end_event])
        t3 = Thread(target= self.alive_request_to_entry_point, args= [self.end_event])
        t4 = Thread(target= self.alive_request_to_logger, args= [self.end_event])
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        self.executing = True
    
    def stop(self):
        self.end_event.set()
        while self.execute_pending_tasks or self.current_thread_count != 0 \
            or self.stalking_entrys or self.stalking_loggers:
            pass
        self.executing = False

    def print(self, *str):
        if self.verbose:
            print(*str)

    def dispatcher_loggers(self):        
        l = [ip for _, ip in self.stalker_loggers.listl[max(-5,-len(l)):]]
        rand.shuffle(l)
        return l
    
    def add_task(self, new_task):
        for ip, tasks in self.pending_tasks.items():
            repeat_task = False
            for task in tasks:
                if task == new_task:
                    repeat_task = True
                    break
            if repeat_task:
                continue
            self.pending_tasks[ip] = new_task
    
    def send_pending_tasks(self, event: Event):
        self.execute_pending_tasks = True
        time.sleep(rand.randint(3,30))
        while not event.is_set():
            for ip, tasks in self.pending_tasks.items():
                for i, task in enumerate(tasks.copy()):
                    try:
                        msg = {
                            'type': ENTRY_POINT,
                            'proto': task[0],
                            'ip': task[1]
                        }
                        s = socket.socket(AF_INET, SOCK_STREAM)
                        s.connect((ip, PORT_GENERAL_ENTRY))
                        s.send(util.encode(msg))
                        s.close()
                        self.print(f'TAREA PENDIENTE "{task[0]}:{task[1]}" ENVIADA a {ip}:{PORT_GENERAL_ENTRY}')
                        tasks.pop(i)
                        time.sleep(rand.randint(1,5))
                    except:
                        self.print(f'TAREA PENDIENTE "{task[0]}:{task[1]}" NO enviada a {ip}:{PORT_GENERAL_ENTRY}')
            time.sleep(rand.randint(3,30))
        self.execute_pending_tasks = False
        print('END Pending Tasks')


    def switch(self, id:int,task: tuple[socket.socket,object],event:Event, storage):
        
        try:
            data_bytes = task[0].recv(10240)
            data = util.decode(data_bytes)            
            type_msg = data["type"]
            protocol = data["proto"]            
        except Exception as e:
            print(e)
            return
                
        if type_msg == CLIENT:
            if protocol == LOGIN_REQUEST:
                self.login_request_from_client(id, task, event, storage, data)
            elif protocol == REGISTER_REQUEST:
                self.register_request_from_client(id, task, event, storage, data)
            elif protocol == CREATE_TWEET_REQUEST:
                self.create_tweet_request_from_client(id, task, event, storage, data)
            elif protocol == PROFILE_REQUEST:
                self.profile_request_from_client(id, task, event, storage, data)
            elif protocol == LOGOUT_REQUEST:
                self.logout_request_from_client(id, task, event, storage, data)
            else:
                print('Q pifia metes?')
        elif type_msg == ENTRY_POINT:
            if protocol == ALIVE_REQUEST:                
                self.alive_response_to_entry_point(id, task, event, storage, data)
            else:
                print('Q pifia metes?')
        elif type_msg == LOGGER:
            if protocol == LOGIN_RESPONSE:
                self.login_response_from_logger(id, task, event, storage, data)
            elif protocol == REGISTER_RESPONSE:
                self.register_response_from_logger(id, task, event, storage, data)
            elif protocol == CREATE_TWEET_RESPONSE:
                self.create_tweet_response_from_logger(id, task, event, storage, data)
            elif protocol == PROFILE_RESPONSE:
                self.profile_response_from_logger(id, task, event, storage, data)
            elif protocol == LOGOUT_RESPONSE:
                self.logout_response_from_logger(id, task, event, storage, data)            
            else:
                print('Q pifia metes?')
        else:
            pass

    def try_send_logger(self, message):

        error = None        
        for ip in self.dispatcher_loggers():
            try:
                send_data = util.encode(message)
                s = socket.socket(AF_INET, SOCK_STREAM)                
                s.connect((ip, PORT_GENERAL_ENTRY))
                s.send(send_data)        
                s.close()
                return True, None
            except Exception as e:                
                print(f'Logger "{ip}" caido')                
                error = e
        return False, error
    
    
    #-------------------- LOGIN ----------------------#

    def login_request_from_client(self, id:int,task,event:Event, storage, data: dict):        

        self.print('LOGIN_REQUEST from CLIENT')
        nick = data['nick']
        password = data['password']

        state = storage.insert_state()
        message = {
            'type': ENTRY_POINT,
            'proto': LOGIN_REQUEST,
            'nick': nick,
            'password': password,
            'id_request': state.id
        }

        good, error = self.try_send_logger(message)
        if not good:            
            msg = {
                'type': ENTRY_POINT,
                'proto': LOGIN_RESPONSE,
                'succesed': False,                
                'error': 'Conexion con logger fallida'
            }
        elif state.hold_event.wait(10):
            state = storage.get_state(state.id)
            if state is None:
                #TODO ver que pasa aqui !!!!!!!!!!
                self.print('QUE VERGA! SIN state en LOGIN REQUEST')
                task[0].close()
                return

            if state.desired_data['succesed']:
                msg = {
                    'type': ENTRY_POINT,
                    'proto': LOGIN_RESPONSE,
                    'succesed': True,
                    'token': state.desired_data['token'],                    
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

        try:
            task[0].send(util.encode(msg))
            task[0].close()
            storage.delete_state(state.id)
            self.print('LOGIN RESPONSE TO CLIENT:\n',msg)
        except Exception as e:
            self.print('LOGIN RESPONSE to CLIENT (((ERRORR))):\n')
            self.print(e)

    def login_response_from_logger(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):

        self.print('LOGIN RESPONSE FROM LOGGER')
        self.stalker_loggers.update_IP(task[1][0])
        state = storage.get_state(data['id_request'])
        task[0].close()
        state.desired_data = data
        state.hold_event.set()

    #------------------ LOGOUT ------------------#

    def logout_request_from_client(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):        

        nick = data['nick']
        token = data['token']

        state = storage.insert_state()
        message = {
            'type': ENTRY_POINT,
            'proto': LOGOUT_REQUEST,
            'nick': nick,
            'token': token,
            'id_request': state.id
        }
                
        good, error = self.try_send_logger(message)
        if not good: 
            msg = {
                'type': ENTRY_POINT,
                'proto': LOGOUT_RESPONSE,
                'succesed': False,                
                'error': 'Conexion con logger fallida'
            }
        elif state.hold_event.wait(10):
            state = storage.get_state(state.id)
            if state is None:
                #TODO ver que pasa aqui !!!!!!!!!!
                self.print('QUE VERGA! SIN state en LOGOUT REQUEST')
                task[0].close()
                return

            if state.desired_data['succesed']:
                msg = {
                    'type': ENTRY_POINT,
                    'proto': LOGOUT_RESPONSE,
                    'succesed': True,
                    'error': None
                }
            else:
                msg = {
                    'type': ENTRY_POINT,
                    'proto': LOGOUT_RESPONSE,
                    'succesed': False,                    
                    'error': state.desired_data['error']
                }
        else:
            msg = {
                'type': ENTRY_POINT,
                'proto': LOGOUT_RESPONSE,
                'succesed': False,                
                'error': 'Tiempo de espera agotado.'
            }

        try:
            task[0].send(util.encode(msg))
            task[0].close()
            self.print('LOGOUT_RESPONSE TO CLIENT:\n',msg)
        except Exception as e:
            self.print('LOGOUT_RESPONSE to CLIENT (((ERRORR))):\n')
            self.print(e)
        storage.delete_state(state.id)

    def logout_response_from_logger(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):

        self.stalker_loggers.update_IP(task[1][0])
        state = storage.get_state(data['id_request'])
        task[0].close()
        state.desired_data = data
        state.hold_event.set()

    #-------------------- REGISTER ----------------------#

    def register_request_from_client(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):        

        name = data['name']
        nick = data['nick']
        password = data['password']

        state = storage.insert_state()
        message = {
            'type': ENTRY_POINT,
            'proto': REGISTER_REQUEST,
            'name': name,
            'nick': nick,
            'password': password,
            'id_request': state.id
        }

        good, error = self.try_send_logger(message)
        if not good: 
            msg = {
                'type': ENTRY_POINT,
                'proto': REGISTER_RESPONSE,
                'succesed': False,                
                'error': 'Conexion con logger fallida'
            }
        elif state.hold_event.wait(10):
            state = storage.get_state(state.id)
            if state is None:
                #TODO ver que pasa aqui !!!!!!!!!!
                self.print('QUE VERGA! SIN state en REGISTER REQUEST')
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
                    'proto': REGISTER_RESPONSE,
                    'succesed': False,                    
                    'error': state.desired_data['error']
                }
        else:
            msg = {
                'type': ENTRY_POINT,
                'proto': REGISTER_RESPONSE,
                'succesed': False,                
                'error': 'Tiempo de espera agotado.'
            }

        try:
            task[0].send(util.encode(msg))
            task[0].close()
            self.print('REGISTER_RESPONSE TO CLIENT:\n',msg)
        except Exception as e:
            self.print('REGISTER_RESPONSE to CLIENT (((ERRORR))):\n')
            self.print(e)
        storage.delete_state(state.id)

    def register_response_from_logger(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):

        self.stalker_loggers.update_IP(task[1][0])
        state = storage.get_state(data['id_request'])
        task[0].close()
        state.desired_data = data
        state.hold_event.set()


    def new_logger_request_from_logger(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):
        
        self.stalker_loggers.extract_IP(task[1][0])
        ip_logger = self.stalker_loggers.recommended_dir()
        self.stalker_loggers.update_IP(task[1][0])
        msg = {
            'type': ENTRY_POINT,
            'proto': NEW_LOGGER_RESPONSE,
            'ip': ip_logger
        }
        self.add_task((ADD_LOGGER, task[1][0]))        
        task[0].send(util.encode(msg))
        task[0].close()
        

    #-------------------- CREATE TWEET ----------------------#

    def create_tweet_request_from_client(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):        

        token = data['token']
        nick = data['nick']
        text = data['text']

        state = storage.insert_state()
        message = {
            'type': ENTRY_POINT,
            'proto': CREATE_TWEET_REQUEST,
            'token': token,
            'nick': nick,   
            'text': text,
            'id_request': state.id
        }

        good, error = self.try_send_logger(message)
        if not good: 
            msg = {
                'type': ENTRY_POINT,
                'proto': CREATE_TWEET_RESPONSE,
                'succesed': False,                
                'error': 'Conexion con logger fallida'
            }
        elif state.hold_event.wait(10):
            state = storage.get_state(state.id)
            if state is None:
                #TODO ver que pasa aqui !!!!!!!!!!
                self.print('QUE VERGA! SIN state en CREATE TWEET REQUEST')
                task[0].close()
                return

            if state.desired_data['succesed']:
                msg = {
                    'type': ENTRY_POINT,
                    'proto': CREATE_TWEET_RESPONSE,
                    'succesed': True,                    
                    'error': None
                }
            else:
                msg = {
                    'type': ENTRY_POINT,
                    'proto': CREATE_TWEET_RESPONSE,
                    'succesed': False,                    
                    'error': state.desired_data['error']
                }
        else:
            msg = {
                'type': ENTRY_POINT,
                'proto': CREATE_TWEET_RESPONSE,
                'succesed': False,                
                'error': 'Tiempo de espera agotado.'
            }

        try:
            task[0].send(util.encode(msg))
            task[0].close()
            self.print('CREATE_TWEET_RESPONSE TO CLIENT:\n',msg)
        except Exception as e:
            self.print('CREATE_TWEET_RESPONSE to CLIENT (((ERRORR))):\n')
            self.print(e)
        storage.delete_state(state.id)

    def create_tweet_response_from_logger(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):

        self.stalker_loggers.update_IP(task[1][0])
        state = storage.get_state(data['id_request'])
        task[0].close()
        state.desired_data = data
        state.hold_event.set()


    #-------------------- PROFILE ----------------------#

    def profile_request_from_client(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):        

        token = data['token']
        nick = data['nick']
        nick_profile = data['nick_profile']
        block = data['block']

        state = storage.insert_state()
        message = {
            'type': ENTRY_POINT,
            'proto': PROFILE_REQUEST,
            'token': token,
            'nick': nick,
            'nick_profile': nick_profile,
            'block': block,
            'id_request': state.id
        }

        good, error = self.try_send_logger(message)
        if not good:
            msg = {
                'type': ENTRY_POINT,
                'proto': PROFILE_RESPONSE,
                'succesed': False,                
                'error': 'Conexion con logger fallida'
            }
        elif state.hold_event.wait(10):
            state = storage.get_state(state.id)
            if state is None:
                #TODO ver que pasa aqui !!!!!!!!!!
                self.print('QUE VERGA! SIN state en PROFILE REQUEST')
                task[0].close()
                return

            if state.desired_data['succesed']:
                msg = {
                    'type': ENTRY_POINT,
                    'proto': PROFILE_RESPONSE,
                    'succesed': True,
                    'data_profile': state.desired_data['data_profile'],
                    'error': None
                }
            else:
                msg = {
                    'type': ENTRY_POINT,
                    'proto': PROFILE_RESPONSE,
                    'succesed': False,                    
                    'error': state.desired_data['error'],
                    'data_profile': None
                }
        else:
            msg = {
                'type': ENTRY_POINT,
                'proto': PROFILE_RESPONSE,
                'succesed': False,                
                'error': 'Tiempo de espera agotado.',
                'data_profile': None
            }

        try:
            task[0].send(util.encode(msg))
            task[0].close()
            self.print('PROFILE_RESPONSE TO CLIENT:\n',msg)
        except Exception as e:
            self.print('PROFILE_RESPONSE to CLIENT (((ERRORR))):\n')
            self.print(e)
        storage.delete_state(state.id)

    def profile_response_from_logger(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):

        self.stalker_loggers.update_IP(task[1][0])
        state = storage.get_state(data['id_request'])
        task[0].close()
        state.desired_data = data
        state.hold_event.set()

    #-------------------- FOLLOW ----------------------#

    def follow_request_from_client(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):
        
        token = data['token']
        nick = data['nick']
        nick_profile = data['nick_profile']        

        state = storage.insert_state()
        message = {
            'type': ENTRY_POINT,
            'proto': FOLLOW_REQUEST,
            'token': token,
            'nick': nick,
            'nick_profile': nick_profile,
            'id_request': state.id
        }

        good, error = self.try_send_logger(message)
        if not good:
            msg = {
                'type': ENTRY_POINT,
                'proto': FOLLOW_RESPONSE,
                'succesed': False,                
                'error': 'Conexion con logger fallida'
            }
        elif state.hold_event.wait(10):
            state = storage.get_state(state.id)
            if state is None:
                #TODO ver que pasa aqui !!!!!!!!!!
                self.print('QUE VERGA! SIN state en FOLLOW REQUEST')
                task[0].close()
                return

            if state.desired_data['succesed']:
                msg = {
                    'type': ENTRY_POINT,
                    'proto': FOLLOW_RESPONSE,
                    'succesed': True,                    
                    'error': None
                }
            else:
                msg = {
                    'type': ENTRY_POINT,
                    'proto': FOLLOW_RESPONSE,
                    'succesed': False,                    
                    'error': state.desired_data['error'],                    
                }
        else:
            msg = {
                'type': ENTRY_POINT,
                'proto': FOLLOW_RESPONSE,
                'succesed': False,                
                'error': 'Tiempo de espera agotado.',                
            }

        try:
            task[0].send(util.encode(msg))
            task[0].close()
            self.print('FOLLOW_RESPONSE TO CLIENT:\n',msg)
        except Exception as e:
            self.print('FOLLOW_RESPONSE to CLIENT (((ERRORR))):\n')
            self.print(e)
        storage.delete_state(state.id)


    def follow_response_from_logger(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):

        self.stalker_loggers.update_IP(task[1][0])
        state = storage.get_state(data['id_request'])
        task[0].close()
        state.desired_data = data
        state.hold_event.set()

    #------------------ ALIVE ------------------#

    def alive_request_to_entry_point(self, event:Event):

        msg_bytes = util.encode(self.stalker_entrys.msg_stalk())
        self.stalking_entrys = True
        time.sleep(rand.randint(20,60))
        while not event.is_set():
            dirs_to_stalk = self.stalker_entrys.dieds_dirs(30)
            print('STALKEANDO Entrys: ', dirs_to_stalk)
            for dir in dirs_to_stalk:
                try:
                    s = socket.socket(AF_INET, SOCK_STREAM)
                    s.connect((dir, PORT_GENERAL_ENTRY))
                    s.send(msg_bytes)
                    data = util.decode(s.recv(1024))                    
                    #TODO Verificar respuesta
                    s.close()
                    self.stalker_entrys.update_IP(dir)
                except:
                    self.print('ALIVE ENTRY Conexion perdida con: ', dir)
            time.sleep(rand.randint(20,60))
        self.stalking_entrys = False
        print('END Stalking Entrys')

    def alive_request_to_logger(self, event: Event):

        msg_bytes = util.encode(self.stalker_loggers.msg_stalk())
        self.stalking_loggers = True
        time.sleep(rand.randint(20,60))
        while not event.is_set():
            dirs_to_stalk = self.stalker_loggers.dieds_dirs(30)
            print('STALKEANDO Loggers: ', dirs_to_stalk)
            for dir in dirs_to_stalk:
                try:
                    s = socket.socket(AF_INET, SOCK_STREAM)
                    s.connect((dir, PORT_GENERAL_LOGGER))
                    s.send(msg_bytes)
                    data = util.decode(s.recv(1024))
                    #TODO Verificar respuesta
                    s.close()
                    self.stalker_loggers.update_IP(dir)
                except:
                    self.print('ALIVE LOGGER Conexion perdida con: ', dir)
            time.sleep(rand.randint(20,60))
        self.stalking_loggers = False
        print('END Stalking Loggers')


    def alive_response_to_entry_point(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):
        #TODO agregar condicional para cuando no este
        self.stalker_entrys.update_IP(task[1][0])
        task[0].send(util.encode({
            'type': ENTRY_POINT,
            'proto': ALIVE_RESPONSE
        }))
        task[0].close()
