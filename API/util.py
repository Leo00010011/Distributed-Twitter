import json
import string
import secrets

alphabet = string.ascii_letters + string.digits

# Tipos de Nodos
CLIENT = 0
ENTRY_POINT = 1
LOGGER = 2
DATA_BASE = 4

# Protocolos de pedidos
LOGIN_REQUEST = 0
LOGIN_RESPONSE = 1
CHORD_REQUEST = 2
CHORD_RESPONSE = 3
NEW_LOGGER_REQUEST = 4
NEW_LOGGER_RESPONSE = 5


# Puertos de escucha
PORT_GENERAL = 8069


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

    def __init__(self) -> None:
        pass

class Gravedigger:

    def __init__(self) -> None:
        pass