from random import randint ,choice , shuffle
from queue import Queue , Empty
from threading import Thread , Event , Lock
import concurrent.futures
from time import sleep
from socket import socket , AF_INET , SOCK_STREAM ,gethostbyname ,gethostname
from hashlib import shake_256
from math import floor , log2
import hashlib
import os
import datetime
import sys
import json

try:
    from threaded_server import MultiThreadedServer
    import util    
except:
    import API.util as util
    from API.threaded_server import MultiThreadedServer



# cuando termina de insertar
# type: Chord(Utils)
# proto: NEW_LOGGER_RESPONSE(Utils)
# sucesors: [los ips de los sucesores]
# siblings: [lista de replicas]
# chord_id: mi sha

# outside_resp
# type: LOGGER
# proto: CHORD_RESPONSE
# IP: [Sucesores de la replica]

# outside_req
# type: LOGGER
# proto: CHORD_REQUEST
# hash: (el nick para hashear) 
# id_req: (int)

# Comunication
#  * Rec(Soy tu nuevo predecesor)
#  * Env(Soy tu nuevo predecesor)
#  * Rec(Soy tu nuevo sucesor)
#  * Env(Soy tu nuevo sucesor)
#  * Rec(<<DAME>> el sucesor de k , mode)
#  * Rec(<<DALE a IP>> el sucesor de k , mode)
#  * Env(<<DALE a IP>> el sucesor de k , mode)
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

    def put_id(self ,old_id):
        with self.lock:
            self.free_ids.append(old_id)

class ThreadHolder:
    def __init__(self ,id: int ,hold_event: Event = None):
        self.id = id
        self.hold_event = None
        if not hold_event:
            self.hold_event = Event()
        else:
            self.hold_event = hold_event
        self.desired_data = None

class StateStorage:
    def __init__(self):
        self.storage: dict[int ,ThreadHolder] = {}
        self.lock: Lock = Lock()
        self.id_gen = NumberGiver()
    
    def insert_state(self):
        id = self.id_gen.get_id()
        state = ThreadHolder(id)
        with self.lock:
            self.storage[state.id] = state
        return state
    
    def delete_state(self ,id):
        with self.lock:
            item = self.storage.pop(id ,None)
            if item:
                self.id_gen.put_id(id)
    
    def get_state(self ,id) -> ThreadHolder:
        with self.lock:
            value = self.storage.get(id ,None)
        return value


# generate 32 bit key
#  secrets.token_bytes([nbytes=None])

# generate hash of a name
# hashlib.sha256('leonardo'.encode()).digest()

class ParsedMsg:
    def __init__(self ,cmd ,id_hex ,owner_ip ,as_max ,req_id):
        self.cmd = cmd
        self.req_id = int(req_id)
        self.owner_ip = owner_ip
        self.id_hex = id_hex
        self.id = int(id_hex ,16)
        self.as_max = as_max == 'True'

class ChordNode:
    def __init__(self ,id ,id_hex ,ip ,as_max):
       self.id = id     
       self.id_hex = id_hex     
       self.ip = ip     
       self.as_max = as_max     

class ChordServer:
    def __init__(self,id,DHT_name ,port ,disable_log):
        self.DHT_name = DHT_name
        self.disable_realtime_log = disable_log
        self.log_lock = Lock()
        self.request_count = {}
        self.max_id = int(''.join(['f' for _ in range(64)]) ,16)
        self.max_id = 1000000
        self.Ft: list[ChordNode] = [None]*floor(log2(self.max_id + 1))
        self.state_storage = StateStorage()
        self.port = port

        self.entry_points = []
        with open('entrys.txt' , 'r') as ft:
            for ip in ft.read().split(sep='\n'):
                self.entry_points.append(str(ip))
        self.server : MultiThreadedServer = MultiThreadedServer(self.port ,100 ,100 ,2 ,self.create_dispatcher() , log = False)
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
        self.ip = get_my_ip()
        self.id = id
        self.id_hex = hex(self.id)[2:]
        # self.id_hex = hashlib.sha256(self.ip.encode()).hexdigest()
        # self.id = int(self.id_hex ,16)
        self.log: list[str] = []
        self.response ={
            self.confirm_cmd:self.rec_confirm_new_prev ,
            self.ImYSucc_cmd:self.rec_ImYSucc ,
            self.ImYPrev_cmd:self.rec_ImYPrev ,
            self.get_succ_req_cmd:self.rec_get_succ_req ,
            self.get_succ_resp_cmd:self.rec_get_succ_resp ,
            self.outside_cmd: self.rec_outside_get
        }

    def insert_as_first(self):
        num = self.id + self.max_id
        num_hex = hex(num)[2:]
        self.Ft[0] = ChordNode(num ,num_hex ,self.ip ,as_max=True)
        self.Ft[1] = ChordNode(num ,num_hex ,self.ip ,as_max=True)
        for i in range(2 ,len(self.Ft)):
            self.Ft[i] = self.Ft[1]

    def insert(self ,ips):
        success = None
        while not success:
            for _ in range(10):
                succ_node = self.ask_succ(ips ,self.id_hex ,False)
                response , prev_node = self.ImYPrev(succ_node.ip)
                if response == 'Busy':
                    self.update_log(f'{succ_node.ip} is busy')
                    sleep(randint(1 ,5))
                    continue
                else:
                    success = True
                    break
            if success:
                break
        self.ImYSucc(prev_node.ip)
        self.confirm_new_prev(succ_node.ip)
        self.Ft[0] = prev_node
        for i in range(1 ,len(self.Ft)):
            self.Ft[i] = succ_node

    def start(self):
        Thread(target= ChordServer.sleeping_log , args=[self] ,daemon = True).start()
        server_thread = Thread(target= self.server.start_server)
        server_thread.start()
        ips = self.get_some_node()
        if len(ips) == 0:
            self.update_log('is first')
            self.insert_as_first()
        else:
            self.insert(ips)
        Thread(target=ChordServer.MaintainFt , args=[self] , daemon=True).start()
        msg = self.build_insert_response()
        # print('builded msg')
        # self.send_and_close(['127.0.0.1'],msg,util.PORT_GENERAL_LOGGER)
        self.register_in_entry()
        self.update_log(f'inserted')
        server_thread.join()


    def create_dispatcher(self):
        def dispatcher(id:int ,task: tuple[socket ,object] ,event:Event ,storage):
            (socket_client , addr_client) = task
            try:                
                msg = socket_client.recv(15000)
                parsed_msg = self.parse_msg(msg)
            except Exception as e:
                self.update_log(f'Bad Request: {msg}')
                self.update_log(str(e))
                return
            self.update_log(f'recived: cmd:{parsed_msg.cmd} req_id:{parsed_msg.req_id} id:{parsed_msg.id_hex} owner:{parsed_msg.owner_ip} as_max:{str(parsed_msg.as_max)}')
            self.response[parsed_msg.cmd](parsed_msg ,socket_client ,addr_client)
        return dispatcher

    def get_some_node(self):
        self.update_log('starting to send for (get_some_node)')
        msg_dict = {
            'type': util.CHORD ,
            'proto': util.NEW_LOGGER_REQUEST
        }
        text = json.dumps(msg_dict)
        response = self.send_til_success(self.entry_points ,text ,'register' ,util.PORT_GENERAL_ENTRY)
        resp_dict = util.decode(response)
        return resp_dict['ip_loggers']

    def sleeping_log(self):
        while(True):
            self.print_log()
            sleep(2)

    def update_log(self ,log_entry = None):
        with self.log_lock:
            if log_entry:
                self.log.append((log_entry ,str(datetime.datetime.now().time())))

    def print_log(self):
        with self.log_lock:
            clear()
            print('---------------------')
            print(f'log of node_{self.id_hex} at {str(datetime.datetime.now().time())}')
            if(not(self.disable_realtime_log == 'yes')):
                if(self.disable_realtime_log == 'file'):
                    with open(f'node_{self.id_hex}.log','a') as f:
                        f.write('\n'.join([f'{time_str}- {entry}' for entry , time_str in self.log]))
                    self.log = [] 
                else:
                    print('LOG:')
                    for entry , time_str in self.log:
                        print(f'{time_str}- {entry}')

            print('request count')
            for key in self.request_count.keys():
                print(f'{key}: {self.request_count[key]}')
            print('FingerTable:')
            with self.Ft_lock:
                for index , node in enumerate(self.Ft):
                    if not node:
                        print('Not initialiced')
                    else:
                        print(f'{index})   ip:{node.ip}   id:{node.id}   as_max: {node.as_max}')





    def succ_who(self ,k ,as_max) -> ChordNode:
        res_id = self.id
        res_hex = self.id_hex

        if as_max:
            k = k - self.max_id
            res_id += self.max_id
            res_hex = hex(res_id)[2:]
        
        #is me
        if (self.Ft[0].id < k or as_max or self.Ft[0].id > self.id) and k <= self.id:
            return ChordNode(res_id ,res_hex ,self.ip ,as_max)
        #is my succesor
        if self.id < k <= self.Ft[1].id:
            return self.Ft[1]
        
        # search in the table
        less_than_me = False
        if k < self.id:
            less_than_me = True
            k += self.max_id
        
        for i in range(2 ,len(self.Ft)):
            if ((i == (len(self.Ft) - 1)) or (self.Ft[i].id <= k < self.Ft[i + 1].id)):
                if less_than_me and self.Ft[i].as_max:
                    num = self.Ft[i].id - self.max_id
                    num_hex = hex(num)[2:]
                    return ChordNode(num ,num_hex ,self.Ft[i].ip ,False)
                else:
                    return self.Ft[i]
        

    def succ(self ,k ,owner_ip ,as_max ,req_id):
        who = self.succ_who(k ,as_max)
        self.update_log(f'who id:{who.id_hex} ip:{who.ip} as_max:{who.as_max}')
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
            self.update_log(f'accepting {hex(k)[2:]}')
            self.accept_succ(owner_ip ,req_id ,who.id_hex ,who.as_max)
        else:
            self.update_log(f'redirecting request to {who.id_hex}:{who.ip}')
            msg = ChordServer.create_msg(self.get_succ_req_cmd ,hex(k)[2:] ,owner_ip ,who.as_max ,req_id)
            self.send_til_success([who.ip] ,msg ,'redirect',self.port)


    def MaintainFt(self):
        while(True):
            sleep(5)   
            for i in range(1 ,len(self.Ft)):
                current = self.id + 2**(i - 1)
                who = self.succ_who(current ,False)
                if(who.ip != self.ip):
                    current_hex = hex(current)[2:]
                    who = self.ask_succ([who.ip] ,current_hex ,who.as_max)
                with self.Ft_lock:
                    self.Ft[i] = who
            self.update_log()

    def send_til_success(self ,ips ,msg ,req_name ,port):
        response = None
        while not response:
            response = self.send_and_close(ips ,msg ,port)
            if not response:
                self.update_log(f'failed to send {req_name} to {ips}:{port}')
                sleep(2)
        return response


            
    def confirm_new_prev(self ,succ_ip):
        msg = ChordServer.create_msg(self.confirm_cmd ,self.id_hex ,self.ip ,False ,0)
        self.update_log('starting to send (confirm)')
        self.send_til_success([succ_ip] ,msg ,'confirm',self.port)

    def rec_confirm_new_prev(self ,msg:ParsedMsg ,socket_client ,addr):
        self.update_log('inside rec_confirm')
        with self.Ft_lock:
            res_id = msg.id
            res_as_max = msg.as_max
            if msg.id > self.id:
                res_id += self.max_id
                res_as_max = True
            res_id_hex = hex(res_id)[2:]
            self.Ft[0] = ChordNode(res_id ,res_id_hex ,msg.owner_ip ,res_as_max)
        with self.busy_lock:
            self.busy = False
        socket_client.send('Ok'.encode())
        socket_client.close()
        self.update_log('confirmed new prev')
        
    
    def rec_outside_get(self ,msg:ParsedMsg ,socket_client ,addr):
        socket_client.close()
        print(f'recived outside req for {msg.id_hex}')
        self.update_log(f'start rec outside_get {msg.id_hex}')
        # {type:'logger' , proto:'chord'}]   
        holder : ThreadHolder= self.state_storage.insert_state()
        while not holder.desired_data:
            me = self.succ(msg.id ,self.ip ,False ,holder.id)
            self.update_log(f'me:{str(me)}')
            if not me:
                self.update_log('starting to wait')
                holder.hold_event.wait(5)
            else:
                holder.desired_data = ChordNode(self.id ,self.id_hex ,self.ip ,False)
            if not holder.desired_data:
                self.update_log(f'failed to get succ of {msg.id}')
        self.state_storage.delete_state(holder.id)
        self.update_log('responding to outside')
        print('starting to respond')
        # type: LOGGER
        # proto: CHORD_RESPONSE
        # IP: [Replicas del sucesor]
        msg_dict = {
            'type': util.LOGGER ,
            'proto': util.CHORD_RESPONSE ,
            'IP':[holder.desired_data.ip] ,
            'id_req':msg.req_id
        }
        socket_client = socket(AF_INET, SOCK_STREAM)
        socket_client.connect((addr[0], util.PORT_GENERAL_LOGGER))
        socket_client.send(util.encode(msg_dict))
        socket_client.close()
        self.update_log(f'end outside req')
        print(f'end outside req')

    def rec_get_succ_req(self ,msg:ParsedMsg ,socket_client ,addr):
        socket_client.send('Ok'.encode())
        self.update_log(f'start rec get_succ_req {msg.id_hex}')
        self.succ(msg.id ,msg.owner_ip ,msg.as_max ,msg.req_id)
        socket_client.close()
        self.update_log('end rec get_succ_req')

    def rec_get_succ_resp(self ,msg:ParsedMsg ,socket_client ,addr):
        self.update_log('start rec get_succ_resp')
        holder = self.state_storage.get_state(msg.req_id)
        holder.desired_data = ChordNode(msg.id ,msg.id_hex ,addr[0] ,msg.as_max)
        holder.hold_event.set()
        self.state_storage.delete_state(msg.req_id)
        socket_client.send('Ok'.encode())
        socket_client.close()
        self.update_log('end rec get_succ_resp')

    def ImYSucc(self ,prev_ip):
        msg = ChordServer.create_msg(self.ImYSucc_cmd ,self.id_hex ,self.ip ,False ,0)
        self.update_log('starting to send (ImYSucc)')
        self.send_til_success([prev_ip] ,msg ,'ImYSucc',self.port)
        

    def rec_ImYSucc(self ,msg:ParsedMsg ,socket_client ,addr):
        self.update_log('start rec ImYSucc')
        res_id = msg.id
        #Si el nuevo sucesor es nuevo minimo y yo soy maximo
        if msg.id < self.id:
            res_id += self.max_id
        res_hex = hex(res_id)[2:]
        with self.Ft_lock:
            self.Ft[1] = ChordNode(res_id ,res_hex ,msg.owner_ip ,msg.id < self.id)
        socket_client.send('Ok'.encode())
        socket_client.close()
        self.update_log('end rec ImYSucc')

    def ImYPrev(self ,succ_ip):
        msg = ChordServer.create_msg(self.ImYPrev_cmd ,self.id_hex ,self.ip ,False ,0)
        self.update_log('starting to send (ImYPrev)')
        response = self.send_til_success([succ_ip] ,msg ,'ImYPrev',self.port)
        arr = response.decode().split(',')
        return arr[0] , ChordNode(int(arr[1] ,16) ,arr[1] ,arr[2] ,arr[3] == 'True')

    def rec_ImYPrev(self ,msg:ParsedMsg ,socket_client ,addr):
        self.update_log('start rec ImYPrev')
        busy = None
        with self.busy_lock:
            busy = self.busy
            if not self.busy:
                self.busy = True
        if busy:
            socket_client.send('Busy,0,none,none'.encode()) 
        else:
            result = None
            with self.Ft_lock:
                result = self.Ft[0]
            res_as_max = result.as_max
            res_id = result.id
            # Si el que se va a insertar es nuevo maximo
            if msg.id > self.id:
                res_as_max = False
                res_id -= self.max_id
            res_id_hex = hex(res_id)[2:]
            # (Busy|Ok) ,id ,ip
            socket_client.send(f'Ok,{res_id_hex},{result.ip},{res_as_max}'.encode()) 
        socket_client.close()
        self.update_log('end rec ImYPrev')

    def register_in_entry(self):
        msg_dict = {
            'type': util.CHORD ,
            'proto': util.INSERTED_LOGGER_REQUEST
        }
        self.update_log('starting to send (register)')
        self.send_til_success(self.entry_points ,json.dumps(msg_dict) ,'register' ,util.PORT_GENERAL_ENTRY)



    def accept_succ(self ,owner_ip ,req_id ,id ,as_max):
        msg = ChordServer.create_msg(self.get_succ_resp_cmd ,id ,self.ip ,as_max ,req_id)
        self.update_log('starting to send (accept)')
        self.send_til_success([owner_ip] ,msg ,'accept',self.port)

    def ask_succ(self , ips:str , id_hex:int , as_max:bool) -> ChordNode:
        holder = self.state_storage.insert_state()
        while True: 
            for _ in range(10):
                msg = ChordServer.create_msg(self.get_succ_req_cmd ,id_hex ,self.ip ,as_max ,holder.id)
                self.update_log(f'starting to send (ask_succ to {ips} for {id_hex} as_max:{str(as_max)})')
                self.send_til_success(ips ,msg ,'ask_succ',self.port)
                self.update_log(f'waiting for response in ask_succ')
                holder.hold_event.wait(5)
                if holder.desired_data:
                    self.state_storage.delete_state(holder.id)
                    break
            if holder.desired_data:
                break
            self.update_log('timout waiting 10 times')
            sleep(2)
        return holder.desired_data
    
    def build_insert_response(self):
        # # # type: Chord(Utils)
        # proto: NEW_LOGGER_RESPONSE(Utils)
        # sucesors: [los ips de los sucesores]
        # siblings: [lista de replicas]
        # chord_id: mi sha
        msg_dict = {
            'type': util.CHORD ,
            'proto': util.NEW_LOGGER_RESPONSE ,
            'sucesors': [self.Ft[1].ip] ,
            'siblings':[] ,
            'chord_id': self.id_hex
        }
        return json.dumps(msg_dict)


    def parse_msg(self ,raw_msg:str) -> ParsedMsg:
        # # type: LOGGER
        # proto: CHORD_REQUEST
        # hash: (el nick para hashear) 
        # id_req: (int)
        
        msg_dict = util.decode(raw_msg)
        # print('dict parsed')
        result = None
        if msg_dict['type'] == util.LOGGER:
            # print('is logger request')
            print(f'recived outside req for {msg_dict["hash"]}')
            # nick_hash = hashlib.sha256(msg_dict['hash'].encode()).hexdigest()
            nick_hash = hex(int(msg_dict['hash']))[2:]
            result = ParsedMsg(self.outside_cmd ,nick_hash ,'0' ,'False' ,msg_dict['id_req'])
        else:
            # print('is intern request')
            arr = msg_dict['content'].split(',')
            result = ParsedMsg(arr[0] , arr[1] , arr[2] , arr[3] ,arr[4])
        # print('parsed')
        return result


    def create_msg(cmd:str ,k:int , owner_ip:str , as_max:bool , req_id:int):
        msg = {
            'type': util.CHORD_INTERNAL ,
            'content': ','.join([str(cmd) ,str(k) ,str(owner_ip) ,str(as_max) ,str(req_id) ,])
        }
        return json.dumps(msg)

    def send_and_close(self ,ips ,msg: str, port):
        response = None
        shuffle(ips)
        for ip in ips:
            for _ in range(10):    
                try:
                    s = socket(AF_INET ,SOCK_STREAM)
                    self.update_log(f'connecting to {ip}:{port}')
                    s.connect((ip ,port))            
                    s.send(msg.encode())            
                    response = s.recv(15000)            
                    s.close()
                    if not (response == None):
                        if ip in self.request_count.keys():
                            self.request_count[ip] += 1
                        else:
                            self.request_count[ip] = 1
                        break
                except Exception as e:
                    self.update_log(str(e)) 
            if not (response == None):
                break
        self.update_log('send ended')
        return response

id = int(input())
server = ChordServer(id,'log',15000,'file')
server.start()
    



