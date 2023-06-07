from API.twitter_server import TweeterServer
from API.chord import ChordServer
from API.util import *
from threading import Thread

class ShellTweeter():


    def __init__(self) -> None:
        self.run()

    def start(self, first):        
        t1 = Thread(target=self.start_TweeterServer)
        t2 = Thread(target=self.start_ChordServer, args= [first])
        t1.start()
        t2.start()
    
    def start_TweeterServer(self):
        self.tweet_server = TweeterServer(PORT_GENERAL_LOGGER,10,10,5)
        self.tweet_server.start_server()
    
    def start_ChordServer(self, first):
        self.chord_server = ChordServer(DHT_name='Log',port = CHORD_PORT, disable_log=False)
        self.chord_server.start()

    def options(self):          
        print('<--- Opciones --->')
        print('1. Start')
        print('<---+---==---+--->')
        
    def run(self):
        while True:
            self.options()
            option = input()
            if option == '1':
                self.begin_start()
            else:
                print('Opcion incorrecta')


    def begin_start(self):
        while True:
            print('Es el primer LOGGER? [s\\N]')
            ans = input()
            if ans == 'S' or ans == 's':
                self.start(True)
                return
            elif ans == 'N' or ans == 'n' or ans == '':
                self.start(False)
                return
            else:
                print('Respuesta incorrecta')

ShellTweeter().run()