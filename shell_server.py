import API.server
from threading import Thread

class ShellServer():

    def __init__(self):
        self.server = API.server.Server()

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