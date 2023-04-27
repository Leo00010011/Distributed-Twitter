import client02
import threading
from threading import Thread

class ShellClient():

    def __init__(self) -> None:
        self.client = None
        self.run()

    def run(self):
        while True:
            print("> ",end="")
            command = input()    
            args = command.split()

            if args[0] == "start":        
                self.start(args)
            elif args[0] == "msg":
                self.msg(args)
            elif args[0] == "exit":                        
                exit()

    def start(self, args):
        if self.client is not None:
            self.client = None            
            print(f"Comunicacion con server {self.client.HOST}:{self.client.PORT} finalizada")
        try:
            host = args[1]
            port = int(args[2])
            self.client = client02.Client(host, port)            
            print(f"> Comunicacion con server {self.client.HOST}:{self.client.PORT} establecida")
            t = Thread(target=self.client.pasive)
            t.start()
        except Exception as e:
            print(e)
            self.client = None

    def msg(self, args):
        try:
            if len(args) == 1 or args[1] == "server": # Mensaje directo al server
                print("> Enviar mensaje al server:")
                print("> ", end="")
                message = input()
                self.client.msg_server(message)
            else:
                print("> Comando incorrecto")
        except Exception as e:
            print(e)

shell = ShellClient()
