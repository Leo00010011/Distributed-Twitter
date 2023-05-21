import socket
from socket import AF_INET, SOCK_STREAM
from threading import Thread
try:
    import util
    from util import PORT_GENERAL
except:
    import API.util as util
    from API.util import PORT_GENERAL
class Client():

    def __init__(self):
        self.HOST_SERVER = None

    def set_ip_server(self, ip_server):
        self.HOST_SERVER = ip_server
            

    def sign_up(self, name, nick, password):
        '''
        Registrar a un usuario en la red social
        ------------------------------------
        `name`: Nombre de usuario
        `nick`: Alias de usuario
        `password`: Contrasenna
        '''


    
    def sign_in(self, alias, password):
        '''
        Iniciar sesion de usuario
        -------------
        `alias`: Nick de Usuario
        `password`: Contrasenna
        '''
       
    
    def tweet(self, text, token):
        '''
        Publicar tweet
        -------------
        `text`: Texto
        `token`: Token
        '''

    
    def retweet(self, id_tweet, token):
        '''
        Publicar tweet
        -------------
        `id_tweet`: Id del Tweet
        `token`: Token
        '''

        #TODO
        raise NotImplementedError()