import socket
import random as rand
from socket import AF_INET, SOCK_STREAM
from threading import Thread
try:
    import util
    from util import PORT_GENERAL_ENTRY, PORT_GENERAL_LOGGER
    from util import CLIENT, ENTRY_POINT, LOGGER,LOGIN_REQUEST, LOGIN_RESPONSE,\
        NEW_LOGGER_RESPONSE, NEW_LOGGER_REQUEST, REGISTER_REQUEST, REGISTER_RESPONSE, \
        CREATE_TWEET_REQUEST, CREATE_TWEET_RESPONSE, PROFILE_REQUEST, PROFILE_RESPONSE
except:
    import API.util as util
    from API.util import PORT_GENERAL_ENTRY, PORT_GENERAL_LOGGER
    from API.util import CLIENT, ENTRY_POINT, LOGGER,LOGIN_REQUEST, LOGIN_RESPONSE,\
        NEW_LOGGER_RESPONSE, NEW_LOGGER_REQUEST, REGISTER_REQUEST, REGISTER_RESPONSE,\
        CREATE_TWEET_REQUEST, CREATE_TWEET_RESPONSE, PROFILE_REQUEST, PROFILE_RESPONSE
class Client():

    def __init__(self):
        self.entry_point_ips = []
        self.__recent_entry_point_ip = None
        self.token = None
        self.nick = None     
        
    def recent_entry_point_ip(self):
        if self.entry_point_ips is None:
            self.__recent_entry_point_ip =rand.choice(self.entry_point_ips)            
        return self.__recent_entry_point_ip

    def sign_up(self, name, nick, password):
        '''
        Registrar a un usuario en la red social
        ------------------------------------
        `name`: Nombre de usuario
        `nick`: Alias de usuario
        `password`: Contrasenna
        '''    
        message = {
            'type': CLIENT,
            'proto': REGISTER_REQUEST,
            'name': name,
            'nick': nick,
            'password': password,        
        }
        send_data = util.encode(message)
        s = socket.socket(AF_INET, SOCK_STREAM)
        s.connect((self.recent_entry_point(), PORT_GENERAL_ENTRY))
        s.send(send_data)
        recv_bytes = s.recv(1024)
        recv_data = util.decode(recv_bytes)

        #TODO Falta agregar un try para cuando se vaya la conexion
        if recv_data['proto'] == REGISTER_RESPONSE:
            if recv_data['succesed']:
                # print('Usuario Registrado correctamente')
                return True, None
            else:
                # print(recv_data['error'])
                return False, recv_data['error']
        else:
            # print('Que mierda me respondieron?')
            return False, 'Que mierda me respondieron?'
    
    def sign_in(self, nick, password):
        '''
        Iniciar sesion de usuario
        -------------
        `alias`: Nick de Usuario
        `password`: Contrasenna
        '''
        message = {
            'type': CLIENT,
            'proto': LOGIN_REQUEST,
            'nick': nick,
            'password': password,        
        }
        send_data = util.encode(message)
        s = socket.socket(AF_INET, SOCK_STREAM)
        s.connect((self.recent_entry_point(), PORT_GENERAL_ENTRY))
        s.send(send_data)
        recv_bytes = s.recv()
        recv_data = util.decode(recv_bytes)

        #TODO Falta agregar un try para cuando se vaya la conexion
        if recv_data['proto'] == LOGIN_RESPONSE:
            if recv_data['succesed']:
                self.token = recv_data['token']
                return True, recv_data['token']
            else:
                # print(recv_data['error'])
                return False, recv_data['error']
        else:
            # print('Que mierda me respondieron?')
            return False, 'Que mierda me respondieron?'
       
    
    def tweet(self, text, token, nick):
        '''
        Publicar tweet
        -------------
        `text`: Texto
        `token`: Token
        '''
        if len(text) > 255:
            return False, 'Tweet con mas de 255 caracteres'
        msg = {
            'type': CLIENT,
            'proto': CREATE_TWEET_REQUEST,
            'token': token,
            'nick': nick,
            'text': text
        }

        #TODO Falta agregar un try para cuando se vaya la conexion
        send_data = util.encode(msg)
        s = socket.socket(AF_INET, SOCK_STREAM)
        s.connect((self.recent_entry_point(), PORT_GENERAL_ENTRY))
        s.send(send_data)
        recv_bytes = s.recv()
        recv_data = util.decode(recv_bytes)
        if recv_data['proto'] == CREATE_TWEET_RESPONSE:
            if recv_data['succesed']:                
                return True, None
            else:
                # print(recv_data['error'])
                return False, recv_data['error']
        else:
            # print('Que mierda me respondieron?')
            return False, 'Que mierda me respondieron?'

    def profile(self, nick_profile, token, nick):

        msg = {
            'type': CLIENT,
            'proto': PROFILE_REQUEST,
            'token': token,
            'nick': nick,
            'nick_profile': nick_profile
        }

        #TODO Falta agregar un try para cuando se vaya la conexion
        send_data = util.encode(msg)
        s = socket.socket(AF_INET, SOCK_STREAM)
        s.connect((self.recent_entry_point(), PORT_GENERAL_ENTRY))
        s.send(send_data)
        recv_bytes = s.recv()
        recv_data = util.decode(recv_bytes)
        if recv_data['proto'] == PROFILE_RESPONSE:
            if recv_data['succesed']:                
                return True, None
            else:
                # print(recv_data['error'])
                return False, recv_data['error']
        else:
            # print('Que mierda me respondieron?')
            return False, 'Que mierda me respondieron?'
    
    def retweet(self, id_tweet, token):
        '''
        Publicar tweet
        -------------
        `id_tweet`: Id del Tweet
        `token`: Token
        '''

        #TODO
        raise NotImplementedError()