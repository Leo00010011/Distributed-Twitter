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

    
class ChordNode:
    def __init__(self ,id ,id_hex ,ip_list ,as_max):
       self.id = TwoBaseId(id,id_hex)      
       self.ip_list = ip_list     
       self.as_max = as_max     
    
    def __str__(self) -> str:
        d = {
            'id_hex': self.id.hex,
            'ip_list': self.ip_list,
            'as_max': self.as_max
        }
        return json.dumps(d)

    def build_from_msg(s):
        if s == 'none':
            return None
        d = json.loads(s)
        return ChordNode(int(d['id_hex'],16),d['id_hex'],d['ip_list'],d['as_max'])

class TwoBaseId:
    def __init__(self,id,id_hex):
        self.dec = id
        self.hex = id_hex

class ChordServer:
    def __init__(self,DHT_name ,port ,disable_log,id = None, print_table = False):
        self.DHT_name = DHT_name
        self.disable_realtime_log = disable_log
        self.log_lock = Lock()
        self.request_count = {}
        self.state_storage = StateStorage()
        self.port = port
        self.print_table = print_table
        self.entry_points = []
        with open('entrys.txt' , 'r') as ft:
            for ip in ft.read().split(sep='\n'):
                self.entry_points.append(str(ip))
        self.server : MultiThreadedServer = MultiThreadedServer(self.port ,100 ,100 ,2 ,self.create_dispatcher() , log = False)
        self.get_succ_req_cmd = 'get_succ_req'
        self.get_succ_resp_cmd = 'get_succ_resp'
        self.ImYSucc_cmd = 'ImYSucc'
        self.ImYPrev_cmd = 'ImYPrev'
        self.ImYRep_cmd = 'ImYRep'
        self.outside_cmd = 'outside'
        self.confirm_cmd = 'confirm_new_succ'
        self.new_rep_cmd = 'new_rep'
        self.new_succ_cmd = 'new_succ'
        self.new_prev_cmd = 'new_prev'
        self.get_reps_cmd = 'get_reps'
        self.busy = False
        self.busy_lock = Lock()
        self.Ft_lock = Lock()
        self.ip = get_my_ip()
        self.id_hex = None
        self.id = None
        self.thread_count = 100
        self.thread_count_Lock = Lock()
        # self.max_id = int(''.join(['f' for _ in range(64)]) ,16)
        self.max_id = 1000000
        if id == None: 
            self.id_hex = hashlib.sha256(self.ip.encode()).hexdigest()
            self.id = int(self.id_hex ,16)
        else:
            self.id_hex = hex(id)[2:]
            self.id = id
        self.Ft: list[tuple[ChordNode,bool]] = [None]*floor(log2(self.max_id + 1))
        self.log: list[str] = []
        self.reps = [self.ip]
        self.response = {
            self.confirm_cmd:self.rec_confirm_new_prev ,
            self.ImYSucc_cmd:self.rec_ImYSucc ,
            self.ImYPrev_cmd:self.rec_ImYPrev ,
            self.ImYRep_cmd : self.rec_ImYRep,
            self.get_succ_req_cmd:self.rec_get_succ_req ,
            self.get_succ_resp_cmd:self.rec_get_succ_resp ,
            self.outside_cmd: self.rec_outside_get,
            self.new_rep_cmd: self.rec_new_rep,
            self.new_prev_cmd: self.rec_new_Prev,
            self.new_succ_cmd: self.rec_new_Succ,
            self.get_reps_cmd: self.rec_get_reps
        }

    def insert_as_first(self):
        num = self.id + self.max_id
        num_hex = hex(num)[2:]
        self.Ft[0] = (ChordNode(num ,num_hex ,self.reps ,as_max=True),True)
        self.Ft[1] = (ChordNode(num ,num_hex ,self.reps ,as_max=True),True)
        for i in range(2 ,len(self.Ft)):
            self.Ft[i] = self.Ft[1]

    def insert(self ,ips):
        node = self.ask_succ(ips ,self.id_hex ,False)
        print(f'node : {node}')
        prev_node = None
        succ_node = None
        if node.id.hex == self.id_hex:
            prev_node, succ_node = self.insert_rep(node)
        else:
            prev_node, succ_node = self.insert_new_node(ips,node)
        self.Ft[0] = (prev_node,self.ip in prev_node.ip_list)
        me_as_succ = self.ip in succ_node.ip_list
        for i in range(1 ,len(self.Ft)):
            self.Ft[i] = (succ_node,me_as_succ)

    def insert_new_node(self,ips,succ_node) -> tuple[ChordNode,ChordNode]:
        response = 'Busy'
        while response == 'Busy':
            response , prev_node = self.ImYPrev(succ_node)
            if response != 'Busy':
                break
            self.update_log(f'{succ_node.ip} is busy')
            sleep(randint(1 ,5))
            succ_node = self.ask_succ(ips ,self.id_hex ,False)
        self.ImYSucc(prev_node)
        self.confirm_new_prev(succ_node)
        return prev_node, succ_node

    def insert_rep(self,rep_node: ChordNode) -> tuple[ChordNode,ChordNode]:
        response = 'Busy'
        while response == 'Busy':
            response, prev_node, succ_node, reps = self.ImYRep(rep_node)
            if response != 'Busy':
                break
            self.update_log(f'{succ_node.ip_list} is busy')
            sleep(randint(1 ,5))
        for rep in reps:
            if rep != self.ip:
                self.reps.append(rep)
        self.new_rep(rep_node)
        return prev_node, succ_node

    def start(self):
        Thread(target= ChordServer.sleeping_log , args=[self] ,daemon = True).start()
        server_thread = Thread(target= self.server.start_server)
        server_thread.start()
        print('some node')
        ips = self.get_some_node()
        if len(ips) == 0:
            self.update_log('is first')
            print('soy primero')
            self.insert_as_first()
        else:
            print('NO soy PRIMERO')
            print(ips)
            self.insert(ips)
        print('insert finished and starting to maintain')
        Thread(target=ChordServer.MaintainFt , args=[self] , daemon=True).start()
        
        msg = self.build_insert_response()
        print('builded msg')
        self.send_and_close(['127.0.0.1'],msg,util.PORT_GENERAL_LOGGER)
        print('before register')
        self.register_in_entry()
        print('registered')
        self.update_log(f'inserted')
        server_thread.join()


    def create_dispatcher(self):
        def dispatcher(id:int ,task: tuple[socket ,object] ,event:Event ,storage):
            with self.thread_count_Lock:
                self.thread_count -= 1
            (socket_client , addr_client) = task
            try:                
                msg = socket_client.recv(15000)
                parsed_msg = self.parse_msg(msg)
            except Exception as e:
                self.update_log(f'Bad Request: {msg}')
                self.update_log(str(e))
                return
            self.update_log(f'recived: {parsed_msg}')
            try:
              self.response[parsed_msg['cmd']](parsed_msg ,socket_client ,addr_client)
            except:
              return
            with self.thread_count_Lock:
                self.thread_count += 1

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
            if self.print_table:
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
            if self.print_table:
                print('request count')
                for key in self.request_count.keys():
                    print(f'{key}: {self.request_count[key]}')
                print(f'thread_count: {self.thread_count}')
                print('Replicas:')
                for rep in self.reps:
                    print(rep)
                print('FingerTable:')
                with self.Ft_lock:
                    for index , node in enumerate(self.Ft):
                        if not node:
                            print('Not initialiced')
                        else:
                            print(f'{index})   ip:{node[0].ip_list}   id:{node[0].id.dec}   as_max: {node[0].as_max} mine: {self.Ft[index][1]}')
                            # print(f'{index})   ip:{node[0].ip_list}   id:{node[0].id.dec}')





    def succ_who(self ,k,as_max) -> tuple[ChordNode,bool]:
        res_id = self.id
        res_hex = self.id_hex
        if as_max:
            k = k - self.max_id
            res_id += self.max_id
            res_hex = hex(res_id)[2:]
            

        #is me
        if (self.Ft[0][0].id.dec < k or as_max or self.Ft[0][0].id.dec > self.id) and k <= self.id:
            return ChordNode(res_id ,res_hex ,self.reps ,as_max), True
            
        #is my succesor
        if self.id < k <= self.Ft[1][0].id.dec:
            return self.Ft[1]
        
        # search in the table
        less_than_me = False
        if k < self.id:
            less_than_me = True
            k += self.max_id
        
        for i in range(2 ,len(self.Ft)):
            if ((i == (len(self.Ft) - 1)) or (self.Ft[i][0].id.dec <= k < self.Ft[i + 1][0].id.dec)):
                if less_than_me and self.Ft[i][0].as_max:
                    num = self.Ft[i][0].id.dec - self.max_id
                    num_hex = hex(num)[2:]
                    return ChordNode(num ,num_hex ,self.Ft[i][0].ip_list ,False), self.Ft[i][1]
                else:
                    return self.Ft[i]
        

    def succ(self ,id: TwoBaseId ,owner_ip ,as_max ,req_id):
        who, mine = self.succ_who(id.dec,as_max)
        self.update_log(f'who id:{who.id.hex} ip:{who.ip_list} as_max:{who.as_max}')
        if mine:
            if(owner_ip == self.ip):
                if as_max:
                    self.update_log('my self as_max')
                    holder = self.state_storage.get_state(req_id)
                    holder.desired_data = who
                    holder.hold_event.set()
                    return False
                return True
            self.update_log(f'accepting {id.hex}')
            print('accepting')
            self.accept_succ(owner_ip ,req_id ,who)
        else:
            self.update_log(f'redirecting request to {who.id.hex}:{who.ip_list}')
            msg = ChordServer.create_msg(cmd = self.get_succ_req_cmd ,id_hex = id.hex ,owner_ip = owner_ip ,as_max = who.as_max ,req_id = req_id)
            self.send_til_success(who.ip_list ,msg ,'redirect',self.port)
            return False


    def MaintainFt(self):
        while(True):
            with self.Ft_lock:
                if not self.Ft[0][1]:
                    self.get_reps(self.Ft[0][0])
            for i in range(1 ,len(self.Ft)):
                current = self.id + 2**(i - 1)
                who, mine = self.succ_who(current ,False)
                if not mine:
                    current_hex = hex(current)[2:]
                    who = self.ask_succ(who.ip_list ,current_hex ,who.as_max)
                with self.Ft_lock:
                    self.Ft[i] = (who,self.ip in who.ip_list)
            self.update_log()
            sleep(5)   
            
    def confirm_new_prev(self ,succ:ChordNode):
        print('starting confirm')
        msg = ChordServer.create_msg(cmd = self.confirm_cmd ,id_hex = self.id_hex , owner_ip = self.ip)
        self.update_log('starting to send (confirm)')
        self.send_til_success(succ.ip_list ,msg ,'confirm',self.port)

    def rec_confirm_new_prev(self ,msg:dict ,socket_client ,addr):
        print('recv confirm')
        self.update_log('inside rec_confirm')
        res_id_hex = msg['id_hex']
        res_id = int(res_id_hex,16)
        res_as_max = False
        if res_id > self.id:
            res_id += self.max_id
            res_id_hex = hex(res_id)[2:]
            res_as_max = True
        prev_node = None
        with self.Ft_lock:
            self.Ft[0] = (ChordNode(res_id ,res_id_hex ,[msg['owner_ip']] ,res_as_max),False)
            prev_node = self.Ft[0][0]
        
        with self.busy_lock:
            self.busy = False
        print('before new prev')
        self.new_Prev(prev_node)
        print('after new prev')
        socket_client.send('Ok'.encode())
        socket_client.close()
        self.update_log('confirmed new prev')
        
    
    def rec_outside_get(self ,msg ,socket_client ,addr):
        socket_client.close()
        print(f'recived outside req for {msg["id_hex"]}')
        self.update_log(f'start rec outside_get {msg["id_hex"]}')
        holder : ThreadHolder = self.state_storage.insert_state()
        print(f'antes del while')
        id = TwoBaseId(int(msg['id_hex'],16),msg['id_hex'] )
        while not holder.desired_data:
            mine = self.succ(id,self.ip ,False ,holder.id)
            self.update_log(f'me:{str(mine)}')
            print(f'me:{str(mine)}')
            if not mine:
                self.update_log('starting to wait')
                print('starting to wait')
                holder.hold_event.wait(5)
            else:
                holder.desired_data = ChordNode(self.id ,self.id_hex ,self.reps ,False)
            if not holder.desired_data:
                self.update_log(f'failed to get succ of {msg["id_hex"]}')
                print('fail to wait')
        self.state_storage.delete_state(holder.id)
        self.update_log('responding to outside')
        self.response_to_outside(holder.desired_data.ip_list,msg['req_id'])

    def response_to_outside(self,ip_list,req_id):
        print(f'ip_list:{ip_list}')
        print(f'req_id:{req_id}')
        self.update_log('responding to outside')
        print('starting to respond')
        msg_dict = {
            'type': util.LOGGER ,
            'proto': util.CHORD_RESPONSE ,
            'IP':ip_list,
            'id_request':req_id
        }
        
        print(f'msg to send {json.dumps(msg_dict)}')
        self.send_soft(['127.0.0.1'],json.dumps(msg_dict),'outside_resp',util.PORT_GENERAL_LOGGER,5,have_recv = False)

        print(f'end outside req')
        self.update_log(f'end outside req')

    def rec_get_succ_req(self ,msg ,socket_client ,addr):
        socket_client.send('Ok'.encode())
        socket_client.close()
        print('recv req')
        # print(f'recv succ for {msg["id_hex"]}')
        self.update_log(f'start rec get_succ_req {msg["id_hex"]}')
        id = TwoBaseId(int(msg["id_hex"],16),msg['id_hex'])
        self.succ(id,msg['owner_ip'] ,msg['as_max'] ,msg['req_id'])
        self.update_log('end rec get_succ_req')

    def rec_get_succ_resp(self ,msg ,socket_client ,addr):
        self.update_log('start rec get_succ_resp')
        holder = self.state_storage.get_state(msg['req_id'])
        if holder is None:
            return
        holder.desired_data = ChordNode.build_from_msg(msg['node'])
        holder.hold_event.set()
        self.state_storage.delete_state(msg['req_id'])
        socket_client.send('Ok'.encode())
        socket_client.close()
        self.update_log('end rec get_succ_resp')

    def get_reps(self,node:ChordNode):
        msg = ChordServer.create_msg(cmd = self.get_reps_cmd)
        response = self.send_soft(node.ip_list,msg,'get_reps',self.port,5)
        arr = json.loads(response)
        node.ip_list = arr

    def rec_get_reps(self ,msg ,socket_client ,addr):
        resp = json.dumps(self.reps)
        socket_client.send(resp.encode())
        socket_client.close()

    def new_Prev(self,prev_node):
        print('new_prev')
        msg = ChordServer.create_msg(cmd = self.new_prev_cmd,node = str(prev_node))
        for rep in self.reps:
            if rep != self.ip:
                self.send_soft([rep],msg,'new succ',self.port,5,have_recv=False)
        print('end new prev')

    def rec_new_Prev(self ,msg ,socket_client ,addr):
        print('recv new_prev')
        new_prev = ChordNode.build_from_msg(msg['node'])
        with self.Ft_lock:
            self.Ft[0] = (new_prev,False)
        socket_client.close()
        print('end recv new_prev')

    def new_Succ(self,succ_node):
        print('new_succ')
        msg = ChordServer.create_msg(cmd = self.new_succ_cmd,node = str(succ_node))
        for rep in self.reps:
            if rep != self.ip:                
                self.send_soft([rep],msg,'new succ',self.port,5,have_recv=False)
        print('end new succ')

    def rec_new_Succ(self ,msg ,socket_client ,addr):
        print(f'recv new_succ {msg}')
        
        new_succ = ChordNode.build_from_msg(msg['node'])
        with self.Ft_lock:
            self.Ft[1] = (new_succ,False)
        socket_client.close()
        print('end recv new_succ')

    def ImYSucc(self ,prev: ChordNode):
        print('starting ImYSucc')
        msg = ChordServer.create_msg(cmd = self.ImYSucc_cmd ,id_hex = self.id_hex ,owner_ip = self.ip)
        self.update_log('starting to send (ImYSucc)')
        self.send_til_success(prev.ip_list ,msg ,'ImYSucc',self.port)
        

    def rec_ImYSucc(self ,msg ,socket_client ,addr):
        print('Recv ImYSucc')
        self.update_log('start rec ImYSucc')
        res_hex = msg['id_hex']
        res_id = int(res_hex,16)
        as_max = False
        #Si el nuevo sucesor es nuevo minimo y yo soy maximo
        if res_id < self.id:
            res_id += self.max_id
            res_hex = hex(res_id)[2:]
            as_max = True
        succ_node = None
        with self.Ft_lock:
            self.Ft[1] = (ChordNode(res_id ,res_hex ,[msg['owner_ip']] ,as_max),False)
            succ_node = self.Ft[1][0]
        print('before new succ')
        self.new_Succ(succ_node)
        socket_client.send('Ok'.encode())
        socket_client.close()
        self.update_log('end rec ImYSucc')

    def ImYPrev(self ,succ: ChordNode):
        msg = ChordServer.create_msg(cmd = self.ImYPrev_cmd ,
                                     id_hex = self.id_hex ,
                                     owner_ip = self.reps)
        self.update_log('starting to send (ImYPrev)')
        print('starting ImYPrev')
        response = self.send_til_success(succ.ip_list ,msg ,'ImYPrev',self.port)
        print('out of send ImYPrev')
        arr = json.loads(response)
        return arr[0] , ChordNode.build_from_msg(arr[1])

    def rec_ImYPrev(self ,msg ,socket_client ,addr):
        self.update_log('start rec ImYPrev')
        print('recv ImYPrev')
        busy = None
        with self.busy_lock:
            busy = self.busy
            if not self.busy:
                self.busy = True
        if busy:
            socket_client.send('Busy,none'.encode()) 
        else:
            result = None
            with self.Ft_lock:
                result = self.Ft[0][0]
            msg_id = int(msg['id_hex'],16)
            res_id = result.id.dec
            res_id_hex = result.id.hex
            res_as_max = result.as_max
            # Si el que se va a insertar es nuevo maximo
            if msg_id > self.id:
                res_id -= self.max_id
                res_id_hex = hex(res_id)[2:]
                res_as_max = False
            s_res = str(ChordNode(res_id,res_id_hex,result.ip_list,res_as_max))
            # (Busy|Ok) ,id ,ip
            msg = json.dumps(['Ok',s_res])
            print('before resp ImYPrev')
            socket_client.send(msg.encode()) 
        socket_client.close()
        print('end ImYPrev')
        self.update_log('end rec ImYPrev')

    # Random entre actualizar la tabla o pedriselo al resto
    # Actualizar la tabla ya esta
    # Pedriselo al resto:
    #  - Pedir horas de actualizacion y aprovechar la respuesta para que te diga las replicas que conoce
    #       * Llevar la hora de la ultima actualizacion real
    #    * Aprovechar y actualizar el conteo de vivos
    #  - Si el mas actual es mas reciente que tu pidele la tabla
    #    * Buscar la forma de serializar la tabla

    def new_rep(self,rep_node: ChordNode):
        print(f'rep ip list{rep_node.ip_list}')
        for rep in rep_node.ip_list:
            msg = ChordServer.create_msg(cmd = self.new_rep_cmd, owner_ip = self.ip)
            self.send_soft([rep],msg,'new_rep',self.port,5)

    def rec_new_rep(self ,msg ,socket_client ,addr):
        print('recv new rep')
        if msg['owner_ip'] not in self.reps:
            self.reps.append(msg['owner_ip'])
        socket_client.send('Ok'.encode())

    def ImYRep(self, rep_node: ChordNode):
        msg = ChordServer.create_msg(cmd = self.ImYRep_cmd ,owner_ip = self.ip)
        print(msg)
        self.update_log('starting to send (ImYRep)')
        response = self.send_til_success(rep_node.ip_list ,msg ,'ImYRep',self.port)
        arr = json.loads(response)
        print(arr)
        return arr[0], ChordNode.build_from_msg(arr[1]),ChordNode.build_from_msg(arr[2]), arr[3]

    def rec_ImYRep(self ,msg ,socket_client :socket,addr):
        print('inside ImYRep')
        busy = False
        print('before busy')
        with self.busy_lock:
            busy = self.busy
        if busy:
            print('before busy')
            socket_client.send('Busy,none,none'.encode())
        else:
            print('prev succ')
            prev = None
            succ = None
            with self.Ft_lock:
                prev = self.Ft[0][0]
                succ = self.Ft[1][0]
            try:
                if msg['owner_ip'] not in self.reps:
                    self.reps.append(msg['owner_ip'])
            except Exception as e:
                print('----------')
                print(e)
                print(msg)
            print('before Ok')
            s = json.dumps(['Ok',str(prev),str(succ),self.reps])
            socket_client.send(s.encode())
        socket_client.close()

    def register_in_entry(self):
        msg_dict = {
            'type': util.CHORD ,
            'proto': util.INSERTED_LOGGER_REQUEST
        }
        self.update_log('starting to send (register)')
        self.send_til_success(self.entry_points ,json.dumps(msg_dict) ,'register' ,util.PORT_GENERAL_ENTRY)



    def accept_succ(self ,owner_ip ,req_id ,node:ChordNode):
        s_node = str(ChordNode(None,node.id.hex,self.reps,node.as_max))
        msg = ChordServer.create_msg(cmd = self.get_succ_resp_cmd ,node = s_node,req_id = req_id)
        self.update_log('starting to send (accept)')
        print('starting to send accept')
        self.send_til_success([owner_ip] ,msg ,'accept',self.port)
        print('ending to send accept')


    def ask_succ(self , ips:str , id_hex:int , as_max:bool) -> ChordNode:
        holder = self.state_storage.insert_state()
        while True: 
            for _ in range(10):
                msg = ChordServer.create_msg(cmd = self.get_succ_req_cmd ,id_hex = id_hex ,owner_ip = self.ip ,as_max = as_max ,req_id = holder.id)
                self.update_log(f'starting to send (ask_succ to {ips} for {id_hex} as_max:{str(as_max)})')
                print(f'BEFORE SEND: {ips} {msg}')
                self.send_til_success(ips ,msg ,'ask_succ',self.port)
                print('AFTER SEND')
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
        msg_dict = {
            'type': util.CHORD ,
            'proto': util.NEW_LOGGER_REQUEST,
            'sucesors': self.Ft[1][0].ip_list,
            'siblings':[] ,
            'chord_id': self.id_hex
        }
        return json.dumps(msg_dict)


    def parse_msg(self ,raw_msg:str):
        msg_dict = util.decode(raw_msg)
        if msg_dict['type'] == util.LOGGER:
            print(f'recived outside req for {msg_dict["hash"]}')
            nick_hash = hashlib.sha256(msg_dict['hash'].encode()).hexdigest()
            # nick_hash = hex(int(msg_dict['hash']))[2:]
            print(nick_hash)
            msg_dict = {
                'cmd': self.outside_cmd,
                'id_hex': nick_hash,
                'req_id': msg_dict['id_request']
            }
        return msg_dict


    def create_msg(**kwarg):
        kwarg['type'] = util.CHORD_INTERNAL 
        return json.dumps(kwarg)

    def send_til_success(self ,ips ,msg ,req_name ,port):
        response = None
        while not response:
            response = self.send_and_close(ips ,msg ,port)
            if not response:
                self.update_log(f'failed to send {req_name} to {ips}:{port}')
                sleep(2)
        return response
    
    def send_soft(self,ips ,msg ,req_name ,port, try_count, have_recv = True):
        response = None
        print(f'inside soft ({req_name})')
        for _ in range(try_count):
            print('inside for')
            response = self.send_and_close(ips ,msg ,port, have_recv)
            if not response:
                print('no response')
                self.update_log(f'failed to send {req_name} to {ips}:{port}')
                sleep(2)
            else:
                break
        return response

    def send_and_close(self ,ips ,msg: str, port,have_recv = True):
        response = None
        shuffle(ips)
        for ip in ips:
            for _ in range(10):    
                try:
                    s = socket(AF_INET ,SOCK_STREAM)
                    self.update_log(f'connecting to {ip}:{port}')
                    s.connect((ip ,port))            
                    s.send(msg.encode()) 
                    if have_recv:           
                        response = s.recv(15000)
                    else:
                        response = 'Ok'
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
pt = input() == 'si'
server = ChordServer('log',15000,'file',id = id,print_table= pt)
server.start()





