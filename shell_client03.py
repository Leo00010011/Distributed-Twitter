import client03
import threading
from threading import Thread

class ShellClient():

    def __init__(self) -> None:
        self.client = client03.Client()
        self.run()

    def run(self):
        while True:
            print("> ",end="")
            command = input()    
            args = command.split()

            if args[0] == "start":        
                self.client.conn_server("127.0.0.1")
            elif args[0] == "msg":
                self.msg(args)
            elif args[0] == "sub":
                self.client.client_pasive_listen_subscribe()
            elif args[0] == "unsub":
                self.client.client_pasive_listen_unsubscribe()
            elif args[0] == "exit":                        
                exit()

    def msg(self, args):
        try:
            if len(args) == 1 or args[1] == "server": # Mensaje directo al server
                print("> Enviar mensaje al server:")
                print("> ", end="")
                message = input()
                self.client.msg_to_server(message)
            else:
                print("> Comando incorrecto")
        except Exception as e:
            print(e)

ShellClient()