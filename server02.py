import socket

class Server():

    def __init__(self, host, port) -> None:
        self.HOST = host
        self.PORT = port

        self.runing = False
        self.socket_server = None

    def run(self, number_listen=1):
        self.runing = True
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_server = s
        s.bind((self.HOST, self.PORT))
        s.listen(number_listen)
        
        while self.runing:
            (conn, addr_client) = s.accept()
            if not self.runing:
                conn.close()
                break
            data = conn.recv(1024)
            if not data:
                break
            print("Conexion establecida con:\n"+
                  f"Cliente:{addr_client[0]}\n"+
                  f"Puerto:{addr_client[1]}\n"+
                  f"Mensaje:{data.decode()}")
            conn.send(b"OK")
            conn.close()            
        s.close()
        self.runing = False

    def broadcast(self, message):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('pepe', 12344))
            s.send(bytes("Hola a todos","utf-8"))
            print("enviado")
            s.close()
        except Exception as e:
            print(e)
            s.close()


    def stop(self):
        #self.socket_server.close()
        self.runing = False
    