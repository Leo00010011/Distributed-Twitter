from random import randint,choice
from queue import Queue, Empty
from threading import Thread, Event, Lock
import concurrent.futures
from time import sleep
from socket import socket, AF_INET, SOCK_STREAM,gethostbyname,gethostname
from threaded_server import MultiThreadedServer
from hashlib import shake_256
from math import floor, log2
import os
import datetime
import sys


# Comunication
#  * Rec(Soy tu nuevo predecesor)
#  * Env(Soy tu nuevo predecesor)
#  * Rec(Soy tu nuevo sucesor)
#  * Env(Soy tu nuevo sucesor)
#  * Rec(<<DAME>> el sucesor de k, mode)
#  * Rec(<<DALE a IP>> el sucesor de k, mode)
#  * Env(<<DALE a IP>> el sucesor de k, mode)
#  * Env(Get some ChordNode)
#  * Rec(Get some ChordNode)
def get_my_ip():
    hostname = gethostname()
    ip = gethostbyname(hostname)
    return ip


def clear():
    os.system("clear")


def integer_numbers():
    i = 0
    while True:
        yield i
        i += 1


class NumberGiver:
    def __init__(self) -> None:
        self.free_ids = []
        self.iter = integer_numbers()
        self.lock = Lock()
    
    def get_id(self):
        new_id = None
        with self.lock:
            if(len(self.free_ids) > 0):
                new_id = self.free_ids.pop(0)
            else:
                new_id = next(self.iter)
        return new_id

    def put_id(self,old_id):
        with self.lock:
            self.free_ids.append(old_id)

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
        with self.lock:
            self.storage[state.id] = state
        return state
    
    def delete_state(self,id):
        with self.lock:
            item = self.storage.pop(id,None)
            if item:
                self.id_gen.put_id(id)
    
    def get_state(self,id) -> ThreadHolder:
        with self.lock:
            value = self.storage.get(id,None)
        return value


# generate 32 bit key
#  secrets.token_bytes([nbytes=None])

# generate hash of a name
# hashlib.sha256('leonardo'.encode()).digest()

class ParsedMsg:
    def __init__(self,cmd,id_k,owner_ip,as_max,req_id):
        self.cmd = cmd
        self.req_id = int(req_id)
        self.owner_ip = owner_ip
        self.id_k = int(id_k)
        self.as_max = as_max == 'True'

class ChordNode:
    def __init__(self,id,ip,as_max):
       self.id = id     
       self.ip = ip     
       self.as_max = as_max     

class ChordServer:
    def __init__(self,DHT_name,port,entry_points,id,disable_log,is_the_first = False,max_id = 1000000):
        self.DHT_name = DHT_name
        self.disable_realtime_log = disable_log
        self.log_lock = Lock()
        self.Ft: list[ChordNode] = [None]*floor(log2(max_id))
        self.state_storage = StateStorage()
        self.port = port
        self.is_the_first = is_the_first
        self.entry_points = entry_points
        self.server : MultiThreadedServer = MultiThreadedServer(self.port,100,100,2,self.create_dispatcher())
        self.get_succ_req_cmd = 'get_succ_req'
        self.get_succ_resp_cmd = 'get_succ_resp'
        self.ImYSucc_cmd = 'ImYSucc_cmd'
        self.ImYPrev_cmd = 'ImYPrev'
        self.outside_cmd = 'outside'
        self.confirm_cmd = 'confirm_new_succ'
        self.busy = False
        self.busy_lock = Lock()
        self.Ft_lock = Lock()
        #TODO gen ID
        self.max_id = max_id
        # self.id = randint(1,max_id)
        self.id = id
        self.ip = get_my_ip()
        self.log: list[str] = []
        self.response ={
            self.confirm_cmd:self.rec_confirm_new_prev,
            self.ImYSucc_cmd:self.rec_ImYSucc,
            self.ImYPrev_cmd:self.rec_ImYPrev,
            self.get_succ_req_cmd:self.rec_get_succ_req,
            self.get_succ_resp_cmd:self.rec_get_succ_resp,
            self.outside_cmd: self.rec_outside_get
        }

    def insert_as_first(self):
        self.Ft[0] = ChordNode(self.id + self.max_id,self.ip,as_max=True)
        self.Ft[1] = ChordNode(self.id + self.max_id,self.ip,as_max=True)
        for i in range(2,len(self.Ft)):
            self.Ft[i] = self.Ft[1]

    def insert(self):
        for _ in range(10):
            ip = self.get_some_node()
            succ_node = self.ask_succ(ip,self.id,False)
            response, prev_node = self.ImYPrev(succ_node.ip)
            if response == 'Busy':
                sleep(randint(1,5))
                continue
            else:
                break
        self.ImYSucc(prev_node.ip)
        #TODO si prev_ip esta caido
        self.confirm_new_prev(succ_node.ip)
        self.Ft[0] = prev_node
        for i in range(1,len(self.Ft)):
            self.Ft[i] = succ_node

    def start(self):
        server_thread = Thread(target= self.server.start_server)
        server_thread.start()
        if self.is_the_first:
            self.insert_as_first()
        else:
            self.insert()
        Thread(target=ChordServer.MaintainFt, args=[self], daemon=True).start()
        self.register_in_entry()
        self.update_log(f'inserted')
        Thread(target= ChordServer.sleeping_log, args=[self],daemon = True).start()
        server_thread.join()


    def create_dispatcher(self):
        def dispatcher(id:int,task: tuple[socket,object],event:Event):
            (socket_client, addr_client) = task
            msg = socket_client.recv(15000).decode()
            if(msg == 'end'):
                event.set()
                socket_client.close()
            parsed_msg = ChordServer.parse_msg(msg)
            self.update_log(f'recived: cmd:{parsed_msg.cmd} req_id:{parsed_msg.req_id} id:{parsed_msg.id_k} owner:{parsed_msg.owner_ip} as_max:{str(parsed_msg.as_max)}')
            self.response[parsed_msg.cmd](parsed_msg,socket_client,addr_client)
        return dispatcher

    def get_some_node(self):
        entry = choice(self.entry_points)
        self.update_log('starting to send for (get_some_node)')
        response = self.send_and_close(entry,'get')
        return response.split(',')[0]

    def sleeping_log(self):
        while(True):
            self.print_log()
            sleep(2)

    def update_log(self,log_entry = None):
        with self.log_lock:
            if log_entry:
                self.log.append((log_entry,str(datetime.datetime.now().time())))

    def print_log(self):
        with self.log_lock:
            clear()
            print('---------------------')
            print(f'log of node_{self.id} at {str(datetime.datetime.now().time())}')
            if(not(self.disable_realtime_log == 'yes')):
                if(self.disable_realtime_log == 'file'):
                    with open(f'node_{self.id}_log','a') as f:
                        f.write('\n'.join([f'{time_str}- {entry}' for entry, time_str in self.log]))
                    self.log = [] 
                else:
                    print('LOG:')
                    for entry, time_str in self.log:
                        print(f'{time_str}- {entry}')
            print('FingerTable:')
            with self.Ft_lock:
                for index, node in enumerate(self.Ft):
                    if not node:
                        print('Not initialiced')
                    else:
                        print(f'{index})   ip:{node.ip}   id:{node.id}   as_max: {node.as_max}')





    def succ_who(self,k,as_max) -> ChordNode:
        if as_max:
            k = k - self.max_id
        res_id = self.id
        if (as_max):
            res_id += self.max_id
        if self.Ft[0].id < k <= self.id:
            return ChordNode(res_id,self.ip,as_max)
        
        #Eres menor que el minimo o eres menor que un nodo siendo as_max

        if((as_max or self.Ft[0].id > self.id) and k < self.id):
            return ChordNode(res_id,self.ip,as_max)
        
        if self.id < k <= self.Ft[1].id:
            return self.Ft[1]
        less_than_me = False
        if k < self.id:
            less_than_me = True
            k += self.max_id
        
        for i in range(2,len(self.Ft) - 1):
            if self.Ft[i].id <= k < self.Ft[i + 1].id:
                if less_than_me and self.Ft[i].as_max:
                    return ChordNode(self.Ft[i].id - self.max_id,self.Ft[i].ip,False)
                else:
                    return self.Ft[i]
            
        return self.Ft[-1]

    def succ(self,k,owner_ip,as_max,req_id):
        who = self.succ_who(k,as_max)
        self.update_log(f'who id:{who.id} ip:{who.ip} as_max:{who.as_max}')
        if who.ip == self.ip:
            if(owner_ip == self.ip):
                if as_max:
                    self.update_log('my self as_max')
                    holder = self.state_storage.get_state(req_id)
                    holder.desired_data = who
                    holder.hold_event.set()
                    return
                else:
                    return 'Me'
            self.update_log(f'accepting {k}')
            self.accept_succ(owner_ip,req_id,who.id,who.as_max)
        else:
            self.update_log(f'redirecting request to {who.id}:{who.ip}')
            msg = ChordServer.create_msg(self.get_succ_req_cmd,k,owner_ip,who.as_max,req_id)
            self.send_and_close(who.ip,msg)

    def MaintainFt(self):
        while(True):
            sleep(5)   
            for i in range(1,len(self.Ft)):
                current = self.id + 2**(i - 1)
                who = self.succ_who(current,False)
                if(who.ip != self.ip):
                    who = self.ask_succ(who.ip,current,who.as_max)
                with self.Ft_lock:
                    self.Ft[i] = who
            self.update_log()
                    
            
    def confirm_new_prev(self,succ_ip):
        msg = ChordServer.create_msg(self.confirm_cmd,self.id,self.ip,False,0)
        self.update_log('starting to send (confirm)')
        self.send_and_close(succ_ip,msg)

    def rec_confirm_new_prev(self,msg:ParsedMsg,socket_client,addr):
        self.update_log('inside rec_confirm')
        with self.Ft_lock:
            res_id = msg.id_k
            res_as_max = msg.as_max
            if msg.id_k > self.id:
                res_id += self.max_id
                res_as_max = True
            self.Ft[0] = ChordNode(res_id,msg.owner_ip,res_as_max)
        with self.busy_lock:
            self.busy = False
        socket_client.send('Ok'.encode())
        socket_client.close()
        self.update_log('confirmed new prev')
        
    
    def rec_outside_get(self,msg:ParsedMsg,socket_client,addr):
        self.update_log(f'start rec outside_get {msg.id_k}')
        # {type:'logger', proto:'chord'}]   
        holder : ThreadHolder= self.state_storage.insert_state()
        me = self.succ(msg.id_k,self.ip,False,holder.id)
        self.update_log(f'me:{str(me)}')
        if not me:
            self.update_log('starting to wait')
            holder.hold_event.wait()
        else:
            holder.desired_data = ChordNode(self.id,self.ip,False)
        self.state_storage.delete_state(holder.id)
        self.update_log('responding to outside')
        socket_client.send(holder.desired_data.ip.encode())
        socket_client.close()
        self.update_log(f'end outside req')

    def rec_get_succ_req(self,msg:ParsedMsg,socket_client,addr):
        socket_client.send('Ok'.encode())
        self.update_log(f'start rec get_succ_req {msg.id_k}')
        self.succ(msg.id_k,msg.owner_ip,msg.as_max,msg.req_id)
        socket_client.close()
        self.update_log('end rec get_succ_req')

    def rec_get_succ_resp(self,msg:ParsedMsg,socket_client,addr):
        self.update_log('start rec get_succ_resp')
        holder = self.state_storage.get_state(msg.req_id)
        holder.desired_data = ChordNode(msg.id_k,addr[0],msg.as_max)
        holder.hold_event.set()
        self.state_storage.delete_state(msg.req_id)
        socket_client.send('Ok'.encode())
        socket_client.close()
        self.update_log('end rec get_succ_resp')

    def ImYSucc(self,prev_ip):
        msg = ChordServer.create_msg(self.ImYSucc_cmd,self.id,self.ip,False,0)
        self.update_log('starting to send (ImYSucc)')
        self.send_and_close(prev_ip,msg)
        

    def rec_ImYSucc(self,msg:ParsedMsg,socket_client,addr):
        self.update_log('start rec ImYSucc')
        res_id = msg.id_k
        if msg.id_k < self.id:
            res_id += self.max_id
        with self.Ft_lock:
            self.Ft[1] = ChordNode(res_id,msg.owner_ip,msg.id_k < self.id)
        socket_client.send('Ok'.encode())
        socket_client.close()
        self.update_log('end rec ImYSucc')

    def ImYPrev(self,succ_ip):
        msg = ChordServer.create_msg(self.ImYPrev_cmd,self.id,self.ip,False,0)
        self.update_log('starting to send (ImYPrev)')
        msg = self.send_and_close(succ_ip,msg)
        arr = msg.split(',')
        return arr[0], ChordNode(int(arr[1]),arr[2],arr[3] == 'True')

    def rec_ImYPrev(self,msg:ParsedMsg,socket_client,addr):
        self.update_log('start rec ImYPrev')
        busy = None
        with self.busy_lock:
            busy = self.busy
            if not self.busy:
                self.busy = True
        if busy:
            socket_client.send('busy,0,none,none'.encode()) 
        else:
            result = None
            with self.Ft_lock:
                result = self.Ft[0]
            res_as_max = result.as_max
            res_id = result.id
            if msg.id_k > self.id:
                res_as_max = False
                res_id -= self.max_id
            # (Busy|Ok),id,ip
            socket_client.send(f'Ok,{res_id},{result.ip},{res_as_max}'.encode()) 
        socket_client.close()
        self.update_log('end rec ImYPrev')

    def register_in_entry(self):
        entry_point = choice(self.entry_points)
        self.update_log('starting to send (register)')
        self.send_and_close(entry_point,f'anotate,{self.id}')



    def accept_succ(self,owner_ip,req_id,id,as_max):
        msg = ChordServer.create_msg(self.get_succ_resp_cmd,id,self.ip,as_max,req_id)
        self.update_log('starting to send (accept)')
        self.send_and_close(owner_ip,msg)

    def ask_succ(self, node_ip:str, k:int, as_max:bool) -> ChordNode:
        holder = self.state_storage.insert_state()
        for _ in range(10):
            msg = ChordServer.create_msg(self.get_succ_req_cmd,k,self.ip,as_max,holder.id)
            self.update_log(f'starting to send (ask_succ to {node_ip} for {k} as_max:{str(as_max)})')
            self.send_and_close(node_ip,msg)
            self.update_log(f'waiting for response in ask_succ')
            holder.hold_event.wait(5)
            if holder.desired_data:
                self.state_storage.delete_state(holder.id)
                break
        if not holder.desired_data:
            raise Exception('No se pudo insertar porque nadie respondio al succ')
        self.state_storage.delete_state(holder.id)
        return holder.desired_data
    
    def parse_msg(raw_msg:str) -> ParsedMsg:
        arr = raw_msg.split(',')
        return ParsedMsg(arr[0], arr[1], arr[2], arr[3],arr[4])
        
    def create_msg(cmd:str,k:int, owner_ip:str, as_max:bool, req_id:int):
        return ','.join([str(cmd),str(k),str(owner_ip),str(as_max),str(req_id),])

    def send_and_close(self,ip,msg):
        s = socket(AF_INET,SOCK_STREAM)
        try:
            s.connect((ip,self.port))
            s.sendall(msg.encode())
            response = s.recv(15000).decode()
            s.close()
        except Exception as e:
            self.update_log(str(e))
            raise e
        self.update_log('send ended')
        return response

# print('is_first?')
# first = input() == 'yes'
# print('disable log?')
# log = input()
# print('id:')
# id_n = int(input())
# server = ChordServer(DHT_name='Log',port = 15000,entry_points=['entry'],is_the_first= first,id = id_n, disable_log=log)
# server.start()
    



    
    



