import json
import string
import secrets

alphabet = string.ascii_letters + string.digits

# Protocolos de pedidos

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
