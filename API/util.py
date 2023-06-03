import json
import string
import secrets
import time
import heapq
import random
import os

alphabet = string.ascii_letters + string.digits

# Tipos de Nodos
CLIENT = 0
ENTRY_POINT = 1
LOGGER = 2

# Protocolos de pedidos
LOGIN_REQUEST = 0
LOGIN_RESPONSE = 1
CHORD_REQUEST = 2
CHORD_RESPONSE = 3
NEW_LOGGER_REQUEST = 4
NEW_LOGGER_RESPONSE = 5
ALIVE_REQUEST = 6
ALIVE_RESPONSE = 7
REGISTER_REQUEST = 8 
REGISTER_RESPONSE = 9
TRANSFERENCE_REQUEST = 10
TRANSFERENCE_RESPONSE = 11
TRANSFERENCE_OVER = 12
CREATE_TWEET_REQUEST = 13
CREATE_TWEET_RESPONSE = 14
RETWEET_REQUEST=15
RETWEET_RESPONSE =16
FOLLOW_REQUEST = 17
FOLLOW_RESPONSE = 18
FEED_REQUEST = 19
FEED_RESPONSE = 20
PROFILE_REQUEST =21
PROFILE_RESPONSE = 22
NEW_ENTRYPOINT_REQUEST = 23
NEW_ENTRYPOINT_RESPONSE = 24
LOGOUT_REQUEST = 25
LOGOUT_RESPONSE = 26

# Puertos de escucha
PORT_GENERAL_ENTRY = 15069
CHORD_PORT = 15042
PORT_GENERAL_LOGGER = 15071

def encode(data_dict):
    '''
    Codifica un diccionario de Python a bytes
    '''
    return json.dumps(data_dict).encode()

def decode(data_bytes):
    '''
    Decodifica bytes para interpretarlo como diccionario de Python
    '''
    return json.loads(data_bytes)

def gen_token(n_bytes):
    return ''.join(secrets.choice(alphabet) for i in range(n_bytes))


class Dispatcher:

    def __init__(self):
        self.__next_petition_id = 0
        self.petitions = {}
        self.slaves = None

    def insert_petition(self, petition):
        ret = self.__next_petition_id
        self.petitions[ret] = petition
        self.__next_petition_id += 1
        return ret

    def extract_petition(self, id):
        return self.petitions.get(id, None)


class Stalker:
    '''
    Estructura que guarda una lista de IP:Puertos (o Puertos),
    con la ultima hora de actividad. Recomienda de forma aleatoria un IP
    para verificar si est'a vivo a'un, pero dando mas probabilidad a los
    IP menos actualizados.
    '''
    def __init__(self, type):
        '''
        Inicializa la estructura Stalker con el tipo de Server que la aloje.
        Internamente utiliza una lista con tuplas de la forma (tiempo, IP:Port)
        '''
        self.list = []
        self.type = type

    def insert_IP(self, dir):
        '''
        Agrega una nueva direcci'on IP a la lista. La presupone nueva.
        Utilizar mejor update cuando no se tiene la certeza de su existencia.        
        '''
        self.list.append((time.time(), dir))

    def update_IP(self, dir):
        '''
        Actualiza el tiempo de un IP. Si este est'a solamente se actualiza el tiempo
        con el tiempo actual. Si no est'a, se a~nade nuevo.
        '''
        for i, item in enumerate(self.list):
            if item[1] == dir:
                self.list[i] = (time.time(), dir)
                self.list.sort()
                return
        self.list.append(time.time(), dir)      

    def extract_IP(self, dir):
        '''
        Se elimina el IP de la lista y se retorna su valor. Si este no existe
        se retorna None
        '''
        for i, item in enumerate(self.list):
            if item[1] == dir:
                return self.list.pop(i)
        return None
    
    def recommended_dir(self):
        '''
        Se recomienda alg'un IP de la lista. Mientras m'as viejo, m'as probable
        eres de ser recomendado.
        '''
        _, dir = random.choices(self.list,weights=range(len(self.list), 0, -1),k=1)[0]
        return dir
    
    def dieds_dirs(self, umbral_time):

        real_time = time.time()
        dieds = []
        for i in len(self.list):
            t, dir = self.list[i]
            if real_time - t >= umbral_time:
                dieds.append(dir)
        return dieds

    def msg_stalk(self):
        '''
        Genera el mensaje de ALIVE_REQUEST
        '''
        msg = {
            'type': self.type,
            'proto': ALIVE_REQUEST, # Definir el protocolo de estar vivo.
        }
        return msg


def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")