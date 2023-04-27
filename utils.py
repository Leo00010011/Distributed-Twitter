import json

# Protocolos de pedidos
MSG_TO_SERVER = 0
CLIENT_PASIVE_LISTEN_SUBSCRIBE = 1
CLIENT_PASIVE_LISTEN_UNSUBSCRIBE = 2

PORT_GENERAL = 8069

def encode(data_dict):
    return json.dumps(data_dict).encode()

def decode(data_bytes):
    return json.loads(data_bytes)