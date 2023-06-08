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
    except Exception as e:
        print(e)
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
    try:
        print("HOLA")
        print("HOLA")
        user = User.select().where(User.alias == alias).get()
        print("HOLA")
        print("HOLA")
        print(user)
        if  user:
            if user.password == password:
                return CreateToken(user)
        return False
    except:
        return False

def CreateToken(user):
    '''
    Crea un token aleatoria de 64 bytes para asignarlo a un usuario.
    Si al generar el token este estuviera asignado, se genera otro, hasta
    que no haya coincidencia.
    '''
    token = gen_token(64)
    while CheckToken(token):
        token = gen_token(64)
    Token.create(user_id= user, token= token)
    return token

def CreateTokenForced(nick, token):
    user = CheckUserAlias(nick)
    Token.create(user_id= user, token= token)

def CheckToken(token, nick = None):
    try:
        if nick:
            return Token.select().where(Token.token == token).get().user_id.alias == nick
        return Token.select().where(Token.token == token).get()
    except:
        return False

def ForceRemoveToken(token):
    '''
    Fuerza la eliminacion del token
    '''
    Token.delete().where(Token.token == token).execute() 

def RemoveToken(nick, token):
    '''
    Elimina de forma segura el token
    '''
    try:
        user = CheckUserAlias(nick)
        Token.delete().where(Token.token == token, Token.user_id == user).execute()
        return True
    except:
        return False
def CreateTweet(text, nick, date=None):
    try:
        user = User.select().where(User.alias == nick).get()
        if user:
            if date is None:
                Tweet.create(user= user, text= text)
            else: Tweet.create(user= user, text= text, tweet_date = date)
            return True
        else:
            return False
    except:
        return False

def CreateReTweet(user_id, nick, date, retweet_date = None):
    try:
        user_id = CheckUserAlias(user_id)
        if retweet_date is None:
            ReTweet.create(user = user_id, nick= nick, date_tweet = date)
        else: 
            ReTweet.create(user = user_id, nick= nick, date_tweet = date, date_retweet = retweet_date)
        return True
    except: 
        return False


def GetUserPaswordRange(hash_limit, offset = None, limit = None):
    if offset is None or limit is None: return User.select().where(User.alias_hash <= hash_limit).order_by(User.alias).dict()[:]
    return User.select().where(User.alias_hash <= hash_limit).order_by(User.alias).offset(offset).limit(limit).dict()[:]

def GetTweetRange(hash_limit, offset = None, limit = None):
    if offset is None or limit is None: return Tweet.select().join(User).where(User.alias_hash <= hash_limit).order_by(Tweet.date.desc()).dict()[:]
    return Tweet.select().join(User).where(User.alias_hash <= hash_limit).order_by(Tweet.date.desc()).offset(offset).limit(limit).dict()[:]

def GetRetweetRange(hash_limit, offset = None, limit = None):
    if offset is None or limit is None: return Retweet.select().join(User).where(User.alias_hash <= hash_limit).order_by(Retweet.date_retweet.desc()).dict()[:]
    return Retweet.select().join(User).where(User.alias_hash <= hash_limit).order_by(Retweet.date_retweet.desc()).offset(offset).limit(limit).dict()[:]

def GetFollowRange(hash_limit, offset = None, limit = None):
    if offset is None or limit is None: return Follow.select().join(User).where(User.alias_hash <= hash_limit).order_by(User.alias.desc()).dict()[:]
    return Follow.select().join(User).where(User.alias_hash <= hash_limit).order_by(User.alias.desc()).offset(offset).limit(limit).dict()[:]

def GetTokenRange(hash_limit, offset = None, limit = None):
    if offset is None or limit is None: return Token.select().join(User).where(User.alias_hash <= hash_limit).order_by(User.alias.desc()).dict()[:]
    return Token.select().join(User).where(User.alias_hash <= hash_limit).order_by(User.alias.desc()).offset(offset).limit(limit).dict()[:]


def DeleteUserRange(hash_limit):
    try :
        User.delete().where(User.alias_hash <= hash_limit).execute()
        return True
    except:
        return False
def DeleteTweetRange(hash_limit):
    try :
        Tweet.delete().join(User).where(User.alias_hash <= hash_limit).execute() 
        return True
    except:
        return False
def DeleteRetweetRange(hash_limit):
    try :
        Retweet.delete().join(User).where(User.alias_hash <= hash_limit).execute() 
        return True
    except:
        return False
def DeleteFollowRange(hash_limit):
    try :
        Follow.delete().join(User).where(User.alias_hash <= hash_limit).execute() 
        return True
    except:
        return False
def DeleteTokenRange(hash_limit):
    try :
        Token.delete().join(User).where(User.alias_hash <= hash_limit).execute() 
        return True
    except:
        return False

def CreateFollow(nick1,nick2):
    try:
        user = User.select().where(User.alias == nick1).get()
        Follow.create(follower =user, followed = nick2)
        return True
    except:
        return False 

def GetProfileRange(nick, offset, limit):
    return (Tweet.select().join(User).where(User.alias == nick).order_by(Tweet.date.descendent()).offset(offset).limit(limit)[:], Retweet.select().join(User).where(User.alias == nick).order_by(Retweet.date_retweet.descendent()).offset(offset).limit(limit)[:])


def GetFollowed(nick):
    return Follow.select().join(User).where(User.alias == nick)[:]

def CheckTweet(nick, date):
    try:    
        return Tweet.select().join(User).where(User.alias == nick, Tweet.date == date).get()
    except:
        return False