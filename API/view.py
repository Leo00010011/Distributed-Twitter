try:
    from model import User, Tweet, ReTweet, Follow, Token
    from util import gen_token
except:
    from API.model import User, Tweet, ReTweet, Follow, Token
    from API.util import gen_token
# Consultas

def CreateUser(name, alias, password):
    pass

def CheckUserAlias(alias):
    raise NotImplementedError()

def GetUserName(name):
    raise NotImplementedError()

def CreateToken(user_id):
    '''
    Crea un token aleatoria de 64 bytes para asignarlo a un usuario.
    Si al generar el token este estuviera asignado, se genera otro, hasta
    que no haya coincidencia.
    '''
    token = gen_token(64)
    while CheckToken(token):
        token = gen_token(64)
    Token.create(user_id= user_id, token= token)

def CheckToken(token):
    '''
    Devuelve el ID del usuario asignado al token
    En caso de no ser encontrado devuelve None
    '''
    try:
        return Token.select().where(Token.token == token).get().user_id
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
    Token.delete().where(Token.token == token, Token.user_id == user_id).execute()

def CreateTweet(user_id, text):
    if User.select().where(User.id == user_id).count() == 1:
        Tweet.create(user_id= user_id, text= text)
        return True
    else:
        return False

def CreateReTweet(user_id, tweet_id):
    raise NotImplementedError()



