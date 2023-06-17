from API.twitter_server import TweeterServer
from API.chord import ChordServer
from API.util import *
from threading import Thread

class ShellTweeter():


    def __init__(self) -> None:
        self.run()

    def start(self, id):
        self.tweet_server = TweeterServer(PORT_GENERAL_LOGGER,10,10,5)
        self.chord_server = ChordServer(DHT_name='Log',port = CHORD_PORT, disable_log='yes', id_hex= id)
        t1 = Thread(target=self.tweet_server.start_server)
        t2 = Thread(target=self.chord_server.start)
        t3 = Thread(target=self.tweet_server.send_pending_tasks, args= [self.tweet_server.end_event])
        t1.start()
        t2.start()
        t3.start()

    def options(self):          
        print('<--- Opciones --->')
        print('1. Start')
        print('2. Chord')
        print('<---+---==---+--->')
        
    def run(self):
        while True:
            self.options()
            option = input()
            if option == '1':
                self.begin_start()
            elif option == '2':
                print(self.tweet_server.chord_id)
            else:
                print('Opcion incorrecta')


    def begin_start(self):
        print('Poner hash especifico')
        id = input()
        if id == '':
            id = None
        self.start(id)

ShellTweeter().run()