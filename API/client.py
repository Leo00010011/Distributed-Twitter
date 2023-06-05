import socket
import random as rand
from socket import AF_INET, SOCK_STREAM
from threading import Thread
try:
    import util
    from util import PORT_GENERAL_ENTRY, PORT_GENERAL_LOGGER
    from util import CLIENT, ENTRY_POINT, LOGGER,LOGIN_REQUEST, LOGIN_RESPONSE,\
        NEW_LOGGER_RESPONSE, NEW_LOGGER_REQUEST, REGISTER_REQUEST, REGISTER_RESPONSE, \
        CREATE_TWEET_REQUEST, CREATE_TWEET_RESPONSE, PROFILE_REQUEST, PROFILE_RESPONSE,\
        FOLLOW_REQUEST,FOLLOW_RESPONSE, LOGOUT_REQUEST, LOGOUT_RESPONSE
except:
    import API.util as util
    from API.util import PORT_GENERAL_ENTRY, PORT_GENERAL_LOGGER
    from API.util import CLIENT, ENTRY_POINT, LOGGER,LOGIN_REQUEST, LOGIN_RESPONSE,\
        NEW_LOGGER_RESPONSE, NEW_LOGGER_REQUEST, REGISTER_REQUEST, REGISTER_RESPONSE,\
        CREATE_TWEET_REQUEST, CREATE_TWEET_RESPONSE, PROFILE_REQUEST, PROFILE_RESPONSE,\
        FOLLOW_REQUEST,FOLLOW_RESPONSE, LOGOUT_REQUEST, LOGOUT_RESPONSE
class Client():

    def __init__(self):
        self.entry_point_ips = []
        self.token = None
        self.nick = None   

        with open('entrys.txt', 'r') as ft:
            for ip in ft.read().split(sep='\n'):
                self.entry_point_ips.append(str(ip))
        self.current_index_entry_point_ip = rand.randint(0, len(self.entry_point_ips))
        

    def try_send_recv(self, message, count_bytes_recv=10240):

        error = None        
        for _ in range(0,len(self.entry_point_ips)):
            try:
                send_data = util.encode(message)
                s = socket.socket(AF_INET, SOCK_STREAM)
                ip = self.entry_point_ips[self.current_index_entry_point_ip]
                s.connect((ip, PORT_GENERAL_ENTRY))
                s.send(send_data)
                recv_bytes = s.recv(count_bytes_recv)
                recv_data = util.decode(recv_bytes)
                return True, recv_data
            except Exception as e:                
                print(f'Entry "{ip}" caido')
                self.current_index_entry_point_ip = (self.current_index_entry_point_ip+1) % len(self.entry_point_ips)
                error = e
        return False, error

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
        
        good, recv_data = self.try_send_recv(message)
        if not good:
            return False, str(recv_data)
        
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
        good, recv_data = self.try_send_recv(message)
        if not good:
            return False, str(recv_data)
        
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
    
    def logout(self, nick, token):

        message = {
            'type': CLIENT,
            'proto': LOGOUT_REQUEST,
            'nick': nick,
            'token': token,        
        }

        good, recv_data = self.try_send_recv(message)
        if not good:
            return False, str(recv_data)
        
        if recv_data['proto'] == LOGOUT_RESPONSE:
            if recv_data['succesed']:                
                return True, None
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
        
        good, recv_data = self.try_send_recv(msg)
        if not good:
            return False, str(recv_data)
        
        if recv_data['proto'] == CREATE_TWEET_RESPONSE:
            if recv_data['succesed']:                
                return True, None
            else:
                # print(recv_data['error'])
                return False, recv_data['error']
        else:
            # print('Que mierda me respondieron?')
            return False, 'Que mierda me respondieron?'

    def profile(self, nick_profile, token, nick, block):

        msg = {
            'type': CLIENT,
            'proto': PROFILE_REQUEST,
            'token': token,
            'nick': nick,
            'nick_profile': nick_profile,
            'block': block
        }
        
        good, recv_data = self.try_send_recv(msg)
        if not good:
            return False, str(recv_data)
        
        if recv_data['proto'] == PROFILE_RESPONSE:
            if recv_data['succesed']:
                return True, recv_data['data_profile'], recv_data['over']
            else:
                # print(recv_data['error'])
                return False, recv_data['error'], None
        else:
            # print('Que mierda me respondieron?')
            return False, 'Que mierda me respondieron?'
        
    def follow(self, nick_profile, token, nick):

        msg = {
            'type': CLIENT,
            'proto': PROFILE_REQUEST,
            'token': token,
            'nick': nick,
            'nick_profile': nick_profile,
        }

        good, recv_data = self.try_send_recv(msg)
        if not good:
            return False, str(recv_data)
        
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