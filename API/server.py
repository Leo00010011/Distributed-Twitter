import socket
from socket import AF_INET, SOCK_STREAM
from threading import Thread

try:
    import util
    from util import PORT_GENERAL
    import view
except:
    import API.util as util
    from API.util import PORT_GENERAL
    import API.view as view
class Server():

    def __init__(self):
        self.HOST = "0.0.0.0"
        self.PORT = PORT_GENERAL
        self.socket_server = None

        self.runing = False        
        
        self.list_clients_pasive_listen  = {}

    def general_listen(self):
        if self.runing:
            return
        self.runing = True
        s = socket.socket(family= AF_INET, type= SOCK_STREAM)
        self.socket_server = s
        s.bind((self.HOST, self.PORT))
        s.listen(1) #TODO Considerar en cambiar este numero

        while self.runing:
            (socket_client, addr_client) = s.accept()
            data = socket_client.recv(1024)
            t = Thread(target=self.switch_no_sign, args= [socket_client, addr_client, data])
            t.start()
            

    def switch_no_sign(self, socket_client, addr_client, data_bytes):
        '''
        Interprete y verificador de peticiones generales.
        Revisa que la estructura de la peticion sea adecuada,
        e interpreta la orden dada, redirigiendo el flujo de
        ejecucion interno del Server.
        ---------------------------------------
        `data_bytes['type']`: Tipo de peticion
        '''
        try:
            data_dict = util.decode(data_bytes)        
            type_rqst = data_dict["type"]
        except Exception as e:
            print(e)
            return
        
        #TODO
        # Implementar la seleccion de que accion realizar
        raise NotImplementedError()
        

    def sign_up(self, socket_client, addr_client, data_dict):
        '''
        Registrar a un usuario en la red social
        ------------------------------------
        `data_dict['name']`: Nombre de usuario
        `data_dict['nick']`: Alias de usuario
        `data_dict['password']`: Contrasenna
        '''
        name = data_dict['name']
        nick = data_dict['nick']
        password = data_dict['password']

        if view.CreateUser(name= name, alias=nick, password= password):
            return True
        else:
            #Algun tipo de error de alias ya existente
            pass
    
    def sign_in(self, socket_client, addr_client, data_dict):
        '''
        Iniciar sesion de usuario
        -------------
        `data_dict['name']`:
        `data_dict['password']`: Contrasenna
        '''
        name = data_dict['name']
        password = data_dict['password']
        
        user = view.GetUserName(name)
        if user and user.password == password:
            view.CreateToken(user.id)

    
    def tweet(self, socket_client, addr_client, data_dict):
        '''
        Publicar tweet
        -------------
        `data_dict['text']`: Texto
        `data_dict['token']`: Token
        '''

        text = data_dict['text']
        token = data_dict['token']

        if len(text) >= 255:
            # Aqui mandar algun error de exceso de contenido 
            return
        if view.CreateTweet(token = token, text = text):
            pass
            #Enviar confirmacion de post realizado
        else:
            pass
            #Enviar error al publicar 
    
    def retweet(self, socket_client, addr_client, data_dict):
        '''
        Publicar tweet
        -------------
        `data_dict['id_tweet']`: Id del Tweet
        `data_dict['token']`: Token
        '''

        user_id = data_dict['id_tweet']
        token = data_dict['token']
        
        if view.CreateReTweet(user = user_id, tweet=tweet_id):
            #Aqui devolver algo plan  
            return 
        else:
            pass
            #Aqui devolver mensaje de error al retwitear
