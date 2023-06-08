try:
    from util import *
    import util
except:
    from API.util import *
    import API.util as util

import socket
from socket import AF_INET, SOCK_STREAM

def send_and_close(ip, port, data):
    print('send and close')
    print(ip, port, data)
    skt = socket.socket(AF_INET,SOCK_STREAM)
    print('socket')
    skt.connect((ip,port))
    print('connect')
    skt.send(util.encode(data))
    print('send')
    skt.close()
    print('close')

def only_send(ip, port, data):
    skt = socket.socket(AF_INET,SOCK_STREAM)
    skt.connect((ip,port))
    skt.send(util.encode(data))
    return skt

def wait_get_delete(storage, state):
    state.hold_event.wait(5)
    state = storage.get_state(state.id)
    storage.delete_state(state.id)

    return state

def do_chord_sequence(storage, nick):
        state = storage.insert_state()
        #Hay que usar Chord para ver quien tiene a ese Nick
        data = chord_request_msg(nick, state.id) #Construir la peticion del chord
        send_and_close('127.0.0.1', CHORD_PORT, data)
        return wait_get_delete(storage, state) 

def login_request_msg(nick,password,id_request):
    data = {
            "type": LOGGER,
            "proto": LOGIN_REQUEST,
            "nick": nick,
            "password": password,
            "id_request": id_request,
        }
    return data

def login_response_msg(succesed, token,error,id_request):
    data = {
            'type':LOGGER,
            'proto': LOGIN_RESPONSE,
            'succesed':succesed, 
            'token':token, 
            'error':error, 
            'id_request':id_request
           }
    return data

def chord_request_msg(nick, id_request):
    data = {
            "type" : LOGGER,
            "proto": CHORD_REQUEST,
            "hash": nick,
            "id_request": id_request,
        }
    return data

def register_request_msg(nick, password, id_request):
    data = {
                "type": LOGGER,
                "proto": REGISTER_REQUEST,
                "nick":nick ,
                "password":password ,
                "id_request":id_request ,
            }
    return data

def register_response_msg(succesed, error, id_request):
    data = {
            'type':LOGGER,
            'proto': REGISTER_RESPONSE,
            'succesed':succesed,
            'error':error,
            'id_request':id_request 
           }
    return data

def create_tweet_response_msg(success, error, id_request):
    data = {
            'type': TWEET,
            'proto': CREATE_TWEET_RESPONSE,
            'success':success ,
            'error':error,
            'id_request':id_request 
        }
    return data

def retweet_response_msg(success, error, id_request):
    data = {
            'type': TWEET,
            'proto': RETWEET_RESPONSE,
            'success':success ,
            'error':error,
            'id_request':id_request 
        }
    return data

def follow_response_msg(success, error, id_request):
    data = {
            'type': TWEET,
            'proto': FOLLOW_RESPONSE,
            'success':success ,
            'error':error,
            'id_request':id_request 
        }
    return data

def feed_response_msg(successed, error, id_request, data):
    msg = {
            'type': TWEET,
            'proto': FEED_RESPONSE,
            'successed':successed ,
            'error':error ,
            "id_request":id_request ,
            'data':data
        }
    return msg

def profile_response_msg(success, error, id_request, data_profile):
    data = {
            'type': TWEET,
            'proto': PROFILE_RESPONSE,
            'success':success ,
            'error':error,
            'data_profile': data_profile,
            'id_request':id_request 
        }
    return data

def logout_request_msg(nick,token,id_request):
    data = {
            "type": LOGGER,
            "proto": LOGOUT_REQUEST,
            "nick": nick,
            "token": token,
            "id_request": id_request,
        }
    return data

def logout_response_msg(success, error, id_request):
    data = {
            'type':LOGGER,
            'proto': LOGOUT_RESPONSE,
            'success':success ,
            'error':error,
            'id_request':id_request 
        }
    return data

def recent_published_request_msg(nick, id_request):
    
    data = {
        'type': TWEET,
        'proto': RECENT_PUBLISHED_REQUEST,
        'nick': nick,
        "id_request": id_request,
    }

    return data

def recent_published_response_msg(successed, error, id_request, data):
    msg = {
            'type': TWEET,
            'proto': RECENT_PUBLISHED_RESPONSE,
            'successed':successed,
            'error':error,
            "id_request":id_request,
            'data':data
        }
    return msg

def check_tweet_request(nick, date, id_request):
    data = {
            'type': TWEET,
            'proto': CHECK_TWEET_REQUEST,
            'nick': nick,
            'date': date,
            "id_request": id_request,
    }
    return data

def check_tweet_request(exist, id_request, text):  
    data = {
                'type': TWEET,
                'proto': CHECK_TWEET_RESPONSE,
                'exist':exist,
                'id_request':id_request,
                'text':text 
            }
    return data