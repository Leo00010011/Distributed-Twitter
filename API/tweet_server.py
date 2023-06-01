import socket
from socket import AF_INET, SOCK_STREAM
from threading import Thread, Event
import hashlib


try:
    import util
    from logger_server import LoggerServer
    from server import Server
    from util import Stalker, Dispatcher
    from util import CHORD, CLIENT, ENTRY_POINT,CREATE_TWEET_REQUEST,CREATE_TWEET_RESPONSE,RETWEET_REQUEST,RETWEET_RESPONSE,FOLLOW_REQUEST,FOLLOW_RESPONSE,FEED_REQUEST,FEED_RESPONSE
    from util import TRANSFERENCE_REQUEST, TRANSFERENCE_RESPONSE, TRANSFERENCE_OVER, TWEET
    import view
    from threaded_server import MultiThreadedServer
except:
    from API.logger_server import LoggerServer
    import API.util as util
    from API.server import Server
    from API.util import Stalker, Dispatcher
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
                TweetServer.get_token(socket_client, addr_client, data_dict)
            elif proto_rqst == RETWEET_REQUEST: 
                LoggerServer.set_token(socket_client, addr_client, data_dict,storage)
            elif proto_rqst == FOLLOW_REQUEST:
                LoggerServer.get_register(socket_client, addr_client, data_dict)
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
        skt.connect(('127.0.0.1',8023))
        skt.send(util.encode(data))
        
        w = state.hold_event.wait(5)
        state = storage.get_state(state.id)
        storage.delete_state(state.id)

        if w:
            #Escribirle al server que tiene al usuario
            state2 = storage.get_state()
            proto = data_dict['proto']
            data = {
                "type": TWEET,
                "proto": proto,
                "ID_request": state2.id,
                'nick': data_dict['nick'],
                'token': data_dict['token']
            }

            if proto == CREATE_TWEET_REQUEST:
                data['text'] = data_dict['text']
            elif proto == FOLLOW_REQUEST:
                data['nick2'] = data_dict['nick2']
            elif proto == RETWEET_REQUEST:
                data['nick2'] = data_dict['nick2']
                data['tweetId'] = data_dict['tweetId']
            
            skt = socket.socket(AF_INET,SOCK_STREAM)
            skt.connect((state.desired_data['IP'],8023))
            skt.send(util.encode(data))

            w = state2.event_holder.wait(5)
            state = storage.get_state(state2.id)
            storage.delete_state(state.id)
            
            if w:
                #reenviar mensaje de autenticacion
                try:
                   data = {
                    'type':TWEET,
                    'proto': proto[0:len(proto)- 7] + 'RESPONSE',
                    'succesed': state.desired_data['succesed'],
                    'error': state.desired_data['error'],
                   }
                   socket_client.send(util.encode(data))
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
            if view.CreateTweet(data_dict['token'], data_dict['text'], data_dict['nick']): 
                
