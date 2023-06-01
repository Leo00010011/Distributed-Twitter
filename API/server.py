import socket
from socket import AF_INET, SOCK_STREAM
from threading import Thread

try:
    import util
    from util import PORT_GENERAL_ENTRY
    import view
except:
    import API.util as util
    from API.util import PORT_GENERAL_ENTRY
    import API.view as view
class Server():

    def __init__(self):
        self.HOST = "0.0.0.0"
      

    def general_listen(self, port, method_switch, listen_count=20, size_recv=1024):
        
        if self.runing:
            return
        self.runing = True
        s = socket.socket(family= AF_INET, type= SOCK_STREAM)
        self.socket_server = s
        s.bind((self.HOST, port))
        s.listen(listen_count)

        while self.runing:
            (socket_client, addr_client) = s.accept()
            data = socket_client.recv(size_recv)
            t = Thread(target=method_switch, args= [socket_client, addr_client, data], daemon=True)
            t.start()
                
        
