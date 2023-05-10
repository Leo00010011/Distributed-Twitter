try:
    from model import User, Tweet, ReTweet, Follow, Token
    from util import gen_token
except:
    from API.model import User, Tweet, ReTweet, Follow, Token
    from API.util import gen_token
# Consultas

def CreateUser(name, alias, password):
    try:
        User.create(name= name, alias=alias, password=password)
        return True
    except:
        return False

def CheckUserAlias(alias):
    '''
    Devualve el ID del Usuario asignado al Alias
    En caso de no ser enconteado devuelve None
    '''
    try:
        return User.select().where(User.alias == alias).get().id
    except:
        return None


def GetTokenLogIn(alias, password):
    '''
    Cuando el usuario se logea con alias y contrasenna 
    se busca que este usuario exista y se le asigna un token
    en caso de que si y se devuelve este Token
    '''
    user = User.select().where(User.alias == alias)
    if  user:
        if user.get().password == password:
            return CreateToken(user.get().id)
    return False


def CreateToken(user_id):
    '''
    Crea un token aleatoria de 64 bytes para asignarlo a un usuario.
    Si al generar el token este estuviera asignado, se genera otro, hasta
    que no haya coincidencia.
    '''
    token = gen_token(64)
    while CheckToken(token):
        token = gen_token(64)
    Token.create(id= user_id, token= token)
    return token

def CheckToken(token):
    '''
    Devuelve el ID del usuario asignado al token
    En caso de no ser encontrado devuelve None
    '''
    try:
        return Token.select().where(Token.token == token).get().id
    except:
        return None    

def ForceRemoveToken(token):
    '''
    Fuerza la eliminacion del token
    '''
    Token.delete().where(Token.token == token).execute() 

def RemoveToken(user_id, token):
    '''
    Elimina de forma segura el token
    '''
    Token.delete().where(Token.token == token, Token.id == user_id).execute()

def CreateTweet(token, text):
    user_id = CheckToken(token)
    if user_id:
        Tweet.create(user_id= user_id, text= text)
        return True
    else:
        return False

def CreateReTweet(user_id, tweet_id):
    
    try:
        ReTweet.create(user = user_id, tweet=tweet_id)
        return True
    except: 
        return False




