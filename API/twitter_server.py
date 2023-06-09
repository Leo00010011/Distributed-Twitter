import socket
from socket import AF_INET, SOCK_STREAM
from threading import Thread, Event
import hashlib
import random
import datetime


try:
    from messages import *
    import util
    from server import Server
    from util import *
    import view
    from threaded_server import MultiThreadedServer
except:
    from API.messages import *
    import API.util as util
    from API.server import Server
    from API.util import *
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
    
    def __init__(self,port: int, task_max: int, thread_count: int, timout: int):

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
        self.current_index_entry_point_ip = random.randint(0, len(self.entry_point_ips))
        self.chord_id = None

    def switch(self, id:int, task: tuple[socket.socket,object], event:Event, storage):
        '''
        Interprete y verificador de peticiones generales.
        Revisa que la estructura de la peticion sea adecuada,
        e interpreta la orden dada, redirigiendo el flujo de
        ejecucion interno del Server.
        ---------------------------------------
        `data_dict['type']`: Tipo de peticion
        '''
        print("\n\n ME ESCRIBIERON UwU \n \n")
        (socket_client, addr_client) = task
        data_byte = socket_client.recv(15000)
        
        try:
            data_dict = util.decode(data_byte)
            type_rqst = data_dict["type"]       
            proto_rqst = data_dict["proto"]
        
        except Exception as e:
            print(e)
            return
        
        print('Switch del Logger')
        print(type_rqst, proto_rqst)
        print(data_dict)
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
                self.tweet_request(socket_client, addr_client, data_dict, storage)
            
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
            elif proto_rqst == PROFILE_DATA_REQUEST:
                self.profile_get(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == PROFILE_REQUEST:
                self.profile_request(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == RECENT_PUBLISHED_REQUEST:
                self.recent_publish(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == CHECK_TWEET_REQUEST:
                self.tweet_check(socket_client, addr_client, data_dict, storage)
            elif proto_rqst in (CREATE_TWEET_RESPONSE, FOLLOW_RESPONSE, RETWEET_RESPONSE, FEED_RESPONSE, PROFILE_RESPONSE, RECENT_PUBLISHED_RESPONSE, CHECK_TWEET_RESPONSE, CHECK_USER_RESPONSE):
                self.set_data(socket_client, addr_client, data_dict,storage)
            elif proto_rqst == CHECK_USER_REQUEST:
                self.nick_check(socket_client, addr_client, data_dict,storage)
        
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
        nick = data_dict['nick']
        state = do_chord_sequence(storage, nick)

        if state and state.desired_data:
            #Escribirle al server que tiene al usuario
            state2 = storage.insert_state()
            data = register_request_msg(data_dict['name'],nick, data_dict["password"], state2.id)
            send_and_close(random.choice(state.desired_data['IP']), PORT_GENERAL_LOGGER, data)
            state = wait_get_delete(storage, state2)
            
            if state.desired_data:
                #reenviar mensaje de autenticacion
                try:
                    state.desired_data['id_request'] = data_dict['id_request']
                    send_and_close(addr_client[0], PORT_GENERAL_ENTRY, state.desired_data)
                
                except:


                    pass
        data = register_response_msg(False, 'Something went wrong in the network connection', data_dict['id_request'])
        send_and_close(addr_client[0],PORT_GENERAL_ENTRY, data)
  
    def login_request(self, socket_client, addr_client, data_dict, storage):
        '''
        Solicitud de inicio de sesion de usuario
        -------------
        `data_dict['nick']`: Nick
        `data_dict['password']`: Contrasenna
        '''

        socket_client.close()
        #Hay que usar Chord para ver quien tiene a ese Nick
        nick = data_dict['nick']
        state = do_chord_sequence(storage,nick)
        print('Llego el CHORD')
        print(state.desired_data)        
        if state and state.desired_data:
            #Escribirle al server que tiene al usuario
            state2 = storage.insert_state()
            data = login_request_msg(nick, data_dict["password"], state2.id)
            send_and_close(state.desired_data['IP'][0],PORT_GENERAL_LOGGER, data)
            print('Send an Close')
            state = wait_get_delete(storage, state2)
            print('Wait', state.desired_data)
            if state and state.desired_data:
                #reenviar mensaje de autenticacion
                try:
                    state.desired_data['id_request'] = data_dict['id_request']
                    send_and_close(addr_client[0], PORT_GENERAL_ENTRY, state.desired_data)
                    return

                except:
                    pass
        print('Hubo error')
        data = login_response_msg(False, None, 'Something went wrong in the network connection', data_dict['id_request'])
        send_and_close(addr_client[0], PORT_GENERAL_ENTRY, data)

    def logout_request(self, socket_client, addr_client, data_dict, storage):
        

        socket_client.close()
        nick = data_dict['nick']
        state = do_chord_sequence(storage, nick)
        
        if state and state.desired_data:
            #Escribirle al server que tiene al usuario
            state2 = storage.insert_state()
            data = logout_request_msg(nick, data_dict["token"], state2.id)
            send_and_close(state.desired_data['IP'][0],CHORD_PORT, data)
            state = wait_get_delete(storage, state2)
            
            if state and state.desired_data:
                #reenviar mensaje de autenticacion
                try:
                    state.desired_data['id_request'] = data_dict['id_request']
                    send_and_close(addr_client[0], PORT_GENERAL_ENTRY, state.desired_data)
                    return
                except:
                    pass
        data = logout_response_msg(False, 'Something went wrong in the network connection', data_dict['id_request'])
        send_and_close(addr_client[0], PORT_GENERAL_ENTRY, data)
       
    def get_register(self, socket_client, addr_client, data_dict, storage):
        '''
        Registrar al usuario
        -------------
        `data_dict['nick']`: Nick
        `data_dict['Password']`: Password
        `data_dict['name']`: Name
        ''' 

        socket_client.close()
        nick = data_dict['nick']
        data = None
        print('get_register')
        print(data_dict)
        if view.CheckUserAlias(nick) is None:
            password = data_dict["password"]
            name = data_dict['name']
            try: 
                print('antes del view')
                code_pass = hashlib.sha256(password.encode()).hexdigest()
                code_nick = hashlib.sha256(nick.encode()).hexdigest()
                print('codificado')
                view.CreateUser(name, nick, code_pass, code_nick)
                print('view correcto')
                data = register_response_msg(True, None, data_dict['id_request'])
                print(data)
            except Exception as e:
                print(e)
                data = register_response_msg(False, 'Error trying to register', data_dict['id_request'])

        else:
            print('Fallo el check')
            data = register_response_msg(False, 'User Nick must be unique', data_dict['id_request'])

        send_and_close(addr_client[0], PORT_GENERAL_LOGGER, data) 

    def set_data(self, socket_client, addr_client, data_dict, storage):
        
        socket_client.close()
        print('Entre a set data')
        Id = data_dict["id_request"]
        state = storage.get_state(Id)
        print(data_dict)
   
        state.desired_data = data_dict
        state.hold_event.set()

    def get_token(self, socket_client, addr_client, data_dict, storage):
        '''
        Loggear al usuario
        -------------
        `data_dict['nick']`: Nick
        `data_dict['Password']`: Password
        '''
        socket_client.close() 
        data = None
        nick = data_dict["nick"]
        password = data_dict["password"]
        id_request = data_dict['id_request']
        try:
            Token = view.GetTokenLogIn(nick,hashlib.sha256(password.encode()).hexdigest())
            if Token:
                data = login_response_msg(True, Token, None, id_request)
                
            else:
                data = login_response_msg(False, None,"Invalid nick or password", id_request)    
        except:
            data = login_response_msg(False, None,"User not register", id_request)    

        send_and_close(addr_client[0], PORT_GENERAL_LOGGER, data) 

    def get_logout(self, socket_client, addr_client, data_dict, storage):
        
        nick = data_dict["nick"]
        token = data_dict["token"]
        id_request = data_dict['id_request']

        if view.CheckToken(token, nick):
            if view.RemoveToken(nick, token):
                data = logout_response_msg(True, None, id_request)
            else:
                data = logout_response_msg(False, "Error removing login", id_request)
        else:
            data = logout_response_msg(False, "Invalid user session data", id_request)

        send_and_close(addr_client[0], PORT_GENERAL_LOGGER, data)    


    def alive_request(self, socket_client, addr_client, data_dict, storage):
        data = {
            'type': LOGGER,
            'proto': ALIVE_RESPONSE,
        }
        socket_client.send(util.encode(data))
        socket_client.close()

    def tweet_request(self, socket_client, addr_client, data_dict, storage): 

        print('Tweet Request')
        socket_client.close()    
        #pedir un evento para m\'aquina de estado 
        nick = data_dict['nick']
        state = do_chord_sequence(storage, nick)
        print('Tweet Request CHORD', state)
        print('Desired', state.desired_data)
        print('IPs', state.desired_data['IP'])
        if state and state.desired_data:
            #Escribirle al server que tiene al usuario
            state2 = storage.insert_state()
            print('State2')
            data_dict['type'] = TWEET
            data_dict['id_request'] = state2.id
            print(data_dict['type'])
            send_and_close(state.desired_data['IP'][0], PORT_GENERAL_LOGGER, data_dict)
            state = wait_get_delete(storage, state2)
            
            if state and state.desired_data:
                #reenviar mensaje de autenticacion
                try:
                    state.desired_data['type'] = LOGGER
                    state.desired_data['id_request'] = data_dict['id_request']
                    print("DATA ENVIADA AL ENTRY:", state.desired_data)
                    send_and_close(addr_client[0],PORT_GENERAL_ENTRY, state.desired_data)
                    return
                except:
                    pass

        data = {
                'type':LOGGER,
                'proto': data_dict['proto'] +1,
                'succesed': False,
                'error': 'Something went wrong in the network connection',
                'id_request':  data_dict['id_request']
        }
        send_and_close(addr_client[0], PORT_GENERAL_ENTRY, data)

    
    def update_info(self, info, table):
        data_dict = {
            'type': TWEET,
            'proto': HARD_WRITE,
            'data': info,
            'table': table
        }
        
        for ip in self.primary:
            skt = socket.socket(AF_INET,SOCK_STREAM)
            skt.connect((ip, PORT_GENERAL_LOGGER))
            skt.send(util.encode(data_dict))
            skt.close() 


    def create_tweet(self, socket_client, addr_client, data_dict, storage):
        
        socket_client.close()
        id_request= data_dict['id_request']
        try:
            if view.CheckToken(data_dict['token'], data_dict['nick']):
                date = datetime.datetime.now() 
                
                if view.CreateTweet( data_dict['text'], data_dict['nick'], date): 
                    data = create_tweet_response_msg(True, None, id_request)
                    send_and_close(addr_client[0], PORT_GENERAL_LOGGER, data)
                    self.update_info([{'text':data_dict['text'], 'nick':data_dict['nick'], 'date':date}], TWEET_TABLE)

                    return
        except:
            pass
        
        data = create_tweet_response_msg(False, 'Wrong user token', id_request)
        send_and_close(addr_client[0], PORT_GENERAL_LOGGER, data)
        
    
    def create_follow(self, socket_client, addr_client, data_dict, storage):
            
            print('Entre al follow')
            socket_client.close()
            id_request= data_dict['id_request']
            data = None
            
            if view.CheckToken(data_dict['token'], data_dict['nick']):
                print('Usuario Autenticado')
                state = do_chord_sequence(storage, data_dict['nick_profile'])
                print('Llego el Chord')
                
                if state and state.desired_data:
                    #Escribirle al server que tiene al usuario
                    state2 = storage.insert_state()
                    data = check_user_profile_request_msg(data_dict['nick_profile'], state2.id)
                    print('antes del send diviti')
                    send_and_close(state.desired_data['IP'][0], PORT_GENERAL_LOGGER, data)
                    state = wait_get_delete(storage, state2)                   
                    print("DATA AFTER SEND AND WAIT",state.desired_data)
                    
                    if state and state.desired_data:
                        data = follow_response_msg(True, None, id_request)
                        #reenviar mensaje de autenticacion
                        if state.desired_data['succesed']:
                            print('SUCCESED')
                            if not view.CreateFollow(data_dict['nick'], data_dict['nick_profile']):
                                data = follow_response_msg(False, 'Error when following this user', id_request)
                                print('Data', data)
                            else: pass
                                # self.update_info([{'follower':data_dict['nick'], 'followed': data_dict['nick_profile'] }], FOLLOW_TABLE)
                        else: data = follow_response_msg(False, 'Wrong user nick to follow', id_request)
                            
                    else: data = follow_response_msg(False, 'Network error', id_request)
                        
                else: data = follow_response_msg(False, 'Network error', id_request)       
                     
            else: data = follow_response_msg(False, 'Wrong token error', id_request) 
            print("Al final", data)
            send_and_close(addr_client[0], PORT_GENERAL_LOGGER, data)       
    
    def nick_check(self, socket_client, addr_client, data_dict, storage):
        print("CHECK NICK")
        socket_client.close()
        data = None
        if view.CheckUserAlias(data_dict['nick']) is not None:
            data = check_user_profile_response_msg(True,None,data_dict['id_request'])
        else:
            data = check_user_profile_response_msg(False,"Invalid user profile to follow",data_dict['id_request'])

        print("CHECK data", data)
        send_and_close(addr_client[0], PORT_GENERAL_LOGGER, data)


    def profile_get(self, socket_client, addr_client, data_dict,storage):
        
        print("PROFILE_GET")
        socket_client.close()
        id_request = data_dict['id_request']
        data_profile = {}
        msg = None
        print(data_dict)

        if view.CheckUserAlias(data_dict['nick_profile']):   
            print("PROFILE exists")         
            tweets, retweets = view.GetProfileRange(data_dict['nick_profile'], data_dict['block']*10, 10)
            
            for tw in tweets:
                tw['date'] = str(tw['date'])
            
            for tw in retweets:
                tw['date_tweet'] = str(tw['date_tweet'])
                tw['date_retweet'] = str(tw['date_retweet'])
            print("AQUI")
            data_profile['tweets'] = tweets
            print("GOT TWEETTS")

            data_profile['retweets'] = []
            
            if retweets:
                for t in retweets:
                    print("RETWEETTS???")
                    state = do_chord_sequence(storage, t.nick)

                    if state and state.desired_data:
                        #Escribirle al server que tiene al usuario
                        state2 = storage.insert_state()
                        data = {
                        'type': TWEET,
                        'proto': GET_TWEET,
                        'nick': t.nick,
                        'date': t.tweet_date,
                        "id_request": state2.id,
                        }
                    
                        send_and_close(state.desired_data['IP'][0], PORT_GENERAL_LOGGER, data)
                        state = wait_get_delete(storage, state2)

                        if state and state.desired_data:
                            if state.desired_data['succesed']:
                                data_profile['retweets'].append(state.desired_data['data_tweet'])
            
            over = len(tweets)< 10 and len(retweets)<10 
            msg =  profile_response_msg(True, None, id_request, data_profile, over)       
        else:
            msg = profile_response_msg(False, "Wrong user name profile", id_request, {}, None)
        
        print('succesed:', msg['succesed'])
        send_and_close(addr_client[0], PORT_GENERAL_LOGGER, msg)
            

    def profile_request(self, socket_client, addr_client, data_dict, storage):
        
        print("PROFILE_REQUEST")
        socket_client.close()
        id_request = data_dict['id_request']
        nick = data_dict['nick_profile'] 
        data = None
        
        if view.CheckToken(data_dict['token'], data_dict['nick']):
                
                print('logged in user')
                state = do_chord_sequence(storage, nick)
                print('Chord hecho')
                print(state)
                print(state.desired_data.get('IP'))
                if state and state.desired_data:
                    #Escribirle al server que tiene al usuario

                    state2 = storage.insert_state()
                    data = profile_data_request_msg(data_dict['nick_profile'], state2.id, data_dict['block'])
                    print('STATE2:    ', data)
                    send_and_close(state.desired_data['IP'][0], PORT_GENERAL_LOGGER, data)
                    
                    state = wait_get_delete(storage, state2)

                    print("PROFILE_DATA:    ", state.desired_data.get)
                    if state and state.desired_data:
                        data = state.desired_data
                        data['id_request'] = data_dict['id_request']
                       
                        #reenviar mensaje de autenticacion
                    else:
                        data = profile_response_msg(False,"Network error", id_request, {}, None)
                        
                else:
                    data = profile_response_msg(False,"Network error", id_request, {},None)        
                    
        else:
            data = profile_response_msg(False,"Wrong token error", id_request, {}, None)   
        
        print(data)
        send_and_close(addr_client[0], PORT_GENERAL_LOGGER, data)   
          
                 
    def create_retweet(self, socket_client, addr_client, data_dict, storage):
        
        socket_client.close()
        id_request = data_dict['id_request']
        data = None

        if view.CheckToken(data_dict['token'], data_dict['nick']):
                
                state = do_chord_sequence(storage, data_dict['nick_profile'])
                
                if state and state.desired_data:
                    #Escribirle al server que tiene al usuario

                    state2 = storage.insert_state()
                    data = check_tweet_request_msg(data_dict['nick_profile'], data_dict['date'], state2.id)
                    send_and_close(state.desired_data['IP'][0], PORT_GENERAL_LOGGER, data)
                    state = wait_get_delete(storage, state2)
                

                    data = {
                            'type': TWEET,
                            'proto': RETWEET_RESPONSE,
                            'id_request':data_dict['id_request'],
                            'succesed': True,
                            'error':None
                    }
                   
                    if state and state.desired_data:

                        if state.desired_data['exist']:
                            if  view.CreateReTweet(data_dict['nick'], data_dict['nick2'], data_dict['date']):
                                data = retweet_response_msg(True, None, id_request)
                                send_and_close(addr_client[0], PORT_GENERAL_LOGGER, data)   
                                return
                    data = retweet_response_msg(False, 'Error trying to retweet', id_request)
                else:
                    data = retweet_response_msg(False, 'Network error', id_request)
                  
        else:
            data = retweet_response_msg(False, 'User is not logged in', id_request)
            
        send_and_close(addr_client[0], PORT_GENERAL_LOGGER, data)   

    def feed_get(self, socket_client, addr_client, data_dict,storage):
        
        socket_client.close()
        msg = None
        id_request = data_dict['id_request']
        feed_data = []

        if view.CheckToken(data_dict['token'], data_dict['nick']):
            
            followed = view.GetFollowed(data_dict['nick'])
            followed = random.shufle(followed)
            
            for f in followed[:min(20, len(followed))]:
                
                state = do_chord_sequence(storage, f.followed) 
                
                if state and state.desired_data:
                    #Escribirle al server que tiene al usuario

                    state2 = storage.insert_state()
                    data = recent_published_request_msg(f.followed, state2.id)
                    send_and_close(state.desired_data['IP'][0], PORT_GENERAL_LOGGER, data)
                    state = wait_get_delete(storage, state2)


                    if state and state.desired_data and state.desired_data["successed"]: 
                        feed_data.append((state.desired_data["date"], state.desired_data["text"], state.desired_data["nick"], state.desired_data.get('nick2', None), state.desired_data.get('date_tweet', None)))
            
            data = feed_response_msg(True, None, id_request, feed_data)
            send_and_close(addr_client[0], PORT_GENERAL_LOGGER, data)
            return
        

        data = feed_response_msg(False, 'User not logged', id_request, [])
        send_and_close(addr_client[0], PORT_GENERAL_LOGGER, data)

                      
    def tweet_check(self, socket_client, addr_client, data_dict,storage):
        
        socket_client.close()

        id_request = data_dict['id_request']
        nick = data_dict['nick']
        date = data_dict.get['date']
        tweet = view.ChechTweet(nick, date)
        
        if tweet:
            data = check_tweet_response_msg(True, id_request, tweet.text)
            
        else: 
            data = check_tweet_response_msg(False, id_request, None)
        
        send_and_close(addr_client[0], PORT_GENERAL_LOGGER, data)
        
    def recent_publish(self, socket_client, addr_client, data_dict,storage):
        
        socket_client.close()
        
        id_request = data_dict['id_request']
        nick = data_dict['nick']
        data_publish = {'tweet': {}, 'retweet': {}}
        
        tweet, retweet = view.GetProfileRange(nick, 0, 100)
        tweet = random.choice(tweet)
        retweet = random.choice(retweet)
        
        r = random.random()
        
        if r < 0.5:
            state = do_chord_sequence(storage, retweet.nick)
            state = storage.insert_state()
            
            if state and state.desired_data:
                    #Escribirle al server que tiene al usuario

                    state2 = storage.insert_state()
                    data = check_tweet_request_msg(retweet.nick, retweet.date_tweet, state2.id)
                    send_and_close(addr_client[0], PORT_GENERAL_LOGGER, data)
                    state = wait_get_delete(storage, state2)
                    

                    if state and state.desired_data and state.desired_data["successed"]: 
                        data_publish['retweet'] = {
                            "date_retweet": retweet.date_retweet,
                            'date_tweet': retweet.date_tweet,
                            'text': state.desired_data["text"],
                            'nick2': retweet.nick
                            } 
                        data = recent_published_response_msg(True, None, id_request, data_publish)
                        send_and_close(addr_client[0], PORT_GENERAL_LOGGER, data)
                        return
        
        data_publish['tweet'] = {
                            "date": tweet.date,
                            'text': tweet.text,
                            } 
        data = recent_published_response_msg(True, None, id_request, data)
        send_and_close(addr_client[0], PORT_GENERAL_LOGGER, data)
        
    def new_logger_response(self, socket_client, addr_client, data_dict,storage):
        socket_client.close()
        if self.chord_id: 
            return
        print(data_dict)
        suc = data_dict.get('succesor', None)
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

                    recv_bytes = skt.recv(15000)
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


    def CopyData(self, data_dict):
        table = data_dict['table']

        for data in data_dict['data']:
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
                view.CreateFollow(follower,followed)
            
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
        
