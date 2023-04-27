import server02
import threading
from threading import Thread

server = server02.Server("0.0.0.0", 12345)

while True:
    print(">",end="")
    command = input()
    
    if command == "run":        
        t = Thread(target= server.run)
        t.start()        
    elif command == "stop":        
        server.stop()
    elif command == "msg":
        server.broadcast("jka")
    elif command == "exit":
        #if server.runing:
        #    server.stop()
        exit()
