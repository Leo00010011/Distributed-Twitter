import socket
from socket import AF_INET, SOCK_STREAM
from threading import Thread, Event, Lock
import random as rand
import time

try:
    import util
    from threaded_server import MultiThreadedServer    
    from util import Stalker, Dispatcher
    from util import PORT_GENERAL_ENTRY, PORT_GENERAL_LOGGER, CHORD
    from util import CLIENT, ENTRY_POINT, LOGGER,LOGIN_REQUEST, LOGIN_RESPONSE,\
        NEW_LOGGER_RESPONSE, NEW_LOGGER_REQUEST, REGISTER_RESPONSE, REGISTER_REQUEST,\
        CREATE_TWEET_REQUEST, CREATE_TWEET_RESPONSE, PROFILE_REQUEST, PROFILE_RESPONSE,\
        FOLLOW_REQUEST,FOLLOW_RESPONSE, LOGOUT_REQUEST, LOGOUT_RESPONSE, ALIVE_REQUEST,\
        ALIVE_RESPONSE, ADD_LOGGER, REMOVE_LOGGER, ADD_ENTRY, REMOVE_ENTRY, INSERTED_LOGGER_REQUEST,\
        INSERTED_LOGGER_RESPONSE, RETWEET_REQUEST, RETWEET_RESPONSE, FEED_REQUEST, FEED_RESPONSE
except:
    import API.util as util
    from API.threaded_server import MultiThreadedServer    
    from API.util import Stalker, Dispatcher
    from API.util import PORT_GENERAL_ENTRY, PORT_GENERAL_LOGGER, CHORD
    from API.util import CLIENT, ENTRY_POINT, LOGGER,LOGIN_REQUEST, LOGIN_RESPONSE,\
        NEW_LOGGER_RESPONSE, NEW_LOGGER_REQUEST, REGISTER_RESPONSE, REGISTER_REQUEST,\
        CREATE_TWEET_REQUEST, CREATE_TWEET_RESPONSE, PROFILE_REQUEST, PROFILE_RESPONSE,\
        FOLLOW_REQUEST,FOLLOW_RESPONSE, LOGOUT_REQUEST, LOGOUT_RESPONSE, ALIVE_REQUEST,\
        ALIVE_RESPONSE, ADD_LOGGER, REMOVE_LOGGER, ADD_ENTRY, REMOVE_ENTRY, INSERTED_LOGGER_REQUEST,\
        INSERTED_LOGGER_RESPONSE, RETWEET_REQUEST, RETWEET_RESPONSE, FEED_REQUEST, FEED_RESPONSE
    
class EntryPointServerTheaded(MultiThreadedServer):

    def __init__(self, port: int, task_max: int, thread_count: int, timeout: int):
        super().__init__(port, task_max, thread_count, timeout, self.switch)
        self.stalker_loggers = Stalker(ENTRY_POINT,umbral_deads=30, umbral_alive=90)
        self.stalker_entrys = Stalker(ENTRY_POINT, umbral_deads=30, umbral_alive=90)
        self.verbose = True
        self.execute_pending_tasks = False
        self.stalking_entrys = False
        self.stalking_loggers = False
        self.executing = False
        self.pending_tasks = {}
        self.my_ip = socket.gethostbyname(socket.gethostname())
        self.lock = Lock()

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
        print(self.stalker_loggers.alive_dirs)
        with self.lock:
            dirs = self.stalker_loggers.alive_dirs.copy()
        print(dirs)
        rand.shuffle(dirs)
        l = dirs[:5]
        return l
    
    def add_task(self, new_task):
        for ip, tasks in self.pending_tasks.items():
            repeat_task = False
            for i, task in enumerate(tasks):
                if task == new_task:
                    repeat_task = True
                    break
            if repeat_task:
                continue
            tasks.append(new_task)
    
    def send_pending_tasks(self, event: Event):
        self.execute_pending_tasks = True
        event.wait(rand.randint(3,30))
        while not event.is_set():
            print('Tareas Pendientes:')
            print(self.pending_tasks)
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
                        event.wait(rand.randint(1,5))
                    except:
                        self.print(f'TAREA PENDIENTE "{task[0]}:{task[1]}" NO enviada a {ip}:{PORT_GENERAL_ENTRY}')
            event.wait(rand.randint(3,30))
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

        print('Nuevo Mensaje')
        print(type_msg, protocol)
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
            elif protocol == RETWEET_REQUEST:
                self.retweet_request_from_client(id, task, event, storage, data)
            elif protocol == FEED_REQUEST:
                self.feed_request_from_client(id, task, event, storage, data)
            else:
                print('Q pifia metes?')
        elif type_msg == ENTRY_POINT:
            if protocol == ALIVE_REQUEST:                
                self.alive_request_from_entry_point(id, task, event, storage, data)
            elif protocol == ADD_LOGGER:
                self.add_logger_from_entry_point(id, task, event, storage, data)
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
            elif protocol == RETWEET_RESPONSE:
                self.feed_response_from_logger(id, task, event, storage, data)
            elif protocol == FEED_RESPONSE:
                self.feed_response_from_logger(id, task, event, storage, data)            
            else:
                print('Q pifia metes?')
        elif type_msg == CHORD:
            if protocol == NEW_LOGGER_REQUEST:
                self.new_logger_request_from_logger(id, task, event, storage, data)
            elif protocol == INSERTED_LOGGER_REQUEST:
                self.inserted_logger_request_from_logger(id, task, event, storage, data)
            else:
                print('Q pifia metes?')
        else:
            print('Q pifia metes?')

    def try_send_logger(self, message):

        error = None        
        for ip in self.dispatcher_loggers():
            print(ip)
            try:
                send_data = util.encode(message)
                s = socket.socket(AF_INET, SOCK_STREAM)                
                s.connect((ip, PORT_GENERAL_LOGGER))
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
        print('antes del send')
        good, error = self.try_send_logger(message)
        print('despues del send')
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
            storage.delete_state(state.id)
            self.print('LOGIN RESPONSE TO CLIENT ', task[1][0])
        except Exception as e:
            self.print(f'LOGIN RESPONSE to CLIENT {task[1][0]} (((ERRORR)))')
            #self.print(e)
        finally:
            task[0].close()

    def login_response_from_logger(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):

        self.print('LOGIN RESPONSE FROM LOGGER')
        with self.lock:
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
            self.print('LOGOUT_RESPONSE TO CLIENT ', task[1][0])
        except Exception as e:
            self.print(f'LOGOUT_RESPONSE to CLIENT {task[1][0]} (((ERRORR)))')
            self.print(e)
        finally:
            task[0].close()
        storage.delete_state(state.id)

    def logout_response_from_logger(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):

        with self.lock:
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
            self.print('REGISTER_RESPONSE TO CLIENT ', task[1][0])
        except Exception as e:
            self.print(f'REGISTER_RESPONSE to CLIENT {task[1][0]} (((ERRORR)))')
            self.print(e)
        finally:
            task[0].close()
        storage.delete_state(state.id)

    def register_response_from_logger(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):

        with self.lock:
            self.stalker_loggers.update_IP(task[1][0])
        state = storage.get_state(data['id_request'])
        task[0].close()
        state.desired_data = data
        state.hold_event.set()
       

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
            self.print('CREATE_TWEET_RESPONSE TO CLIENT ', task[1][0])
        except Exception as e:
            self.print(f'CREATE_TWEET_RESPONSE to CLIENT {task[1][0]} (((ERRORR)))')
            self.print(e)
        finally:
            task[0].close()
        storage.delete_state(state.id)

    def create_tweet_response_from_logger(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):

        with self.lock:
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
            self.print('PROFILE_RESPONSE TO CLIENT ', task[1][0])
        except Exception as e:
            self.print(f'PROFILE_RESPONSE to CLIENT {task[1][0]} (((ERRORR)))')
            self.print(e)
        finally:
            task[0].close()
        storage.delete_state(state.id)

    def profile_response_from_logger(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):

        with self.lock:
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
            self.print('FOLLOW_RESPONSE TO CLIENT ', task[1][0])
        except Exception as e:
            self.print(f'FOLLOW_RESPONSE to CLIENT {task[1][0]} (((ERRORR)))')
            self.print(e)
        finally:
            task[0].close()
        storage.delete_state(state.id)


    def follow_response_from_logger(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):

        with self.lock:
            self.stalker_loggers.update_IP(task[1][0])
        state = storage.get_state(data['id_request'])
        task[0].close()
        state.desired_data = data
        state.hold_event.set()

    #-------------------- RETWEET ----------------------#

    def retweet_request_from_client(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):
        
        token = data['token']
        nick = data['nick']
        date = data['date']

        state = storage.insert_state()
        message = {
            'type': ENTRY_POINT,
            'proto': RETWEET_REQUEST,
            'token': token,
            'nick': nick,
            'date': date,
            'id_request': state.id
        }

        good, error = self.try_send_logger(message)
        if not good:
            msg = {
                'type': ENTRY_POINT,
                'proto': RETWEET_RESPONSE,
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
                    'proto': RETWEET_RESPONSE,
                    'succesed': True,                    
                    'error': None
                }
            else:
                msg = {
                    'type': ENTRY_POINT,
                    'proto': RETWEET_RESPONSE,
                    'succesed': False,                    
                    'error': state.desired_data['error'],                    
                }
        else:
            msg = {
                'type': ENTRY_POINT,
                'proto': RETWEET_RESPONSE,
                'succesed': False,                
                'error': 'Tiempo de espera agotado.',                
            }

        try:
            task[0].send(util.encode(msg))
            task[0].close()
            self.print('RETWEET_RESPONSE TO CLIENT: ', task[1][0])
        except Exception as e:
            self.print(f'RETWEET_RESPONSE to CLIENT {task[1][0]} (((ERRORR)))')
            self.print(e)
        storage.delete_state(state.id)


    def retweet_response_from_logger(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):

        with self.lock:
            self.stalker_loggers.update_IP(task[1][0])
        state = storage.get_state(data['id_request'])
        task[0].close()
        state.desired_data = data
        state.hold_event.set()

    #-------------------- FEED ----------------------#

    def feed_request_from_client(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):
        
        token = data['token']
        nick = data['nick']        

        state = storage.insert_state()
        message = {
            'type': ENTRY_POINT,
            'proto': FEED_REQUEST,
            'token': token,
            'nick': nick,            
            'id_request': state.id
        }

        good, error = self.try_send_logger(message)
        if not good:
            msg = {
                'type': ENTRY_POINT,
                'proto': FEED_RESPONSE,
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
                    'proto': FEED_RESPONSE,
                    'succesed': True,  
                    'data': state.desired_data['data'],
                    'error': None
                }
            else:
                msg = {
                    'type': ENTRY_POINT,
                    'proto': FEED_RESPONSE,
                    'succesed': False,                    
                    'error': state.desired_data['error'],                    
                }
        else:
            msg = {
                'type': ENTRY_POINT,
                'proto': FEED_RESPONSE,
                'succesed': False,                
                'error': 'Tiempo de espera agotado.',                
            }

        try:
            task[0].send(util.encode(msg))            
            self.print('RETWEET_RESPONSE TO CLIENT: ', task[1][0])
        except Exception as e:
            self.print(f'RETWEET_RESPONSE to CLIENT {task[1][0]} (((ERRORR)))')
            self.print(e)
        finally:
            task[0].close()
        storage.delete_state(state.id)


    def feed_response_from_logger(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):

        with self.lock:
            self.stalker_loggers.update_IP(task[1][0])
        state = storage.get_state(data['id_request'])
        task[0].close()
        state.desired_data = data
        state.hold_event.set()


    def follow_response_from_logger(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):

        with self.lock:
            self.stalker_loggers.update_IP(task[1][0])
        state = storage.get_state(data['id_request'])
        task[0].close()
        state.desired_data = data
        state.hold_event.set()

    #------------------ ALIVE ------------------#

    def alive_request_to_entry_point(self, event:Event):

        msg_bytes = util.encode(self.stalker_entrys.msg_stalk())
        self.stalking_entrys = True
        event.wait(rand.randint(20,60))
        while not event.is_set():
            dirs_to_stalk = self.stalker_entrys.refresh_dirs()
            print('STALKEANDO Entrys: ', dirs_to_stalk)
            for dir in dirs_to_stalk:
                try:
                    s = socket.socket(AF_INET, SOCK_STREAM)
                    s.connect((dir, PORT_GENERAL_ENTRY))
                    s.send(msg_bytes)
                    data = util.decode(s.recv(1024))                    
                    #TODO Verificar respuesta                    
                    self.stalker_entrys.update_IP(dir)
                except:
                    self.print('ALIVE ENTRY Conexion perdida con: ', dir)
                finally:
                    s.close()
            event.wait(rand.randint(20,60))
        self.stalking_entrys = False
        print('END Stalking Entrys')

    def alive_request_to_logger(self, event: Event):

        msg_bytes = util.encode(self.stalker_loggers.msg_stalk())
        self.stalking_loggers = True
        event.wait(rand.randint(20,60))
        while not event.is_set():
            with self.lock:
                dirs_to_stalk = self.stalker_loggers.refresh_dirs()
            print('STALKEANDO Loggers: ', dirs_to_stalk)
            for dir in dirs_to_stalk:
                try:
                    s = socket.socket(AF_INET, SOCK_STREAM)
                    s.connect((dir, PORT_GENERAL_LOGGER))
                    s.send(msg_bytes)
                    data = util.decode(s.recv(1024))
                    #TODO Verificar respuesta
                    with self.lock:
                        self.stalker_loggers.update_IP(dir)
                except:
                    self.print('ALIVE LOGGER Conexion perdida con: ', dir)
                finally:
                    s.close()
            event.wait(rand.randint(20,60))
        self.stalking_loggers = False
        print('END Stalking Loggers')


    def alive_request_from_entry_point(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):
        #TODO agregar condicional para cuando no este
        self.stalker_entrys.update_IP(task[1][0])
        task[0].send(util.encode({
            'type': ENTRY_POINT,
            'proto': ALIVE_RESPONSE
        }))
        task[0].close()

    #------------------ NEW LOGGER ------------------#

    def new_logger_request_from_logger(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):
                
        self.lock.acquire()
        if len(self.stalker_loggers.list) > 0:
            if self.stalker_loggers.extract_IP(task[1][0]) is not None:
                self.stalker_loggers.update_IP(task[1][0])
                alive_loggers = [ip for ip in self.stalker_loggers.alive_dirs.copy()]
            else:
                alive_loggers = [ip for ip in self.stalker_loggers.alive_dirs.copy()]
            if len(alive_loggers) == 0:
                alive_loggers.append(self.stalker_loggers.list[-1])
            self.lock.release()

            rand.shuffle(alive_loggers)
            ip_loggers = alive_loggers[:5]

            msg = {
                'type': ENTRY_POINT,
                'proto': NEW_LOGGER_RESPONSE,
                'ip_loggers': ip_loggers
            }
        else:            
            self.lock.release()
            msg = {
                'type': ENTRY_POINT,
                'proto': NEW_LOGGER_RESPONSE,
                'ip_loggers': []
            }        
        task[0].send(util.encode(msg))
        task[0].close()        


    def inserted_logger_request_from_logger(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):        
        with self.lock:
            self.stalker_loggers.update_IP(task[1][0])
            self.stalker_loggers.refresh_dirs()
        msg = {
            'type': ENTRY_POINT,
            'proto': INSERTED_LOGGER_RESPONSE,            
        }
        self.add_task((ADD_LOGGER, task[1][0]))
        task[0].send(util.encode(msg))
        task[0].close()

    def add_logger_from_entry_point(self, id:int,task: tuple[socket.socket,object],event:Event, storage, data: dict):

        with self.lock:
            self.stalker_loggers.update_IP(data['ip'])
            self.stalker_loggers.refresh_dirs()
 