from queue import Queue, Empty
from threading import Thread, Event, Lock
import concurrent.futures
from time import sleep
from socket import socket, AF_INET, SOCK_STREAM

def integer_numbers():
    i = 0
    while True:
        yield i
        i += 1


class NumberGiver:
    def __init__(self):
        self.free_ids = []
        self.iter = integer_numbers()
        self.lock = Lock()
    
    def get_id(self):
        new_id = None
        self.lock.acquire()
        if(len(self.free_ids) > 0):
            new_id = self.free_ids.pop(0)
        else:
            new_id = next(self.iter)
        self.lock.release()
        return new_id

    def put_id(self,old_id):
        self.lock.acquire()
        self.free_ids.append(old_id)
        self.lock.release()

class ThreadHolder:
    def __init__(self,id: int,hold_event: Event = None):
        self.id = id
        self.hold_event = None
        if not hold_event:
            self.hold_event = Event()
        else:
            self.hold_event = hold_event
        self.desired_data = None

class StateStorage:
    def __init__(self):
        self.storage: dict[int,ThreadHolder] = {}
        self.lock: Lock = Lock()
        self.id_gen = NumberGiver()
    
    def insert_state(self):
        id = self.id_gen.get_id()
        state = ThreadHolder(id)
        self.lock.acquire()
        self.storage[state.id] = state
        self.lock.release()
        return state
    
    def delete_state(self,id):
        self.lock.acquire()
        item = self.storage.pop(id,None)
        if item:
            self.id_gen.put_id(id)
        self.lock.release()
    
    def get_state(self,id):
        self.lock.acquire()
        value = self.storage.get(id,None)
        self.lock.release()
        return value

def end_event_client(end_event: Event,port):
    end_event.wait()
    s = socket(AF_INET,SOCK_STREAM)
    # ip = gethostbyname('eager_galois')
    ip = '127.0.0.1'
    s.connect((ip,port))
    request = ""
    s.sendall(request.encode())
    

def server_printer(id:int,task: tuple[socket,object],event:Event):
    (socket_client, addr_client) = task
    data = socket_client.recv(1000).decode()
    if(data == 'end'):
        event.set()
        socket_client.close()
    print(f'from{addr_client}: {data}')
    socket_client.sendall('OK'.encode())
    socket_client.close()

def test_printer(id,content,event:Event):
    if(content == 'end'):
        print(f'worker_{id}->ENDING SERVER')
        event.set()
    else:
        print(f'worker_{id}' + content)

class MultiThreadedServer:
    def __init__(self,port: int, task_max: int, thread_count: int, timeout: int, parse_func):
    
        self.task_max = task_max
        self.thread_count = thread_count
        self.current_thread_count = 0
        self.timeout = timeout
        self.parse_func = parse_func
        self.end_event = Event()
        self.task_list = Queue(task_max)
        self.storage = StateStorage()
        self.port = port

    def consumer_func(self, id : int,task_list: Queue ,event :Event, parse_func,self_timeout,storage):
        while not event.is_set() or not task_list.empty():
            try:
                task = task_list.get(timeout=self_timeout)
                print(f'START worker_{id}')
                parse_func(id,task,event,storage)
            except Empty:
                continue
        print(f'END worker_{id}')
        self.current_thread_count -= 1
    
    def start_test(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers = self.thread_count) as executor:
            for id in range(self.thread_count):
                executor.submit(self.consumer_func,id,self.task_list,self.end_event,self.parse_func,self.timeout,self.storage)
            while(True):
                task = input()
                if(self.end_event.is_set()):
                    break
                self.task_list.put(task)
        print('ENDED listening thread')


    def start_server(self):
        print('start server')
        self.end_event.clear()
        with concurrent.futures.ThreadPoolExecutor(max_workers = self.thread_count) as executor:
            executor.submit(end_event_client,self.end_event,self.port)
            for id in range(self.thread_count):
                executor.submit(self.consumer_func,id,self.task_list,self.end_event,self.parse_func,self.timeout, self.storage)
                self.current_thread_count += 1
                print(self.current_thread_count)
            s = socket(family = AF_INET, type = SOCK_STREAM)            
            s.bind(("0.0.0.0", self.port))
            s.listen(5)
            print('Listen')
            while True:
                (socket_client, addr_client) = s.accept()
                print('Accept')
                print(addr_client)
                if(self.end_event.is_set()):
                    print('Aqui no debe entrar')
                    socket_client.close()
                    break
                print('Aqui si debe entrar')
                self.task_list.put((socket_client, addr_client))
            s.close()
            print('ENDED listening thread')        
    
