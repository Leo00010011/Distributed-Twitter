import socket
from socket import AF_INET, SOCK_STREAM
from threading import Thread, Event
import hashlib


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


class TweeterServer(MultiThreadedServer):
    
    def __init__(self,port: int, task_max: int, thread_count: int, timout: int, parse_func):

        MultiThreadedServer.__init__(self,port, task_max, thread_count, timout, TweeterServer.switch)

    def switch(id:int, task: tuple[socket,object], event:Event, storage):
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
        
        if type_rqst == ENTRY_POINT:
            
            if proto_rqst == LOGIN_REQUEST:
                TweeterServer.login_request(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == LOGOUT_REQUEST:
                TweeterServer.logout_request(socket_client, addr_client, data_dict,storage)
            elif proto_rqst == REGISTER_REQUEST:
                TweeterServer.register_request(socket_client, addr_client, data_dict, storage)
            
            elif proto_rqst in  (CREATE_TWEET_REQUEST, FOLLOW_REQUEST, RETWEET_REQUEST, FEED_REQUEST, PROFILE_REQUEST):
                TweetServer.tweet_request(socket_client, addr_client, data_dict, storage)
            
            elif proto_rqst == ALIVE_REQUEST:
                TweeterServer.alive_request(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == NEW_LOGGER_RESPONSE: 
                pass #TODO 
                
      
        elif type_rqst == LOGGER:
            
            if proto_rqst == LOGIN_REQUEST:
                TweeterServer.get_token(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == LOGOUT_REQUEST:
                TweeterServer.get_logout(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == REGISTER_REQUEST:
                TweeterServer.get_register(socket_client, addr_client, data_dict, storage)
            
            elif proto_rqst in  (LOGIN_RESPONSE, REGISTER_RESPONSE, CHORD_RESPONSE, LOGOUT_RESPONSE): 
                TweeterServer.set_data(socket_client, addr_client, data_dict,storage)
            
        elif type_rqst == TWEET:
            
            if proto_rqst == CREATE_TWEET_REQUEST:
                TweetServer.create_tweet(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == FOLLOW_REQUEST:
                TweeterServer.create_follow(socket_client, addr_client, data_dict,storage)
            elif proto_rqst == RETWEET_REQUEST: 
                TweeterServer.create_retweet(socket_client, addr_client, data_dict,storage)
            elif proto_rqst == FEED_REQUEST:
                TweeterServer.feed_get(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == PROFILE_REQUEST:
                TweeterServer.profile_get(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == RECENT_PUBLISHED_REQUEST:
                TweetServer.recent_publish(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == CHECK_TWEET_REQUEST:
                TweetServer.tweet_check(socket_client, addr_client, data_dict, storage)
            elif proto_rqst in (CREATE_TWEET_RESPONSE, FOLLOW_RESPONSE, RETWEET_RESPONSE, FEED_RESPONSE, PROFILE_RESPONSE, RECENT_PUBLICHED_RESPONSE, CHECK_TWEET_RESPONSE):
                TweeterServer.set_data(socket_client, addr_client, data_dict,storage)
        
        else: 
            pass
        #TODO error de tipo
        
    def register_request(socket_client, addr_client, data_dict, storage):
        '''
        Registrar a un usuario en la red social
        ------------------------------------
        `data_dict['name']`: Nombre de usuario
        `data_dict['nick']`: Alias de usuario
        `data_dict['password']`: Contrasenna
        '''
  
        #pedir un evento para m\'aquina de estado 
        state = storage.insert_state()

        #Hay que usar Chord para ver quien tiene a ese Nick
        nick = data_dict['nick']
        data = {
                "type" : LOGGER,
                "proto": CHORD_REQUEST,
                "hash": nick,
                "ID_request": state.id,
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
                "ID_request": state2.id,
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
                    socket_client.send(util.encode(state.desired_data))
                    socket_client.close()
                except:
                    pass

        data = {
                    'type':LOGGER,
                    'proto': LOGIN_RESPONSE,
                    'succesed': False,
                    'token': None,
                    'error': 'Something went wrong in the network connection',
           }
        socket_client.send(util.encode(data))
        socket_client.close()
    
    def login_request(socket_client, addr_client, data_dict, storage):
        '''
        Solicitud de inicio de sesion de usuario
        -------------
        `data_dict['nick']`: Nick
        `data_dict['password']`: Contrasenna
        '''
        #pedir un evento para m\'aquina de estado 
        state = storage.insert_state()

        #Hay que usar Chord para ver quien tiene a ese Nick
        nick = data_dict['nick']
        data = {
                "type" : LOGGER,
                "proto": CHORD_REQUEST,
                "Hash": nick,
                "ID_request": state.id,
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
                "ID_request": state2.id,
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
                   socket_client.send(util.encode(state.desired_data))
                   socket_client.close()
                except:
                    pass

        data = {
                'type':LOGGER,
                'proto': LOGIN_RESPONSE,
                'succesed': False,
                'token': None,
                'error': 'Something went wrong in the network connection',
           }
        socket_client.send(util.encode(data))
        socket_client.close()

    def logout_request(socket_client, addr_client, data_dict, storage):
        state = storage.insert_state()

        #Hay que usar Chord para ver quien tiene a ese Nick
        nick = data_dict['nick']
        data = {
                "type" : LOGGER,
                "proto": CHORD_REQUEST,
                "Hash": nick,
                "ID_request": state.id,
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
                "password": data_dict["password"],
                "ID_request": state2.id,
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
                   socket_client.send(util.encode(state.desired_data))
                   socket_client.close()
                except:
                    pass

        data = {
                'type':LOGGER,
                'proto': LOGOUT_RESPONSE,
                'succesed': False,
                'token': None,
                'error': 'Something went wrong in the network connection',
           }
        socket_client.send(util.encode(data))
        socket_client.close()

    def get_register(socket_client, addr_client, data_dict, storage):
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
                    'ID_request': data_dict['ID_request']
                }
            except:
                data = {
                    'type': LOGGER,
                    'proto': REQUEST_RESPONSE,
                    'succesed': False,
                    'error': 'Error trying to register',
                    'ID_request': data_dict['ID_request']
                }
        else:
            data = {
                    'type': LOGGER,
                    'proto': REQUEST_RESPONSE,
                    'succesed': False,
                    'error': 'User Nick must be unique',
                    'ID_request': data_dict['ID_request']
                }
        
        socket_client.send(util.encode(data))
        socket_client.close()  

    def set_data(socket_client, addr_client, data_dict, storage):
        Id = data_dict["ID_request"]
        state = storage.get_state(Id)
   
        state.desired_data = data_dict
        state.hold_event.set()
        socket_client.close()

    def get_token(socket_client, addr_client, data_dict, storage):
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
                    'ID_request': data_dict['ID_request']
                }
            else:
                data={
                    'type': LOGGER,
                    'proto': LOGIN_RESPONSE,
                    'succesed': False,
                    'token': None,
                    'error': "Invalid nick or password",
                    'ID_request': data_dict['ID_request']
                }     
        except:
                data={
                    'type': LOGGER,
                    'proto': LOGIN_RESPONSE,
                    'succesed': False,
                    'token': None,
                    'error': "User not register",
                    'ID_request': data_dict['ID_request']
                }
        
        socket_client.send(util.encode(data))
        socket_client.close()

    def get_logout(socket_client, addr_client, data_dict, storage):
        nick = data_dict["nick"]
        token = data_dict["token"]
        if view.CheckToken(token, nick):
            if view.RemoveToken(nick, token):
                data ={
                    'type':LOGGER,
                    'proto': LOGOUT_REQUEST,
                    'succesed': True,
                    'error': None
                }
            else:
                data ={
                    'type':LOGGER,
                    'proto': LOGOUT_REQUEST,
                    'succesed': False,
                    'error': "Error removing login"
                }
        else:
            data = {
                    'type':LOGGER,
                    'proto': LOGOUT_REQUEST,
                    'succesed': False,
                    'error': "Invalid user session data"
                }
        
        socket_client.send(util.encode(data))
        socket_client.close()

    def alive_request(socket_client, addr_client, data_dict, storage):
        data = {
            'type': LOGGER,
            'proto': ALIVE_RESPONSE,
        }
        socket_client.send(util.encode(data))
        socket_client.close()

    def data_transfer_request(socket_client, addr_client, data_dict, storage):
        """
        Peticion de transferencia de datos
        datadict['number']: Numero de bloques enviados y recibidos
        datadict['chord_id']: Nuemro a partir del cual buscar
        """

        number = data_dict['number']
        hash_limit = data_dict['chord_id']
        table = data_dict['table']

        data = {
            'type': LOGGER,
            'proto': TRANSFERENCE_RESPONSE,
            'number': number + 1,
            'chord_id': hash_limit,
            'table': table
        }

        if table == 'tweet':
            table_data = view.GetTweetRange(hash_limit, (number +1)*10,10) 
        if table == 'retweet':
            table_data = view.GetRetweetRange(hash_limit, (number +1)*10,10) 
        if table == 'follow':
            table_data = view.GetFollowRange(hash_limit, (number +1)*10,10) 
        if table == 'token':
            table_data = view.GetTokenRange(hash_limit, (number +1)*10,10) 
        if table == 'user':
            table_data = view.GetUserPaswordRange(hash_limit, (number+1) * 10,10)
        
        i = 0
        for d in table_data:
            data[f'data_{i}'] = {}
            if table == 'tweet':
                data[f'data_{i}']["nick"] = d.user.nick
                data[f'data_{i}']['text'] = d.text
                data[f'data_{i}']["date"] = d.date
            
            if table == 'retweet':
                data[f'data_{i}']["nick"] = d.user.nick
                data[f'data_{i}']['date_tweet'] = d.date_tweet
                data[f'data_{i}']['date_retweet'] = d.date_retweet
                data[f'data_{i}']["nick2"] = d.nick
            
            if table == 'follow':
                data[f'data_{i}']["nick"] = d.follower.nick
                data[f'data_{i}']['nick2'] = d.followed

            if table == 'token':
                data[f'data_{i}']["nick"] = d.user_id.nick
                data[f'data_{i}']['token'] = d.token
            
            if table == 'user':
                data[f'data_{i}']["name"] = d.name
                data[f'data_{i}']['password'] = d.password
                data[f'data_{i}']["nick"] = d.alias
            
            i+=1
        
        if i < 10:
            data['over'] = True
        else: 
            data['over'] = False

        socket_client.send(util.encode(data))
        socket_client.close()

    def data_transfer_response(socket_client, addr_client, data_dict, storage):        
        table = data_dict['table']
        for i in range(10):
            data = data_dict.get(f'date_{i}',None)
            if data is None: break

            if table == 'tweet':
                user = data["nick"]
                text = data['text']
                date = data["date"]
                view.CreateTweet(text,user,)

            if table == 'retweet':
                user = data["nick"]
                date_tweet = data['date_tweet']
                date_retweet = data['date_retweet']
                nick = data["nick2"]
                view.CreateReTweet(user,nick, date_tweet,date_retweet)

            if table == 'follow':
                follower = data["nick"]
                followed = data['nick2']
                view.CreateFollow(follower,folowed)
            
            if table == 'token':
                nick = data["nick"]
                token = data['token']
                view.CreateTokenForced(nick, token)

            
            if table == 'user':
                name = data["name"]
                password = data['password']
                nick = data["nick"]
                view.CreateUser(name, nick, password, hashlib.sha1(bytes(nick)).hexdigest())

        if data_dict['over']:
            data = {
                'type': LOGGER,
                'proto': TRANSFERENCE_OVER,
                'chord_id': data_dict['chord_id'],
                'replication': False,
                'table': data_dict['table']
            }
        else:
            data = {
                'type': LOGGER,
                'proto': TRANSFERENCE_REQUEST,
                'chord_id': data_dict['chord_id'],
                'number':data_dict['number'],
                'table': data_dict['table']
            }
        socket_client.send(util.encode(data))
        socket_client.close()
            
    def data_transfer_over(socket_client, addr_client, data_dict, storage):
        if not data_dict['replication']:
            limit  = data_dict['chord_id']
            table = data_dict['table']
            if table == 'tweet':
                view.DeleteTweetRange(hash_limit)
            if table == 'retweet':
                view.DeleteRetweetRange(hash_limit)
            if table == 'follow':
                view.DeleteFollowRange(hash_limit)
            if table == 'token':
                view.DeleteTokenRange(hash_limit)
            if table == 'user':
                view.DeleteUserPaswordRange(hash_limit)
        
        socket_client.close()

    def tweet_request(socket_client, addr_client, data_dict, storage):       
        #pedir un evento para m\'aquina de estado 
        state = storage.insert_state()

        data = {
            'type': TWEET,
            'proto': CHORD_REQUEST,
            'hash': data_dict['nick'],
            "ID_request": state.id,
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
            
            skt = socket.socket(AF_INET,SOCK_STREAM)
            skt.connect((state.desired_data['IP'], PORT_GENERAL_LOGGER))
            skt.send(util.encode(data_dict))

            w = state2.hold_event.wait(5)
            state = storage.get_state(state2.id)
            storage.delete_state(state.id)
            
            if w:
                #reenviar mensaje de autenticacion
                try:

                   socket_client.send(util.encode(state.desired_data))
                   socket_client.close()
                except:
                    pass

        data = {
                'type':TWEET,
                'proto': proto[0:len(proto)- 7] + 'RESPONSE',
                'succesed': False,
                'error': 'Something went wrong in the network connection',
        }
        socket_client.send(util.encode(data))
        socket_client.close()

    def create_tweet(socket_client, addr_client, data_dict, storage):
        try:
            if view.CheckToken(data_dict['token'], data_dict['nick']) and view.CreateTweet( data_dict['text'], data_dict['nick']): 
                data = {
                    'type': TWEET,
                    'proto': CREATE_TWEET_RESPONSE,
                    'success': True,
                    'error':None 
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
                    'error': 'Wrong user token' 
                }
        socket_client.send(util.encode(data))
        socket_client.close()
    
    def create_follow(socket_client, addr_client, data_dict, storage):
            if view.CheckToken(data_dict['token'], data_dict['nick']):
                state = storage.insert_state()
                data = {
                        'type': TWEET,
                        'proto': CHORD_REQUEST,
                        'hash': data_dict['nick'],
                        "ID_request": state.id,
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
                            'nick': data_dict['nick2'] 
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
                            'ID_request': data_dict['ID_request'] 
                        }
                        #reenviar mensaje de autenticacion
                        if state.desire_data['exist']:
                            
                            if not view.CreateFollow(data_dict['nick'], data_dict['nick1']):
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

    def profile_get(socket_client, addr_client, data_dict,storage):
        if view.CheckUserAlias(data_dict['nick']):
            msg = {
                'type':TWEET,
                'proto': PROFILE_RESPONSE,
                'succesed': True,
                'error': None,
                'data_profile': {},
                'ID_request': data_dict['ID_request']
            }
            prof = view.GetProfileRange(data_dict['nick'], data_dict['number']*10, 10)
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
                     "ID_request": state.id,
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
                     "ID_request": state.id,
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
                'ID_request': data_dict['ID_request']
            }

            socket_client.send(util.encode(msg))
            socket_client.close()

    def profile_request(socket_client, addr_client, data_dict, storage):
        if view.CheckToken(data_dict['token'], data_dict['nick']):
                state = storage.insert_state()
                data = {
                        'type': TWEET,
                        'proto': CHORD_REQUEST,
                        'hash': data_dict['nick2'],
                        "ID_request": state.id,
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
                            'nick': data_dict['nick2'],
                            "ID_request": state2.id,
                    }

                    skt = socket.socket(AF_INET,SOCK_STREAM)
                    skt.connect((state.desired_data['IP'], PORT_GENERAL_LOGGER))
                    skt.send(util.encode(data_dict))                    
                    
                    w = state2.hold_event.wait(5)
                    state = storage.get_state(state2.id)
                    storage.delete_state(state.id)

                    data = state.desire_data
                    if w:
                        data['ID_request'] = data_dict['ID_request']
                       
                        #reenviar mensaje de autenticacion
                    else:

                        data = {
                            'type':TWEET,
                            'proto': PROFILE_RESPONSE,
                            'succesed': False,
                            'error': "Network error",
                            'ID_request' : data_dict['ID_request']
                        }
                else:        
                    data = {
                            'type':TWEET,
                            'proto': PROFILE_RESPONSE,
                            'succesed': False,
                            'error': "Network error",
                            'ID_request': data_dict['ID_request']
                        }
        else: 
                data = {
                            'type':TWEET,
                            'proto': PROFILE_RESPONSE,
                            'succesed': False,
                            'error': "Wrong token error",
                            'ID_request': data_dict['ID_request']
                        }    
            
        socket_client.send(util.encode(data))
        socket_client.close()  
                 
    def create_retweet(socket_client, addr_client, data_dict, storage):
        if view.CheckToken(data_dict['token'], data_dict['nick']):
                state = storage.insert_state()
                data = {
                        'type': TWEET,
                        'proto': CHORD_REQUEST,
                        'hash': data_dict['nick2'],
                        "ID_request": state.id,
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
                            "ID_request": state2.id,
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
                            "ID_request": state2.id,
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
                            "ID_request": state2.id,
                            'succesed': False,
                            'error': 'Network error'
                    } 
        else:
            data = {
                            'type': TWEET,
                            'proto': RETWEET_RESPONSE,
                            "ID_request": state2.id,
                            'succesed': False,
                            'error': 'User is not logged in'
                    }

        socket_client.send(util.encode(data))
        socket_client.close() 

    def feed_get(socket_client, addr_client, data_dict,storage):
        if view.CheckToken(data_dict['token'], data_dict['nick']):
            followed = view.GetFollowed(data_dict['nick'])
            msg = {
                    'type': TWEET,
                    'proto': FEED_RESPONSE,
                    'successed': True,
                    'error': None,
                    "ID_request": data_dict['ID_request'],
                    'data':{}
                }
            #TODO pedir de alguna forma un subconjunto de tamanno 20 random
            for f in followed:
                state = storage.insert_state()
                data = {
                    'type': TWEET,
                    'proto': CHORD_REQUEST,
                    'hash': f.followed,
                    "ID_request": state.id,
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
                        "ID_request": state.id,
                    }


                    skt = socket.socket(AF_INET,SOCK_STREAM)
                    skt.connect((state.desired_data['IP'], PORT_GENERAL_LOGGER))
                    skt.send(util.encode(data_dict))

                    w = state2.hold_event.wait(3)
                    state = storage.get_state(state2.id)
                    storage.delete_state(state.id)

                    if w and state.desired_data["successed"]: 
                        date =state.desired_data["date"]
                        msg['data'][f'{date}'] = (state.desired_data["text"], state.desired_data.get('nick2', None))

            socket_client.send(util.encode(msg))
            socket_clien.close()
            return
        
        msg = {
                    'type': TWEET,
                    'proto': FEED_RESPONSE,
                    'successed': False,
                    'error': 'User not logged',
                    "ID_request": data_dict['ID_request'],
                    'data':{}
                }   
        socket_client.send(util.encode(msg))
        socket_clien.close()
                      
    def tweet_check(socket_client, addr_client, data_dict,storage):
        nick = data_dict['nick']
        date = data_dict.get['date']

        if view.ChechTweet(nick, date):
            data = {
                'type': TWEET,
                'proto': CHECK_TWEET_RESPONSE,
                'exist':True,
                'ID_request':data_dict['ID_request']
            }
            socket_client.send(util.encode(data))
            socket_client.close()
            return
        
        data = {
                'type': TWEET,
                'proto': CHECK_TWEET_RESPONSE,
                'exist':False,
                'ID_request':data_dict['ID_request']
            }
        socket_client.send(util.encode(data))
        socket_client.close()
        
    def recent_publish(socket_client, addr_client, data_dict,storage):
        nick = data_dict['nick']
        tweet, retweet = view.GetProfileRange(nick, 0, 100)
        #TODO seleccionar un tweet o u retweet random para feed, en caso de
        #TODO retweet haer chord y pedir el texto del retweet

    