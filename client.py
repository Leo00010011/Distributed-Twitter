import socket
from socket import AF_INET, SOCK_STREAM
from threading import Thread
import util
from util import PORT_GENERAL

class Client():

    def __init__(self) -> None:
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

        #TODO
        raise NotImplementedError()
    
    def sign_in(self, name, password):
        '''
        Iniciar sesion de usuario
        -------------
        `name`: Nombre de Usuario
        `password`: Contrasenna
        '''

        #TODO
        raise NotImplementedError()
    
    def tweet(self, text, token):
        '''
        Publicar tweet
        -------------
        `text`: Texto
        `token`: Token
        '''

        #TODO
        raise NotImplementedError()
    
    def retweet(self, id_tweet, token):
        '''
        Publicar tweet
        -------------
        `id_tweet`: Id del Tweet
        `token`: Token
        '''

        #TODO
        raise NotImplementedError()