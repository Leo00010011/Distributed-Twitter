import socket
from socket import AF_INET, SOCK_STREAM
from threading import Thread, Event
import hashlib
import random


try:
    import util
    from server import Server
    from util import Stalker, Dispatcher
    from util import CLIENT, ENTRY_POINT, LOGGER, CHORD
    from util import LOGIN_REQUEST, LOGIN_RESPONSE, CHORD_REQUEST, CHORD_RESPONSE, NEW_LOGGER_REQUEST, NEW_LOGGER_RESPONSE, ALIVE_REQUEST, ALIVE_RESPONSE, REGISTER_REQUEST, REGISTER_RESPONSE, TRANSFERENCE_REQUEST
    from util import TRANSFERENCE_RESPONSE, TRANSFERENCE_OVER, CREATE_TWEET_REQUEST, CREATE_TWEET_RESPONSE, RETWEET_REQUEST, RETWEET_RESPONSE, FOLLOW_REQUEST, FOLLOW_RESPONSE, FEED_REQUEST, FEED_RESPONSE
    from util import PROFILE_REQUEST, PROFILE_RESPONSE, NEW_ENTRYPOINT_REQUEST, NEW_ENTRYPOINT_RESPONSE, LOGOUT_REQUEST, LOGOUT_RESPONSE, GET_TOKEN, RECENT_PUBLISHED_REQUEST, RECENT_PUBLISHED_RESPONSE, CHECK_TWEET_REQUEST, CHECK_TWEET_RESPONSE
    from util import PORT_GENERAL_ENTRY, CHORD_PORT, PORT_GENERAL_LOGGER
    import view
    from threaded_server import MultiThreadedServer
except:
    import API.util as util
    from API.server import Server
    from API.util import Stalker, Dispatcher
    from API.util import CLIENT, ENTRY_POINT, LOGGER, CHORD
    from API.util import LOGIN_REQUEST, LOGIN_RESPONSE, CHORD_REQUEST, CHORD_RESPONSE, NEW_LOGGER_REQUEST, NEW_LOGGER_RESPONSE, ALIVE_REQUEST, ALIVE_RESPONSE, REGISTER_REQUEST, REGISTER_RESPONSE, TRANSFERENCE_REQUEST
    from API.util import TRANSFERENCE_RESPONSE, TRANSFERENCE_OVER, CREATE_TWEET_REQUEST, CREATE_TWEET_RESPONSE, RETWEET_REQUEST, RETWEET_RESPONSE, FOLLOW_REQUEST, FOLLOW_RESPONSE, FEED_REQUEST, FEED_RESPONSE
    from API.util import PROFILE_REQUEST, PROFILE_RESPONSE, NEW_ENTRYPOINT_REQUEST, NEW_ENTRYPOINT_RESPONSE, LOGOUT_REQUEST, LOGOUT_RESPONSE, GET_TOKEN, RECENT_PUBLISHED_REQUEST, RECENT_PUBLISHED_RESPONSE, CHECK_TWEET_REQUEST, CHECK_TWEET_RESPONSE
    from API.util import PORT_GENERAL_ENTRY, CHORD_PORT, PORT_GENERAL_LOGGER
    import API.view as view
    from API.threaded_server import MultiThreadedServer

NEW_NODE = 0
REPLIC_NODE = 1

USER_TABLE = 0
TOKEN_TABLE = 1
TWEET_TABLE = 2
RETWEET_TABLE = 3
FOLLOW_TABLE = 4
class TweeterServer(MultiThreadedServer):
    
    def __init__(self,port: int, task_max: int, thread_count: int, timout: int, parse_func):

        MultiThreadedServer.__init__(self,port, task_max, thread_count, timout, self.switch)
        
        self.entry_point_ips = []
        self.node_sibiling = []
        self.primary = []
        self.siblings = []
        self.is_primary = False
        self.my_ip = socket.gethostbyname(socket.gethostname())
        
        with open('entrys.txt', 'r') as ft:
            for ip in ft.read().split(sep='\n'):
                self.entry_point_ips.append(str(ip))
        self.current_index_entry_point_ip = rand.randint(0, len(self.entry_point_ips))
        self.chord_id = None

    def switch(self, id:int, task: tuple[socket,object], event:Event, storage):
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
        
        if type_rqst == CHORD:
            
            if proto_rqst == NEW_LOGGER_REQUEST:
                self.new_logger_response(socket_client, addr_client, data_dict,storage)
            
            

        if type_rqst == ENTRY_POINT:
            
            if proto_rqst == LOGIN_REQUEST:
                self.login_request(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == LOGOUT_REQUEST:
                self.logout_request(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == REGISTER_REQUEST:
                self.register_request(socket_client, addr_client, data_dict, storage)
            
            elif proto_rqst in  (CREATE_TWEET_REQUEST, FOLLOW_REQUEST, RETWEET_REQUEST, FEED_REQUEST, PROFILE_REQUEST):
                TweetServer.tweet_request(socket_client, addr_client, data_dict, storage)
            
            elif proto_rqst == ALIVE_REQUEST:
                self.alive_request(socket_client, addr_client, data_dict, storage)
                      
        elif type_rqst == LOGGER:
            
            if proto_rqst == LOGIN_REQUEST:
                self.get_token(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == LOGOUT_REQUEST:
                self.get_logout(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == REGISTER_REQUEST:
                self.get_register(socket_client, addr_client, data_dict, storage)
            
            elif proto_rqst in  (LOGIN_RESPONSE, REGISTER_RESPONSE, CHORD_RESPONSE, LOGOUT_RESPONSE): 
                self.set_data(socket_client, addr_client, data_dict,storage)
            
        elif type_rqst == TWEET:
            
            if proto_rqst == CREATE_TWEET_REQUEST:
                self.create_tweet(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == FOLLOW_REQUEST:
                self.create_follow(socket_client, addr_client, data_dict,storage)
            elif proto_rqst == RETWEET_REQUEST: 
                self.create_retweet(socket_client, addr_client, data_dict,storage)
            elif proto_rqst == FEED_REQUEST:
                self.feed_get(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == PROFILE_REQUEST:
                self.profile_get(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == RECENT_PUBLISHED_REQUEST:
                self.recent_publish(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == CHECK_TWEET_REQUEST:
                self.tweet_check(socket_client, addr_client, data_dict, storage)
            elif proto_rqst in (CREATE_TWEET_RESPONSE, FOLLOW_RESPONSE, RETWEET_RESPONSE, FEED_RESPONSE, PROFILE_RESPONSE, RECENT_PUBLICHED_RESPONSE, CHECK_TWEET_RESPONSE):
                self.set_data(socket_client, addr_client, data_dict,storage)
        
        else: 
            pass
        #TODO error de tipo
        
    def register_request(self, socket_client, addr_client, data_dict, storage):
        '''
        Registrar a un usuario en la red social
        ------------------------------------
        `data_dict['name']`: Nombre de usuario
        `data_dict['nick']`: Alias de usuario
        `data_dict['password']`: Contrasenna
        '''
        socket_client.close()
        #pedir un evento para m\'aquina de estado 
        state = storage.insert_state()

        #Hay que usar Chord para ver quien tiene a ese Nick
        nick = data_dict['nick']
        data = {
                "type" : LOGGER,
                "proto": CHORD_REQUEST,
                "hash": nick,
                "id_request": state.id,
        } #Construir la peticion del chord

        skt = socket.socket(AF_INET,SOCK_STREAM)
        skt.connect(('127.0.0.1',CHORD_PORT))
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
                "id_request": state2.id,
            }
            skt = socket.socket(AF_INET,SOCK_STREAM)
            skt.connect((state.desired_data['IP'],CHORD_PORT))
            skt.send(util.encode(data))

            w = state2.event_holder.wait(5)
            state = storage.get_state(state2.id)
            storage.delete_state(state.id)
            
            if w:
                #reenviar mensaje de autenticacion
                try:
                    state.desired_data['id_request'] = data_dict['id_request']

                    socket_client = socket.socket(AF_INET,SOCK_STREAM)
                    socket_client.connect((addr_client[0],PORT_GENERAL_ENTRY))
                    socket_client.send(util.encode(state.desired_data))
                    socket_client.close()
                except:
                    pass

        data = {
                    'type':LOGGER,
                    'proto': REGISTER_RESPONSE,
                    'succesed': False,
                    'error': 'Something went wrong in the network connection',
                    'id_request': data_dict['id_request']
           }
        
        socket_client = socket.socket(AF_INET,SOCK_STREAM)
        socket_client.connect((addr_client[0],PORT_GENERAL_ENTRY))
        socket_client.send(util.encode(data))
        socket_client.close()
    
    def login_request(self, socket_client, addr_client, data_dict, storage):
        '''
        Solicitud de inicio de sesion de usuario
        -------------
        `data_dict['nick']`: Nick
        `data_dict['password']`: Contrasenna
        '''

        socket_client.close()
        #pedir un evento para m\'aquina de estado 
        state = storage.insert_state()

        #Hay que usar Chord para ver quien tiene a ese Nick
        nick = data_dict['nick']
        data = {
                "type" : LOGGER,
                "proto": CHORD_REQUEST,
                "hash": nick,
                "id_request": state.id,
        } #Construir la peticion del chord
        
        skt = socket.socket(AF_INET,SOCK_STREAM)
        skt.connect(('127.0.0.1',CHORD_PORT))
        skt.send(util.encode(data))
        
        w = state.hold_event.wait(5)
        state = storage.get_state(state.id)
        storage.delete_state(state.id)
        
        if w:
            #Escribirle al server que tiene al usuario
            state2 = storage.get_state()
            data = {
                "type": LOGGER,
                "proto": LOGIN_REQUEST,
                "nick": data_dict["nick"],
                "password": data_dict["password"],
                "id_request": state2.id,
            }
            skt = socket.socket(AF_INET,SOCK_STREAM)
            skt.connect((state.desired_data['IP'],CHORD_PORT))
            skt.send(util.encode(data))

            w = state2.event_holder.wait(5)
            state = storage.get_state(state2.id)
            storage.delete_state(state.id)
            
            if w:
                #reenviar mensaje de autenticacion
                try:
                    state.desired_data['id_request'] = data_dict['id_request']

                    socket_client = socket.socket(AF_INET,SOCK_STREAM)
                    socket_client.connect((addr_client[0],PORT_GENERAL_ENTRY))
                    socket_client.send(util.encode(state.desired_data))
                    socket_client.close()
                    return

                except:
                    pass

        data = {
                'type':LOGGER,
                'proto': LOGIN_RESPONSE,
                'succesed': False,
                'token': None,
                'error': 'Something went wrong in the network connection',
                'id_request': data_dict['id_request']
           }
        
        socket_client = socket.socket(AF_INET,SOCK_STREAM)
        socket_client.connect((addr_client[0],PORT_GENERAL_ENTRY))
        socket_client.send(util.encode(data))
        socket_client.close()

    def logout_request(self, socket_client, addr_client, data_dict, storage):
        

        socket_client.close()
        state = storage.insert_state()

        #Hay que usar Chord para ver quien tiene a ese Nick
        nick = data_dict['nick']
        data = {
                "type" : LOGGER,
                "proto": CHORD_REQUEST,
                "hash": nick,
                "id_request": state.id,
        } #Construir la peticion del chord
        
        skt = socket.socket(AF_INET,SOCK_STREAM)
        skt.connect(('127.0.0.1',CHORD_PORT))
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
                "token": data_dict["token"],
                "id_request": state2.id,
            }
            skt = socket.socket(AF_INET,SOCK_STREAM)
            skt.connect((state.desired_data['IP'],CHORD_PORT))
            skt.send(util.encode(data))


            w = state2.event_holder.wait(5)
            state = storage.get_state(state2.id)
            storage.delete_state(state.id)
            
            if w:
                #reenviar mensaje de autenticacion
                try:
                    state.desired_data['id_request'] = data_dict['id_request']

                    socket_client = socket.socket(AF_INET,SOCK_STREAM)
                    socket_client.connect((addr_client[0],PORT_GENERAL_ENTRY))
                    socket_client.send(util.encode(state.desired_data))
                    socket_client.close()
                    return
                except:
                    pass

        data = {
                'type':LOGGER,
                'proto': LOGOUT_RESPONSE,
                'succesed': False,
                'error': 'Something went wrong in the network connection',
                'id_request': data_dict['id_request']
           }
        
        socket_client = socket.socket(AF_INET,SOCK_STREAM)
        socket_client.connect((addr_client[0],PORT_GENERAL_ENTRY))
        socket_client.send(util.encode(state.desired_data))
        socket_client.close()
       
    def get_register(self, socket_client, addr_client, data_dict, storage):
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
                    'proto': REQUEST_RESPONSE,
                    'succesed': True,
                    'error': None,
                    'id_request': data_dict['id_request']
                }
            except:
                data = {
                    'type': LOGGER,
                    'proto': REQUEST_RESPONSE,
                    'succesed': False,
                    'error': 'Error trying to register',
                    'id_request': data_dict['id_request']
                }
        else:
            data = {
                    'type': LOGGER,
                    'proto': REQUEST_RESPONSE,
                    'succesed': False,
                    'error': 'User Nick must be unique',
                    'id_request': data_dict['id_request']
                }
        
        socket_client.send(util.encode(data))
        socket_client.close()  

    def set_data(self, socket_client, addr_client, data_dict, storage):
        Id = data_dict["id_request"]
        state = storage.get_state(Id)
   
        state.desired_data = data_dict
        state.hold_event.set()
        socket_client.close()

    def get_token(self, socket_client, addr_client, data_dict, storage):
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
                    'id_request': data_dict['id_request']
                }
            else:
                data={
                    'type': LOGGER,
                    'proto': LOGIN_RESPONSE,
                    'succesed': False,
                    'token': None,
                    'error': "Invalid nick or password",
                    'id_request': data_dict['id_request']
                }     
        except:
                data={
                    'type': LOGGER,
                    'proto': LOGIN_RESPONSE,
                    'succesed': False,
                    'token': None,
                    'error': "User not register",
                    'id_request': data_dict['id_request']
                }
        
        socket_client.send(util.encode(data))
        socket_client.close()

    def get_logout(self, socket_client, addr_client, data_dict, storage):
        nick = data_dict["nick"]
        token = data_dict["token"]
        if view.CheckToken(token, nick):
            if view.RemoveToken(nick, token):
                data ={
                    'type':LOGGER,
                    'proto': LOGOUT_REQUEST,
                    'succesed': True,
                    'error': None,
                    'id_request':data_dict['id_request']
                }
            else:
                data ={
                    'type':LOGGER,
                    'proto': LOGOUT_REQUEST,
                    'succesed': False,
                    'id_request':data_dict['id_request'],
                    'error': "Error removing login"
                }
        else:
            data = {
                    'type':LOGGER,
                    'proto': LOGOUT_REQUEST,
                    'succesed': False,
                    'id_request':data_dict['id_request'],
                    'error': "Invalid user session data"
                }
        
        socket_client.send(util.encode(data))
        socket_client.close()

    def alive_request(self, socket_client, addr_client, data_dict, storage):
        data = {
            'type': LOGGER,
            'proto': ALIVE_RESPONSE,
        }
        socket_client.send(util.encode(data))
        socket_client.close()

    # def data_transfer_request(self, socket_client, addr_client, data_dict, storage):
    #     """
    #     Peticion de transferencia de datos
    #     datadict['block']: Numero de bloques enviados y recibidos
    #     datadict['chord_id']: Nuemro a partir del cual buscar
    #     """

    #     block = data_dict['block']
    #     hash_limit = data_dict['chord_id']
    #     table = data_dict['table']

    #     data = {
    #         'type': LOGGER,
    #         'proto': TRANSFERENCE_RESPONSE,
    #         'block': block + 1,
    #         'chord_id': hash_limit,
    #         'table': table
    #     }

    #     if table == 'tweet':
    #         table_data = view.GetTweetRange(hash_limit, (block +1)*10,10) 
    #     if table == 'retweet':
    #         table_data = view.GetRetweetRange(hash_limit, (block +1)*10,10) 
    #     if table == 'follow':
    #         table_data = view.GetFollowRange(hash_limit, (block +1)*10,10) 
    #     if table == 'token':
    #         table_data = view.GetTokenRange(hash_limit, (block +1)*10,10) 
    #     if table == 'user':
    #         table_data = view.GetUserPaswordRange(hash_limit, (block+1) * 10,10)
        
    #     i = 0
    #     for d in table_data:
    #         data[f'data_{i}'] = {}
    #         if table == 'tweet':
    #             data[f'data_{i}']["nick"] = d.user.nick
    #             data[f'data_{i}']['text'] = d.text
    #             data[f'data_{i}']["date"] = d.date
            
    #         if table == 'retweet':
    #             data[f'data_{i}']["nick"] = d.user.nick
    #             data[f'data_{i}']['date_tweet'] = d.date_tweet
    #             data[f'data_{i}']['date_retweet'] = d.date_retweet
    #             data[f'data_{i}']["nick2"] = d.nick
            
    #         if table == 'follow':
    #             data[f'data_{i}']["nick"] = d.follower.nick
    #             data[f'data_{i}']['nick2'] = d.followed

    #         if table == 'token':
    #             data[f'data_{i}']["nick"] = d.user_id.nick
    #             data[f'data_{i}']['token'] = d.token
            
    #         if table == 'user':
    #             data[f'data_{i}']["name"] = d.name
    #             data[f'data_{i}']['password'] = d.password
    #             data[f'data_{i}']["nick"] = d.alias
            
    #         i+=1
        
    #     if i < 10:
    #         data['over'] = True
    #     else: 
    #         data['over'] = False

    #     socket_client.send(util.encode(data))
    #     socket_client.close()

    # def data_transfer_response(self, socket_client, addr_client, data_dict, storage):        
    #     table = data_dict['table']
    #     for i in range(10):
    #         data = data_dict.get(f'date_{i}',None)
    #         if data is None: break

    #         if table == TWEET_TABLE:
    #             user = data["nick"]
    #             text = data['text']
    #             date = data["date"]
    #             view.CreateTweet(text,user,date)

    #         if table == RETWEET_TABLE:
    #             user = data["nick"]
    #             date_tweet = data['date_tweet']
    #             date_retweet = data['date_retweet']
    #             nick = data["nick2"]
    #             view.CreateReTweet(user,nick, date_tweet,date_retweet)

    #         if table == FOLLOW_TABLE:
    #             follower = data["follower"]
    #             followed = data['followed']
    #             view.CreateFollow(follower,folowed)
            
    #         if table == TOKEN_TABLE:
    #             nick = data["nick"]
    #             token = data['token']
    #             view.CreateTokenForced(nick, token)

            
    #         if table == USER_TABLE:
    #             name = data["name"]
    #             password = data['password']
    #             nick = data["nick"]
    #             view.CreateUser(name, nick, password, hashlib.sha1(bytes(nick)).hexdigest())

    #     if data_dict['over']:
    #         data = {
    #             'type': LOGGER,
    #             'proto': TRANSFERENCE_OVER,
    #             'chord_id': data_dict['chord_id'],
    #             'replication': False,
    #             'table': data_dict['table']
    #         }
    #     else:
    #         data = {
    #             'type': LOGGER,
    #             'proto': TRANSFERENCE_REQUEST,
    #             'chord_id': data_dict['chord_id'],
    #             'block':data_dict['block'],
    #             'table': data_dict['table']
    #         }
    #     socket_client.send(util.encode(data))
    #     socket_client.close()
            
    # def data_transfer_over(self, socket_client, addr_client, data_dict, storage):
    #     if not data_dict['replication']:
    #         limit  = data_dict['chord_id']
    #         table = data_dict['table']
    #         if table == 'tweet':
    #             view.DeleteTweetRange(hash_limit)
    #         if table == 'retweet':
    #             view.DeleteRetweetRange(hash_limit)
    #         if table == 'follow':
    #             view.DeleteFollowRange(hash_limit)
    #         if table == 'token':
    #             view.DeleteTokenRange(hash_limit)
    #         if table == 'user':
    #             view.DeleteUserPaswordRange(hash_limit)
        
    #     socket_client.close()

    def tweet_request(self, socket_client, addr_client, data_dict, storage): 

        socket_client.close()    
        #pedir un evento para m\'aquina de estado 
        state = storage.insert_state()

        data = {
            'type': TWEET,
            'proto': CHORD_REQUEST,
            'hash': data_dict['nick'],
            "id_request": state.id,
        }
        
        skt = socket.socket(AF_INET,SOCK_STREAM)
        skt.connect(('127.0.0.1', CHORD_PORT ))
        skt.send(util.encode(data))
        
        w = state.hold_event.wait(5)
        state = storage.get_state(state.id)
        storage.delete_state(state.id)

        if w:
            #Escribirle al server que tiene al usuario
            state2 = storage.get_state()
            data_dict['type'] = TWEET
            data_dict['id_request'] = state2.id
            
            skt = socket.socket(AF_INET,SOCK_STREAM)
            skt.connect((state.desired_data['IP'], PORT_GENERAL_LOGGER))
            skt.send(util.encode(data_dict))

            w = state2.hold_event.wait(5)
            state = storage.get_state(state2.id)
            storage.delete_state(state.id)
            
            if w:
                #reenviar mensaje de autenticacion
                try:
                    state.desired_data['id_request'] = data_dict['id_request']

                    socket_client = socket.socket(AF_INET,SOCK_STREAM)
                    socket_client.connect((addr_client[0],PORT_GENERAL_ENTRY))
                    socket_client.send(util.encode(state.desired_data))
                    socket_client.close()
                except:
                    pass

        data = {
                'type':TWEET,
                'proto': proto[0:len(proto)- 7] + 'RESPONSE',
                'succesed': False,
                'error': 'Something went wrong in the network connection',
                'id_request':  data_dict['id_request']
        }
        socket_client = socket.socket(AF_INET,SOCK_STREAM)
        socket_client.connect((addr_client[0],PORT_GENERAL_ENTRY))
        socket_client.send(util.encode(state.desired_data))
        socket_client.close()

    def create_tweet(self, socket_client, addr_client, data_dict, storage):
        try:
            if view.CheckToken(data_dict['token'], data_dict['nick']) and view.CreateTweet( data_dict['text'], data_dict['nick']): 
                data = {
                    'type': TWEET,
                    'proto': CREATE_TWEET_RESPONSE,
                    'success': True,
                    'error':None,
                    'id_request':data_dict['id_request'] 
                }
                socket_client.send(util.encode(data))
                socket_client.close()
                return
        except:
            pass 
        data = {
                    'type': TWEET,
                    'proto': CREATE_TWEET_RESPONSE,
                    'success': False,
                    'error': 'Wrong user token',
                    'id_request':data_dict['id_request'] 
                }
        socket_client.send(util.encode(data))
        socket_client.close()
    
    def create_follow(self, socket_client, addr_client, data_dict, storage):
            if view.CheckToken(data_dict['token'], data_dict['nick']):
                state = storage.insert_state()
                data = {
                        'type': TWEET,
                        'proto': CHORD_REQUEST,
                        'hash': data_dict['nick'],
                        "id_request": state.id,
                    }
                skt = socket.socket(AF_INET,SOCK_STREAM)
                skt.connect(('127.0.0.1', CHORD_PORT ))
                skt.send(util.encode(data))

                w = state.hold_event.wait(5)
                state = storage.get_state(state.id)
                storage.delete_state(state.id)

                if w:
                    #Escribirle al server que tiene al usuario
                    state2 = storage.get_state()
                    data = {
                            'type': TWEET,
                            'proto': CHECK_USER_REQUEST,
                            'nick': data_dict['nick_profile'],
                            'id_request':state2.id
                    }

                    skt = socket.socket(AF_INET,SOCK_STREAM)
                    skt.connect((state.desired_data['IP'], PORT_GENERAL_LOGGER))
                    skt.send(util.encode(data_dict))                    
                    
                    w = state2.hold_event.wait(5)
                    state = storage.get_state(state2.id)
                    storage.delete_state(state.id)

                    if w:
                        data = {
                            'type': TWEET,
                            'proto': FOLLOW_RESPONSE,
                            'success': True,
                            'error':None,
                            'id_request': data_dict['id_request'] 
                        }
                        #reenviar mensaje de autenticacion
                        if state.desire_data['exist']:
                            
                            if not view.CreateFollow(data_dict['nick'], data_dict['nick_profile']):
                                data['success'] = False
                                data['error'] = 'Error when following this user'
                        else:
                            data['success'] = False
                            data['error'] = 'Wrong user nick to follow'
                    else:
                        data['success'] = False
                        data['error'] = 'Network error'
                else:        
                    data['success'] = False
                    data['error'] = 'Network error'
            else: 
                data['success'] = False
                data['error'] = 'Wrong token error'     
            
            socket_client.send(util.encode(data))
            socket_client.close()

    def profile_get(self, socket_client, addr_client, data_dict,storage):
        if view.CheckUserAlias(data_dict['nick_profile']):
            msg = {
                'type':TWEET,
                'proto': PROFILE_RESPONSE,
                'succesed': True,
                'error': None,
                'data_profile': {},
                'id_request': data_dict['id_request']
            }
            prof = view.GetProfileRange(data_dict['nick_profile'], data_dict['block']*10, 10)
            i=0
            for t in pref[0]:
                msg['data_profile'][str(t.date)] = (t.text, None) 
                i+=1
            
            if i< 10: msg['over'] = True 
            else: msg['over'] = False

            for t in pref[1]:
                state = storage.insert_state()
                data = {
                     'type': TWEET,
                     'proto': CHORD_REQUEST,
                     'hash': t.nick,
                     "id_request": state.id,
                 }
        
                skt = socket.socket(AF_INET,SOCK_STREAM)
                skt.connect(('127.0.0.1', CHORD_PORT ))
                skt.send(util.encode(data))

                w = state.hold_event.wait(5)
                state = storage.get_state(state.id)
                storage.delete_state(state.id)

                if w:
                    #Escribirle al server que tiene al usuario
                    state2 = storage.get_state()
                    data = {
                     'type': TWEET,
                     'proto': GET_TWEET,
                     'nick': t.nick,
                     'date': t.tweet_date,
                     "id_request": state2.id,
                }
                
                skt = socket.socket(AF_INET,SOCK_STREAM)
                skt.connect((state.desired_data['IP'], PORT_GENERAL_LOGGER))
                skt.send(util.encode(data_dict))

                w = state2.hold_event.wait(5)
                state = storage.get_state(state2.id)
                storage.delete_state(state.id)
            
                if w:
                    if state.desired_dats['succcesed']:
                        data = state.desired_data['date']
                        text = state.desired_data['text']
                        nick = state.desired_data['nick']
                        msg['data_profile'][str(date)] = (text, nick)
                    
                    
                #     data['data_profile'][str(t.date_retweet)] = (t.text, t.nick) 
                #     i+=1

            
        else: 
            msg = {
                'type':TWEET,
                'proto': PROFILE_RESPONSE,
                'succesed': False,
                'error': "Wrong user name profile",
                'data_profile': {},
                'id_request': data_dict['id_request']
            }

            socket_client.send(util.encode(msg))
            socket_client.close()

    def profile_request(self, socket_client, addr_client, data_dict, storage):
        if view.CheckToken(data_dict['token'], data_dict['nick']):
                state = storage.insert_state()
                data = {
                        'type': TWEET,
                        'proto': CHORD_REQUEST,
                        'hash': data_dict['nick_profile'],
                        "id_request": state.id,
                    }
                
                skt = socket.socket(AF_INET,SOCK_STREAM)
                skt.connect(('127.0.0.1', CHORD_PORT ))
                skt.send(util.encode(data))

                w = state.hold_event.wait(5)
                state = storage.get_state(state.id)
                storage.delete_state(state.id)

                if w:
                    #Escribirle al server que tiene al usuario
                    state2 = storage.get_state()
                    data = {
                            'type': TWEET,
                            'proto': PROFILE_GET,
                            'nick': data_dict['nick_profile'],
                            "id_request": state2.id,
                    }

                    skt = socket.socket(AF_INET,SOCK_STREAM)
                    skt.connect((state.desired_data['IP'], PORT_GENERAL_LOGGER))
                    skt.send(util.encode(data_dict))                    
                    
                    w = state2.hold_event.wait(5)
                    state = storage.get_state(state2.id)
                    storage.delete_state(state.id)

                    data = state.desire_data
                    if w:
                        data['id_request'] = data_dict['id_request']
                       
                        #reenviar mensaje de autenticacion
                    else:

                        data = {
                            'type':TWEET,
                            'proto': PROFILE_RESPONSE,
                            'succesed': False,
                            'error': "Network error",
                            'id_request' : data_dict['id_request']
                        }
                else:        
                    data = {
                            'type':TWEET,
                            'proto': PROFILE_RESPONSE,
                            'succesed': False,
                            'error': "Network error",
                            'id_request': data_dict['id_request']
                        }
        else: 
                data = {
                            'type':TWEET,
                            'proto': PROFILE_RESPONSE,
                            'succesed': False,
                            'error': "Wrong token error",
                            'id_request': data_dict['id_request']
                        }    
            
        socket_client.send(util.encode(data))
        socket_client.close()  
                 
    def create_retweet(self, socket_client, addr_client, data_dict, storage):
        if view.CheckToken(data_dict['token'], data_dict['nick']):
                state = storage.insert_state()
                data = {
                        'type': TWEET,
                        'proto': CHORD_REQUEST,
                        'hash': data_dict['nick2'],
                        "id_request": state.id,
                    }
                
                skt = socket.socket(AF_INET,SOCK_STREAM)
                skt.connect(('127.0.0.1', CHORD_PORT ))
                skt.send(util.encode(data))

                w = state.hold_event.wait(5)
                state = storage.get_state(state.id)
                storage.delete_state(state.id)

                if w:
                    #Escribirle al server que tiene al usuario
                    state2 = storage.get_state()
                    data = {
                            'type': TWEET,
                            'proto': CHECK_TWEET_REQUEST,
                            'nick': data_dict['nick2'],
                            'date': data_dict['date'],
                            "id_request": state2.id,
                    }

                    skt = socket.socket(AF_INET,SOCK_STREAM)
                    skt.connect((state.desired_data['IP'], PORT_GENERAL_LOGGER))
                    skt.send(util.encode(data_dict))                    
                    
                    w = state2.hold_event.wait(5)
                    state = storage.get_state(state2.id)
                    storage.delete_state(state.id)

                    data = {
                            'type': TWEET,
                            'proto': RETWEET_RESPONSE,
                            'id_request':data_dict['id_request'],
                            'succesed': True,
                            'error':None
                    }
                   
                    if w:
                        if state.desired_data['exist']:
                            if  view.CreateReTweet(data_dict['nick'], data_dict['nick2'], data_dict['date']):
                                socket_client.send(util.encode(data))
                                socket_client.close()
                                return
                    
                    data['succesed']=False
                    data['error'] = 'Error trying to retweet'
                else:
                  data = {
                            'type': TWEET,
                            'proto': RETWEET_RESPONSE,
                            'id_request':data_dict['id_request'],
                            'succesed': False,
                            'error': 'Network error'
                    } 
        else:
            data = {
                            'type': TWEET,
                            'proto': RETWEET_RESPONSE,
                            'id_request':data_dict['id_request'],
                            'succesed': False,
                            'error': 'User is not logged in'
                    }

        socket_client.send(util.encode(data))
        socket_client.close() 

    def feed_get(self, socket_client, addr_client, data_dict,storage):
        if view.CheckToken(data_dict['token'], data_dict['nick']):
            followed = view.GetFollowed(data_dict['nick'])
            msg = {
                    'type': TWEET,
                    'proto': FEED_RESPONSE,
                    'successed': True,
                    'error': None,
                    "id_request": data_dict['id_request'],
                    'data':[]
                }
            followed = random.shufle(followed)
            
            for f in followed[:min(20, len(followed))]:
                
                state = storage.insert_state()
                data = {
                    'type': TWEET,
                    'proto': CHORD_REQUEST,
                    'hash': f.followed,
                    "id_request": state.id,
                }

                skt = socket.socket(AF_INET,SOCK_STREAM)
                skt.connect(('127.0.0.1', CHORD_PORT ))
                skt.send(util.encode(data))

                w = state.hold_event.wait(3)
                state = storage.get_state(state.id)
                storage.delete_state(state.id)

                if w:
                    #Escribirle al server que tiene al usuario
                    state2 = storage.get_state()
                    data = {
                        'type': TWEET,
                        'proto': RECENT_PUBLICHED_REQUEST,
                        'nick': f.followed,
                        "id_request": state.id,
                    }


                    skt = socket.socket(AF_INET,SOCK_STREAM)
                    skt.connect((state.desired_data['IP'], PORT_GENERAL_LOGGER))
                    skt.send(util.encode(data_dict))

                    w = state2.hold_event.wait(3)
                    state = storage.get_state(state2.id)
                    storage.delete_state(state.id)

                    if w and state.desired_data["successed"]: 
                        msg['data'].append((state.desired_data["date"], state.desired_data["text"], state.desired_data["nick"], state.desired_data.get('nick2', None), state.desired_data.get('date_tweet', None)))

            socket_client.send(util.encode(msg))
            socket_clien.close()
            return
        
        msg = {
                    'type': TWEET,
                    'proto': FEED_RESPONSE,
                    'successed': False,
                    'error': 'User not logged',
                    "id_request": data_dict['id_request'],
                    'data':[]
                }   
        socket_client.send(util.encode(msg))
        socket_clien.close()
                      
    def tweet_check(self, socket_client, addr_client, data_dict,storage):
        nick = data_dict['nick']
        date = data_dict.get['date']
        tweet = view.ChechTweet(nick, date)
        if tweet:
            data = {
                'type': TWEET,
                'proto': CHECK_TWEET_RESPONSE,
                'exist':True,
                'id_request':data_dict['id_request'],
                'text': tweet.text
            }
            socket_client.send(util.encode(data))
            socket_client.close()
            return
        
        data = {
                'type': TWEET,
                'proto': CHECK_TWEET_RESPONSE,
                'exist':False,
                'id_request':data_dict['id_request'],
                'text': None
            }
        socket_client.send(util.encode(data))
        socket_client.close()
        
    def recent_publish(self, socket_client, addr_client, data_dict,storage):
        nick = data_dict['nick']
        tweet, retweet = view.GetProfileRange(nick, 0, 100)
        tweet = random.choice(tweet)
        retweet = random.choice(retweet)
        r = random.random()
        
        if r < 0.5:
            state = storage.insert_state()
            data = {
                'type': TWEET,
                'proto': CHORD_REQUEST,
                'hash': retweet.nick,
                "id_request": state.id,
            }

            skt = socket.socket(AF_INET,SOCK_STREAM)
            skt.connect(('127.0.0.1', CHORD_PORT ))
            skt.send(util.encode(data))

            w = state.hold_event.wait(3)
            state = storage.get_state(state.id)
            storage.delete_state(state.id)

            if w:
                    #Escribirle al server que tiene al usuario
                    state2 = storage.get_state()
                    data = {
                        'type': TWEET,
                        'proto': CHECK_TWEET_REQUEST,
                        'nick': retweet.nick,
                        'date': retweet.date_tweet,
                        "id_request": state.id,
                    }


                    skt = socket.socket(AF_INET,SOCK_STREAM)
                    skt.connect((state.desired_data['IP'], PORT_GENERAL_LOGGER))
                    skt.send(util.encode(data_dict))

                    w = state2.hold_event.wait(3)
                    state = storage.get_state(state2.id)
                    storage.delete_state(state.id)

                    if w and state.desired_data["successed"]: 
                        data = {
                            'type': TWEET,
                            'proto': RECENT_PUBLICHED_RESPONSE,
                            'succesed':  True,
                            'error':None,
                            "id_request": data_dict['id_request'],
                            "date": retweet.date_retweet,
                            'text': state.desired_data["text"],
                            'nick2': retweet.nick
                        }
                        socket_client.send(util.encode(data))
                        socket_client.close()

            return
        data = {
                'type': TWEET,
                'proto': RECENT_PUBLICHED_RESPONSE,
                'succesed':  True,
                'error':None,
                "id_request": data_dict['id_request'],
                "date": tweet.date,
                'text': tweet.text,
                'nick2': None
            }
        socket_client.send(util.encode(data))
        socket_client.close()
            
    def new_logger_request(self):
        
        data = {
            'type': LOGGER,
            'proto': NEW_LOGGER_REQUEST,
            'function': NEW_NODE 
        }

        skt = socket.socket(AF_INET,SOCK_STREAM)
        skt.connect(('127.0.0.1', CHORD_PORT))
        skt.send(util.encode(data))

    def new_logger_response(self, socket_client, addr_client, data_dict,storage):
        socket_client.close()
        if self.chord_id: 
            return
        suc = data_dict.get('successor', None)
        sib = data_dict('siblings',None)
        
        self.say_hello(sib)
        self.chord_id = data_dict['chord_id']

        type_node, ips = REPLIC_NODE, self.primary if sib else NEW_NODE, suc
        
        ips = random.shufle(ips)
        data = {
            'type': LOGGER,
            'proto': TRANSFERENCE_REQUEST,
            'chord_id': self.chord_id,
            'table': USER_TABLE,
            'over': False,
            'block': 0
        }
        
        for s in ips:
            if s == self.my_if: continue
            try:
                skt = socket.socket(AF_INET,SOCK_STREAM)
                skt.connect((s, PORT_GENERAL_LOGGER))

                while True:

                    skt.send(util.encode(data))

                    recv_bytes = skt.recv(4026)
                    data_dict = util.decode(recv_bytes)
                    self.CopyData(data_dict)

                    if data_dict['over']:
                        if data_dict['table'] == FOLLOW_TABLE:
                            data = {
                                'type': LOGGER,
                                'proto': TRANSFERENCE_OVER,
                                'chord_id': self.chord_id,
                                'over': True,
                                'type_node': type_node
                            }

                            skt.send(util.encode(data))
                            skt.close()
                            return

                        data = {
                            'type': LOGGER,
                            'proto': TRANSFERENCE_REQUEST,
                            'chord_id': self.chord_id,
                            'table': data_dict['table'] + 1,
                            'over': False,
                            'block': 0 
                        }
                    else:
                        data['block'] = data['block'] + 1 
            except:
                pass

    

        # error = None        
        
        # for _ in range(0,len(self.entry_point_ips)):
        #     try:
        #         send_data = util.encode(data)
        #         s = socket.socket(AF_INET, SOCK_STREAM)
        #         ip = self.entry_point_ips[self.current_index_entry_point_ip]
        #         s.connect((ip, PORT_GENERAL_ENTRY))
        #         s.send(send_data)
        #         recv_bytes = s.recv(count_bytes_recv)
        #         recv_data = util.decode(recv_bytes)
        #         return True, recv_data
        #     except Exception as e:                
        #         print(f'Entry "{ip}" caido')
        #         self.current_index_entry_point_ip = (self.current_index_entry_point_ip+1) % len(self.entry_point_ips)
        #         error = e
        # return False, error

    def CopyData(self, data_dict):
        table = data_dict['table']
        for i in data_dict['data']:

            if table == TWEET_TABLE:
                user = data["nick"]
                text = data['text']
                date = data["date"]
                view.CreateTweet(text,user,date)

            if table == RETWEET_TABLE:
                user = data["nick"]
                date_tweet = data['date_tweet']
                date_retweet = data['date_retweet']
                nick = data["nick2"]
                view.CreateReTweet(user,nick, date_tweet,date_retweet)

            if table == FOLLOW_TABLE:
                follower = data["follower"]
                followed = data['followed']
                view.CreateFollow(follower,folowed)
            
            if table == TOKEN_TABLE:
                nick = data["nick"]
                token = data['token']
                view.CreateTokenForced(nick, token)

            
            if table == USER_TABLE:
                name = data["name"]
                password = data['password']
                nick = data["nick"]
                view.CreateUser(name, nick, password, hashlib.sha1(bytes(nick)).hexdigest())

    def data_transfer(self, socket_client, addr_client, data_dict, storage):
            """
            Peticion de transferencia de datos
            datadict['block']: Numero de bloques enviados y recibidos
            datadict['chord_id']: Nuemro a partir del cual buscar
            """            
            hash_limit = data_dict['chord_id']
            table = None

            while True:
                if data_dict['over']:
                    if data_dict['type_node']: break
                    view.DeleteTweetRange(hash_limit)            
                    view.DeleteRetweetRange(hash_limit)
                    view.DeleteFollowRange(hash_limit)
                    view.DeleteTokenRange(hash_limit)
                    view.DeleteUserPaswordRange(hash_limit)
     
                block = data_dict['block']
                data = {
                        'type': LOGGER,
                        'proto': TRANSFERENCE_RESPONSE,
                        'block': block + 1,
                        'table': data_dict['table'],
                        'data': [],
                        'over': False
                    }

                if not table == data_dict['table']:    
                    table = data_dict['table']
        
                    if table == TWEET_TABLE:
                        table_data = view.GetTweetRange(hash_limit) 
                    if table == RETWEET_TABLE:
                        table_data = view.GetRetweetRange(hash_limit) 
                    if table == FOLLOW_TABLE:
                        table_data = view.GetFollowRange(hash_limit) 
                    if table == TOKEN_TABLE:
                        table_data = view.GetTokenRange(hash_limit) 
                    if table == USER_TABLE:
                        table_data = view.GetUserPaswordRange(hash_limit)
                
                start = block* 20
                end = min(block*20 + 20, len(table_data))
                
                data['data'] = table_data[block:end]
                if end >= len(table_data): data['over'] = True
                socket_client.sendall(util.encode(data))

                recv_bytes = socket_client.recv(4026)
                data_dict = util.decode(recv_bytes)

            
            socket_client.close()


    def say_hello(self, siblings):
        self.siblings = siblings
        data = {
            'type': LOGGER,
            'proto': HELLO,
            'primary': len(siblings) < 5
        }

        for s in siblings:
            skt = socket.socket(AF_INET,PORT_GENERAL_LOGGER)
            skt.connect((s, CHORD_PORT))
            skt.send(util.encose(data))
            
            data_x = skt.recv(1024)
            data_x = util.decode(data_x)
            if self.primary == []:
                self.primary = data_x['primary']

            skt.close()

        if len(siblings) < 5:
            self.primary.append(self.my_ip)


    def say_welcome(self, socket_client, addr_client, data_dict, storage):
        
        data = {
            'type': LOGGER,
            'proto': WELCOME,
            'primary': self.primary
        }
        socket_client.send(util.encode(data))
        socket_client.close()
        
        if data_dict['primary']:
            self.primary.append(addr_client[0]) 
        self.siblings.append(addr_client[0])
        
