import API.server_entry_point as server
from threading import Thread
from API.util import PORT_GENERAL_ENTRY
import API.util as util
import time

class ShellServerEntry():

    def __init__(self):
        self.server = server.EntryPointServerTheaded(PORT_GENERAL_ENTRY, 10,10,1)
        #self.server.start_server()
        self.run()

    def run(self):
        while True:
            command = input()
            args = command.split()
            if args[0] == 'help':
                pass
            elif args[0] == 'loggers':
                if args[1] == 'ip':
                    pass
                elif args[1] == 'all':
                    pass
                else:
                    print('comando invalido')
            elif args[0] == 'clear':
                util.clear()
            elif args[0] == 'stop':
                self.server.end_event.set()
                print('Deteniendo servicio')
                time.sleep(10)
                print('Servicio detenido')
            elif args[0] == 'start':
                self.server.start()
            elif args[0] == 'exit':
                exit()
            else:
                print('comando invalido')
                

s = ShellServerEntry()