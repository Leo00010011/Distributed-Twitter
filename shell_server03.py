import server03
import threading
from threading import Thread
import time

server = server03.Server()

while True:
    print("> ",end="")
    command = input()
    
    if command == "start":
        t = Thread(target= server.general_listen)
        t.start()
    elif command == "stop":        
        server.stop()
        time.sleep(3)
    elif command == "msg":
        server.msg()
    elif command == "list":
        print("Listado")
        print(list(server.list_clients_pasive_listen.keys()))
    elif command == "exit":
        server.stop()
        time.sleep(3)
        exit(0)