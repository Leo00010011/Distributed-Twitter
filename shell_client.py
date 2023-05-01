import API.client
# Flujo del cliente
# * Autenticacion?
# * Resuelve el ip del servidor
# * Si no hay token
#   * Si no esta registrado se registra
#   * Si Esta registrado y se logea
# * Darle feed al usuario
#   * Pedir el feed
#   * Codificar el feed para enviarlo
#   * Recibe el feed
#   * Lo decodifica
#   * Lo muestra

# enquieries para escoger entre opciones
# click tiene un pager, editor
# prompt tiene replies, history, autosugestion, autocompletion

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