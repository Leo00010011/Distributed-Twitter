import API.server_entry_point as server
from threading import Thread

class ShellServerEntry():

    def __init__(self):
        self.server = server.EntryPointServerTheaded()

    def run(self):
        while True:
            print("> ",end="")
            command = input()
            
            if command == "start":
                t = Thread(target= self.server.general_listen, deamon=True)
                t.start()
            if command == 'msg':
                print('Holis')
            elif command == "exit":                
                exit()

s = ShellServer()
s.run()