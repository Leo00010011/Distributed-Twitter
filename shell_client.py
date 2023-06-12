import API.client as client
import API.util as util
import random
class ShellClient():

    def __init__(self) -> None:
        self.client = client.Client()
        self.name = None
        self.nick = None
        self.token = None
        self.cache = util.Cache()
        self.run() 

    def print_Dwitter(self):
        print("||=====================================||")
        print(" <<<<<<|||---\\\\\\ Dwitter ///---|||>>>>>>")
        print("||=====================================||")
        if self.nick is not None:            
            print(f'&>+- Usuario: {self.nick} -+<&')

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
                    self.sign_in()
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
                    self.feed()
                # Crear Dweet
                elif args[0] == "2" and len(args) == 1:
                    self.create_tweet()
                # Crear ReDweet
                elif args[0] == "3" and len(args) == 1:
                    pass
                # Ver Perfil
                elif args[0] == "4" and len(args) == 1:
                    self.see_profile()
                # Mi Perfil
                elif args[0] == "5" and len(args) == 1:
                    pass
                # Seguir Usuario
                elif args[0] == "6" and len(args) == 1:
                    print('intentar follow')
                    self.follow()
                # Cerrar Sesion
                elif args[0] == "7" and len(args) == 1:
                    self.logout()
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
                continue
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
            print('Paso 1: Ingrese su Nick de Usuario')
            print('> ', end='')
            nick = input()
            print('Paso 2: Ingrese su Contrasenna')
            print('> ', end='')
            password = input()            
            
            succesed, token = self.client.sign_in(nick, password)
            if succesed:
                self.token = token
                self.nick = nick
                print('SESION INICIADA CON EXITO!')
                print('Pulse ENTER para volver al menu principal')
                input()
                return
            else:
                print('Ha ocurrido un ERROR :"(')
                print('<+++++ Error +++++>')
                print(token)
                print('<+++++|+++++|+++++>')
                print('Escriba "r" para repetir el proceso o pulse simplemente ENTER para regresar al menu principal')
                inp = input()
                if inp != 'r':
                    return

    def logout(self):
        
        util.clear()
        self.print_Dwitter()
        print()
        while True:
            print('<--- Cerrar Sesion --->')
            print('Paso 1: Si esta seguro que desea cerrar sesion escriba "q"')
            print('> ', end='')
            if input() == 'q':                                
                succesed, error = self.client.logout(self.nick, self.token)
                if succesed:
                    print('SESION FINALIZADA CON EXITO!')
                    print('Pulse ENTER para volver al menu principal')
                    self.token = None
                    self.nick = None
                    self.name = None
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
                
    def see_profile(self):

        while True:            
            util.clear()
            self.print_Dwitter()
            print()
            print('<--- Ver Perfil --->')
            print('Paso 1: Ingrese el Nick del Usuario')
            print('> ', end='')
            nick = input()

            block = 0
            temp = []
            i = 0
            while True:
                succesed, data_profile, over = self.client.profile(nick, self.token, self.nick, block)                
                if succesed:
                    tweet = data_profile['tweets']
                    retweet = data_profile['retweets']
                    
                    print('|======< Dweets del Perfil >======|')
                    for t in tweet:
                        print('Tweet ', t)
                        self.cache.add_something(t["date"], t["text"], nick, None, None)
                        print('Guadado en Cache')
                        print(f'{i} Tweet de {nick} del {t["date"]}:')
                        print(t["text"])
                        print()
                        temp.append(t)
                        i+=1
                    print('|======< FIN de los Dweets >======|')
                    
                    print('|======< ReDweets del Perfil >======|')
                    for r in retweet:
                        self.cache.add_something(r["date_retweet"], t["text"], r["alias"], r["nick"], r["date_tweet"])
                        print('Guadado en Cache')
                        print(f'{i} ReTweet de {r["alias"]} del {r["date_retweet"]}\n')
                        print(f'Tweet Original de {r["nick"]} del {r["date_tweet"]}:')
                        print(r["text"])
                        print()
                        temp.append(r)
                        i+=1
                    print('|======< FIN de los ReDweets >======|')

                    print('Pulse ENTER para seguir viendo, o "q" para salir con el perfil')
                    if input() == 'q':
                        over = True
                                        
                    if over:
                        print('|======< Fin del Perfil >======|')
                        break
                    block += 1
                else:
                    print('Ha ocurrido un ERROR :"(')
                    print('<+++++ Error +++++>')
                    print(data_profile)
                    print('<+++++|+++++|+++++>')

                    if nick in self.cache.profiles:
                        publishes = list(self.cache.profiles[nick])
                        if len(publishes)>0:
                            print('Mostrando Cache')
                            print(publishes)
                            for thing in random.sample(publishes, min(10, len(publishes))):
                                if thing[3] is None:
                                    print(f'Tweet de {nick} del {thing[0]}:')
                                    print(thing[1])
                                    print()
                                else:
                                    print(f'{i} ReTweet de {nick} del {thing[0]}')
                                    print(f'Tweet Original de {thing[2]} del {thing[3]}:')
                                    print(thing[1])
                                    print()

                    
                    #saved = self.cache.profiles.get(nick, None)
                    #if saved is not None:
                    #    print('Mostrando datos guardados:')
                    #    for i, (date, (text, nick_original, date_original)) in enumerate(saved.items()):
                    #        if nick_original:
                    #            print(f'{i} ReTweet de {nick} del {date}\n')
                    #            print(f'Tweet Original de {nick_original} del {date_original}:')
                    #            print(text)
                    #        else:
                    #            print(f'{i} Tweet de {nick} del {date}:')
                    #            print(text)

                    print('Pulse "r" para volver a intentar, o pulse ENTER en otro caso')
                    inp = input()
                    if inp != 'r':
                        break                    
            print('Pulse ENTER para ver otro perfil, o escriba "q" para volver al menu principal')
            if input() == 'q':
                break

    def follow(self):        

        while True:
            util.clear()
            self.print_Dwitter()
            print()
            print('<--- Seguir Perfil --->')
            print('Paso 1: Ingrese el Nick del Usuario')
            print('> ', end='')
            nick = input()

            succesed, error = self.client.follow(nick, self.token, self.nick)
            if succesed:
                print(f'Comenzo a seguir a @{nick} CON EXITO!!!')
                print('Pulse ENTER para volver a intentar, o escriba "q" para volver al menu principal')
                input()
                return
            else:
                print('Ha ocurrido un ERROR :"(')
                print('<+++++ Error +++++>')
                print(error)
                print('<+++++|+++++|+++++>')
                print('Pulse ENTER para volver a intentar, o escriba "q" para volver al menu principal')
                if input() == 'q':
                    return

    def create_tweet(self):
        util.clear()
        self.print_Dwitter()
        print()

        while True:

            print('<--- Crear Dweet --->')
            print('Paso 1: Ingrese el texto del Dweet. Recuerde que solo puede contener 255 caracteres')
            print('> ', end='')
            text = input()

            print('Paso 2: Confirmar subida. Especifique la opcion que desee realizar.')
            print('1. Publicar Dweet')
            print('2. Editar Dweet')
            print('3. Cancelar Dweet')
            option = input()
            if option == '1':
                while True:
                    succesed, error = self.client.tweet(text, self.token, self.nick)
                    if succesed:
                        print('Dweet PUBLICADO CON EXITO!!!')
                        print('Pulse ENTER para volver al menu principal')
                        input()
                        return
                    else:
                        print('Ha ocurrido un ERROR :"(')
                        print('<+++++ Error +++++>')
                        print(error)
                        print('<+++++|+++++|+++++>')
                        print('Pulse ENTER para volver a intentar, o escriba "q" para volver al menu principal')
                        if input() == 'q':
                            return
            elif option == '2':
                continue
            else:
                break
    
                    
    def feed(self):

        util.clear()
        self.print_Dwitter()
        print()        
        
        temp = []
        while True:            
            succesed, things = self.client.feed(self.token, self.nick)                  
            if succesed:                                
                for i, thing in enumerate(things):
                    print('Archivo uno ', thing)
                    self.cache.add_something(thing[0], thing[1], thing[2], thing[3], thing[4])
                    print('Guadado en Cache')
                    if thing[3] is None:
                        print(f'{i} Tweet de {thing[2]} del {thing[0]}:')
                        print(thing[1])
                        print()
                    else:
                        print(f'{i} ReTweet de {thing[2]} del {thing[0]}')
                        print(f'Tweet Original de {thing[3]} del {thing[4]}:')
                        print(thing[1])
                        print()              
                if len(things) > 0:
                    retweting = True
                    while retweting:
                        print('Seleccione el Dweet que desea redweetear o simplemente pulse ENTER')
                        try:
                            option = int(input())
                            if 0 <= option < len(things):
                                done, error_re = self.client.retweet(self.token, self.nick,  thing[2], thing[0])
                                if done:
                                    print('ReDweet realizado con EXITO')
                                else:
                                    print('ReDweet FALLIDO')
                                    print('<+++++ Error +++++>')
                                    print(error_re)
                                    print('<+++++|+++++|+++++>')
                        except:
                            retweting = False
            else:
                print('Ha ocurrido un ERROR :"(')
                print('<+++++ Error +++++>')
                print(things)
                print('<+++++|+++++|+++++>')                
            print('Pulse ENTER para volver a intentar, o escriba "q" para terminar')
            inp = input()
            if inp == 'q':
                break
            '''
            i = block*10
            if succesed:
                tweet = data_profile['tweets']
                retweet = data_profile['retweets']
                
                print('|======< Dweets del Perfil >======|')
                for t in tweet:
                    print(f'{i} Tweet de {nick} del {t["date"]}:')
                    print(t["text"])
                    print()
                    temp.append(t)
                    i+=1
                print('|======< FIN de los Dweets >======|')
                
                print('|======< ReDweets del Perfil >======|')
                for r in retweet:
                    print(f'{i} ReTweet de {r["alias"]} del {r["date_retweet"]}\n')
                    print(f'Tweet Original de {r["nick"]} del {r["date_tweet"]}:')
                    print(r["text"])
                    print()
                    temp.append(r)
                    i+=1
                print('|======< ReDweets del Perfil >======|')
                
                repeat = True
                while repeat:
                    print('Escriba el numero del Dweet o ReDeweet que desea ReDweetear. En caso contrario presione ENTER')
                    try:
                        inpu = int(input())
                        if 0 <= inpu < len(temp):
                            print('RETWEET desde el client')
                            print(temp[inpu])
                            if 'date_retweet' in temp[inpu].keys():
                                good, retweet = self.client.retweet(self.token, self.nick, temp[inpu]["nick"], temp[inpu]["date_tweet"])
                            else:
                                good, retweet = self.client.retweet(self.token, self.nick, temp[inpu]["alias"], temp[inpu]["date"])
                            print('RETWEET recibido al cliente')
                            if good:
                                print('ReDweet realizado con EXITO')
                            else:
                                print('ReDweet NOOOOO realizado con EXITO')
                    except:
                        repeat = False

                if over:
                    print('|======< Fin del Perfil >======|')
                    break
                print('Pulse ENTER para ver mas, o escriba "q" para terminar con este usuario')
                if input() == 'q':
                    break
                block += 1
            else:
                print('Ha ocurrido un ERROR :"(')
                print('<+++++ Error +++++>')
                print(data_profile)
                print('<+++++|+++++|+++++>')
                print('Pulse ENTER para volver a intentar, o escriba "q" para terminar con este usuario')
                inp = input()
                if inp != 'q':
                    return
            '''



s = ShellClient()
s.run()