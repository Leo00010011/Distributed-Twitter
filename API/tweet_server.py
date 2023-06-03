import socket
from socket import AF_INET, SOCK_STREAM
from threading import Thread, Event
import hashlib


try:
    import util
    from logger_server import LoggerServer
    from server import Server
    from util import Stalker, Dispatcher
    from util import PORT_GENERAL_ENTRY,PORT_GENERAL_LOGGER,CHORD_PORT
    from util import CHORD, CLIENT, ENTRY_POINT,CREATE_TWEET_REQUEST,CREATE_TWEET_RESPONSE,RETWEET_REQUEST,RETWEET_RESPONSE,FOLLOW_REQUEST,FOLLOW_RESPONSE,FEED_REQUEST,FEED_RESPONSE
    from util import TRANSFERENCE_REQUEST, TRANSFERENCE_RESPONSE, TRANSFERENCE_OVER, TWEET
    import view
    from threaded_server import MultiThreadedServer
except:
    from API.logger_server import LoggerServer
    import API.util as util
    from API.server import Server
    from API.util import Stalker, Dispatcher
    from API.util import PORT_GENERAL_ENTRY,PORT_GENERAL_LOGGER,CHORD_PORT
    from API.util import CHORD, CLIENT, ENTRY_POINT,CREATE_TWEET_REQUEST,CREATE_TWEET_RESPONSE,RETWEET_REQUEST,RETWEET_RESPONSE,FOLLOW_REQUEST,FOLLOW_RESPONSE,FEED_REQUEST,FEED_RESPONSE
    from API.util import TRANSFERENCE_REQUEST, TRANSFERENCE_RESPONSE,TRANSFERENCE_OVER, TWEET
    import API.view as view
    from API.threaded_server import MultiThreadedServer

class TweetServer(LoggerServer):
    
    def __init__(self,port: int, task_max: int, thread_count: int, timout: int, parse_func):

        MultiThreadedServer.__init__(self,port, task_max, thread_count, timout, TweetServer.switch)

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
            if proto_rqst in  (CREATE_TWEET_REQUEST, FOLLOW_REQUEST, RETWEET_REQUEST):
                TweetServer.tweet_request(socket_client, addr_client, data_dict, storage)
            elif proto_rqst == ALIVE_REQUEST:
                LoggerServer.alive_request(socket_client, addr_client, data_dict)

        elif type_rqst == TWEET:
            if proto_rqst == CHORD_RESPONSE:
                LoggerServer.chord_response(socket_client, addr_client, data_dict,storage)
            elif proto_rqst == CREATE_TWEET_REQUEST:
                TweetServer.create_tweet(socket_client, addr_client, data_dict)
            elif proto_rqst == RETWEET_REQUEST: 
                LoggerServer.set_token(socket_client, addr_client, data_dict,storage)
            elif proto_rqst == FOLLOW_REQUEST:
                LoggerServer.create_follow(socket_client, addr_client, data_dict,storage)
            elif proto_rqst == FEED_REQUEST:
                LoggerServer.set_register(socket_client, addr_client, data_dict, storage)
        
        elif proto_rqst == TRANSFERENCE_REQUEST:
                LoggerServer.data_transfer_request(socket_client, addr_client, data_dict)
        elif proto_rqst == TRANSFERENCE_RESPONSE:
                LoggerServer.data_transfer_response(socket_client, addr_client, data_dict)
        elif proto_rqst == TRANSFERENCE_OVER:
                LoggerServer.data_transfer_over(socket_client, addr_client, data_dict)
        else: 
            pass
        #TODO error de tipo
    
    def tweet_request(socket_client, addr_client, data_dict, storage):       
        #pedir un evento para m\'aquina de estado 
        state = storage.insert_state()

        data = {
            'type': TWEET,
            'proto': CHORD_REQUEST,
            'hash': data_dict['nick'],
            'IP': self.socket_server,
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
                'type':TWEET,
                'proto': proto[0:len(proto)- 7] + 'RESPONSE',
                'succesed': False,
                'error': 'Something went wrong in the network connection',
        }
        socket_client.send(util.encode(data))
        socket_client.close()

    def create_tweet(socket_client, addr_client, data_dict):
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
                        'IP': self.socket_server,
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
                    
                    w = state2.event_holder.wait(5)
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

    def profile_get(socket_client, addr_client, data_dict):
        if view.CheckUserAlias(data_dict['nick']):
            data = {
                'type':TWEET,
                'proto': PROFILE_RESPONSE,
                'succesed': True,
                'error': None,
                'data_profile': {},
                'ID_request': data_dict['ID_request']
            }
            prof = view.GetProfileRange(data_dict['nick'], data_dict['number']*10, 10)
            i=0
            for t in pref:
                data['data_profile'][str(t.date)] = (t.text, None) 
                i+=1
            
            if i< 10: data['over'] = True 
            else: data['over'] = False
        else: 
            data = {
                'type':TWEET,
                'proto': PROFILE_RESPONSE,
                'succesed': False,
                'error': "Wrong user name profile",
                'data_profile': {},
                'ID_request': data_dict['ID_request']
            }

            socket_client.send(util.encode(data))
            socket_client.close()

    def profile_request(socket_client, addr_client, data_dict, storage):
        if view.CheckToken(data_dict['token'], data_dict['nick']):
                state = storage.insert_state()
                data = {
                        'type': TWEET,
                        'proto': CHORD_REQUEST,
                        'hash': data_dict['nick2'],
                        'IP': self.socket_server,
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
                    
                    w = state2.event_holder.wait(5)
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
                        'IP': self.socket_server,
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
                            'proto': CHECK_TWEET,
                            'nick': data_dict['nick2'],
                            'date': data_dict['date'],
                            "ID_request": state2.id,
                    }

                    skt = socket.socket(AF_INET,SOCK_STREAM)
                    skt.connect((state.desired_data['IP'], PORT_GENERAL_LOGGER))
                    skt.send(util.encode(data_dict))                    
                    
                    w = state2.event_holder.wait(5)
                    state = storage.get_state(state2.id)
                    storage.delete_state(state.id)

                    data = state.desire_data
                    if w:
                        data['ID_request'] = data_dict['ID_request']
                       

