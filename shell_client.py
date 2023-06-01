import API.client as client
import API.util as util

class ShellClient():

    def __init__(self) -> None:
        self.client = client.Client()
        self.name = None
        self.nick = None
        self.token = None
        self.run()        

    def print_Dwitter(self):
        print("||=====================================||")
        print(" <<<<<<|||---\\\\\\ Dwitter ///---|||>>>>>>")
        print("||=====================================||")

    def print_options_unlogin(self):        
        print('<--- Opciones --->')
        print('1. Registrarse')
        print('2. Iniciar Sesion')
        print('3. Salir')
        print('<---+---==---+--->')

    def print_options_login(self):        
        print('<--- Opciones --->')
        print('1. Ver Nuevos Dweets')
        print('2. Crear Dweet')
        print('3. Crear ReDweet')
        print('4. Ver Perfil')
        print('5. Mi Perfil')
        print('6. Seguir Usuario')
        print('7. Cerrar Sesion')
        print('8. Salir')
        print('<---+---==---+--->')

    def run(self):
        while True:
            if self.token is None:
                util.clear()
                self.print_Dwitter()
                print()
                self.print_options_unlogin()     
                print('Seleccione una opcion')
                print("> ",end="")
                command = input()
                args = command.split()
                if args[0] == "1" and len(args) == 1:
                    self.sign_up()
                elif args[0] == "2" and len(args) == 1:
                    exit()
                elif args[0] == "3" and len(args) == 1:
                    exit()
                else:
                    pass
            else:
                util.clear()
                self.print_Dwitter()
                print()
                self.print_options_login()     
                print('Seleccione una opcion')
                print("> ",end="")
                command = input()
                args = command.split()
                # Ver Nuevos Dweets
                if args[0] == "1" and len(args) == 1:
                    pass
                # Crear Dweet
                elif args[0] == "2" and len(args) == 1:
                    pass
                # Crear ReDweet
                elif args[0] == "3" and len(args) == 1:
                    pass
                # Ver Perfil
                elif args[0] == "4" and len(args) == 1:
                    pass
                # Mi Perfil
                elif args[0] == "5" and len(args) == 1:
                    pass
                # Seguir Usuario
                elif args[0] == "6" and len(args) == 1:
                    pass
                # Cerrar Sesion
                elif args[0] == "7" and len(args) == 1:
                    exit()
                # Salir
                elif args[0] == "8" and len(args) == 1:
                    exit()
                else:
                    pass

    def sign_up(self):

        while True:
            util.clear()
            self.print_Dwitter()
            print()
            print('<--- Registrarse --->')
            print('Paso 1: Ingrese Nombre de Usuario')
            print('> ', end='')
            name = input()
            print('Paso 2: Ingrese Nick (sera unico para cada usuario)')
            print('> ', end='')
            nick = input()
            print('Paso 3: Ingrese Contrasenna')
            print('> ', end='')
            password = input()
            print('Paso 4: Repita Contrasenna')
            print('> ', end='')
            repeat_password = input()

            if password != repeat_password:
                print('ALERTA!!! La contrasenna no coincide :(')
                print('Escriba "r" para repetir el proceso o pulse simplemente ENTER para regresar al menu principal')
                inp = input()
                if inp != 'r':
                    return
            #if password != repeat_password:
            succesed, error = self.client.sign_up(name, nick, password)
            if succesed:
                print('USUARIO CREADO CON EXITO!')
                print('Pulse ENTER para volver al menu principal')
                input()
                return
            else:
                print('Ha ocurrido un ERROR :"(')
                print('<+++++ Error +++++>')
                print(error)
                print('<+++++|+++++|+++++>')
                print('Escriba "r" para repetir el proceso o pulse simplemente ENTER para regresar al menu principal')
                inp = input()
                if inp != 'r':
                    return
                
    def sign_in(self):

        while True:
            util.clear()
            self.print_Dwitter()
            print()
            print('<--- Iniciar Sesion --->')
            print('Paso 1: Ingrese Nick de Usuario')
            print('> ', end='')
            nick = input()
            print('Paso 2: Ingrese Contrasenna')
            print('> ', end='')
            password = input()            
            
            succesed, error = self.client.sign_in(nick, password)
            if succesed:
                print('SESION INICIADA CON EXITO!')
                print('Pulse ENTER para volver al menu principal')
                input()
                return
            else:
                print('Ha ocurrido un ERROR :"(')
                print('<+++++ Error +++++>')
                print(error)
                print('<+++++|+++++|+++++>')
                print('Escriba "r" para repetir el proceso o pulse simplemente ENTER para regresar al menu principal')
                inp = input()
                if inp != 'r':
                    return


s = ShellClient()
s.run()