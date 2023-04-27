import API.client

class ShellClient():

    def __init__(self) -> None:
        self.client = API.client.Client()
        self.run()

    def run(self):
        while True:
            print("> ",end="")
            command = input()    
            args = command.split()

            if args[0] == "start":        
                self.client.set_ip_server("127.0.0.1")            
            elif args[0] == "exit":
                exit()    

s = ShellClient()
s.run()