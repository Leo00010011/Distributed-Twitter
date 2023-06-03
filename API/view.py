try:
    from model import User, Tweet, ReTweet, Follow, Token
    from util import gen_token
except:
    from API.model import User, Tweet, ReTweet, Follow, Token
    from API.util import gen_token
# Consultas

def CreateUser(name, alias, password, alias_hash):
    try:
        User.create(name= name, alias=alias, password=password, alias_hash = alias_hash)
        return True
    except:
        return False

def CheckUserAlias(alias):
    '''
    Devualve el ID del Usuario asignado al Alias
    En caso de no ser encontrado devuelve None
    '''
    try:
        return User.select().where(User.alias == alias).get()
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

def LogIn(alias, password):

    user = CheckUserAlias(alias)
    if user and user.password == password:
           return view.CreateToken(user.id)
    return None

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

def CheckToken(token, nick):
    '''
    Devuelve el ID del usuario asignado al token
    En caso de no ser encontrado devuelve None
    '''
    try:
        return Token.select().where(Token.token == token).get().user_id.alias == nick
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

def CreateTweet(text, nick):

    user_id = User.select().where(User.alias == nick).get().id
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


def GetUserPaswordRange(hash_limit, offset, limit):
    return User.select().where(User.alias_hash <= hash_limit).oreder_by(User.alias).offset(offset).limit(limit)

def GetTweetRange(hash_limit, offset, limit):
    return Tweet.select().where(Tweet.user.alias_hash <= hash_limit).oreder_by(Tweet.user.alias).offset(offset).limit(limit)

def GetRetweetRange(hash_limit, offset, limit):
    return Retweet.select().where(Retweet.user.alias_hash <= hash_limit).oreder_by(Retweet.user.alias).offset(offset).limit(limit)

def GetFollowRange(hash_limit, offset, limit):
    return Follow.select().where(Follow.follower.alias_hash <= hash_limit).oreder_by(Tweet.follower.alias).offset(offset).limit(limit)

def GetTokenRange(hash_limit, offset, limit):
    return Token.select().where(Token.user_id.alias_hash <= hash_limit).oreder_by(Token.user_id.alias).offset(offset).limit(limit)


def DeleteUserRange(hash_limit):
    try :
        User.delte().where(User.alias_hash <= hash_limit)
        return True
    except:
        return False
def DeleteTweetRange(hash_limit):
    try :
        Tweet.select().where(Tweet.user.alias_hash <= hash_limit) 
        return True
    except:
        return False
def DeleteRetweetRange(hash_limit):
    try :
        Retweet.select().where(Retweet.user.alias_hash <= hash_limit) 
        return True
    except:
        return False
def DeleteFollowRange(hash_limit):
    try :
        Follow.select().where(Follow.follower.alias_hash <= hash_limit) 
        return True
    except:
        return False
def DeleteTokenRange(hash_limit):
    try :
        Token.select().where(Token.user_id.alias_hash <= hash_limit) 
        return True
    except:
        return False

def CreateFollow(nick1,nick2):
    try:
        user = User.select().where(User.alias == nick1).get()
        Follow.create(user,nick2)
        return True
    except:
        return False 

def GetProfileRange(nick, offset, limit):
    return Tweet.select().where(Tweet.user.alias == nick).oreder_by(Tweet.date.descendent()).offset(offset).limit(limit)


