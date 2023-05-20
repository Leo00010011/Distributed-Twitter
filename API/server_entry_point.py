import socket
from socket import AF_INET, SOCK_STREAM
from threading import Thread

try:
    import util
    from util import CLIENT, ENTRY_POINT, LOGIN, REGISTER
    import view
except:
    import API.util as util
    from API.util import PORT_GENERAL
    import API.view as view

class EntryPointServer():

    def __init__(self) -> None:
        self.loggers = []
        
    