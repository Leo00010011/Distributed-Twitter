import json

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