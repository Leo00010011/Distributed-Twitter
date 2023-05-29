from queue import Queue, Empty
from threading import Thread, Event
import concurrent.futures
from time import sleep
from socket import socket, AF_INET, SOCK_STREAM


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
    def __init__(self,port: int, task_max: int, thread_count: int, timout: int, parse_func) -> None:
        self.port = port
        self.task_max = task_max
        self.thread_count = thread_count
        self.timout = timout
        self.parse_func = parse_func
        self.end_event = Event()
        self.task_list = Queue(task_max)

    def consumer_func(id : int,task_list: Queue ,event :Event, parse_func,self_timeout):
        while not event.is_set() or not task_list.empty():
            try:
                task = task_list.get(timeout=self_timeout)
                print(f'START worker_{id}')
                parse_func(id,task,event)
            except Empty:
                continue
        print(f'END worker_{id}')
    
    def start_test(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers = self.thread_count) as executor:
            for id in range(self.thread_count):
                executor.submit(MultiThreadedServer.consumer_func,id,self.task_list,self.end_event,self.parse_func,self.timout)
            while(True):
                task = input()
                if(self.end_event.is_set()):
                    break
                self.task_list.put(task)
            print('ENDED listening thread')


    def start_server(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers = self.thread_count) as executor:
            executor.submit(end_event_client,self.end_event,self.port)
            for id in range(self.thread_count):
                executor.submit(MultiThreadedServer.consumer_func,id,self.task_list,self.end_event,self.parse_func,self.timout)
            s = socket(family = AF_INET, type = SOCK_STREAM)
            s.bind(("0.0.0.0", self.port))
            s.listen(5)
            while True:
                (socket_client, addr_client) = s.accept()
                if(self.end_event.is_set()):
                    socket_client.close()
                    break
                self.task_list.put((socket_client, addr_client))
            s.close()
            print('ENDED listening thread')
    
server = MultiThreadedServer(15000,10,10,5,server_printer)
server.start_server()

