try:
    from model import User, Tweet, ReTweet, Follow, Token
    from util import gen_token
except:
    from API.model import User, Tweet, ReTweet, Follow, Token
    from API.util import gen_token
# Consultas

def CreateUser(name, alias, password, alias_hash):
    try:
        if not User.select().where(User.name== name, User.alias==alias, User.password==password, User.alias_hash == alias_hash).exists():
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
                print('P')
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
    try:
        return Token.select().where(Token.user_id == user).get().token
    except:
        pass
    token = gen_token(64)
    while CheckToken(token):
        token = gen_token(64)
    Token.create(user_id= user, token= token)
    return token

def CreateTokenForced(nick, token):
    try:
        user = CheckUserAlias(nick)
        if not Token.select().where(Token.user_id== user, Token.token== token).exits():
            Token.create(user_id= user, token= token)
        return True
    except:
        return False

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
                if not Tweet.select().where(Tweet.user== user, Tweet.text== text, Tweet.date == date).exists():
                    Tweet.create(user= user, text= text)
            else:
                if not Tweet.select().join(User).where(User.alias== nick, Tweet.text== text, Tweet.date == date).exists():
                    Tweet.create(user= user, text= text, date = date)
            return True
        else:
            return False
    except:
        return False

def CreateReTweet(user_id, nick, date, retweet_date = None):    
    try:    
        user_id = CheckUserAlias(user_id)
        if retweet_date is None:
            if not ReTweet.select().where(ReTweet.user == user_id, ReTweet.nick ==nick, ReTweet.date_tweet== date).exists():
                ReTweet.create(user = user_id, nick= nick, date_tweet = date)
        else: 
            if not ReTweet.select().join(User).where(User.alias== nick, ReTweet.date_tweet== date, ReTweet.date_retweet == retweet_date).exists():
                ReTweet.create(user = user_id, nick= nick, date_tweet = date, date_retweet = retweet_date)
        return True
    except: 
        return False


def GetUserPaswordRange(hash_limit, offset = None, limit = None, my_hash = None):
    try:
        print("****HASHES****\n")
        print(hash_limit)
        print(my_hash)
        print("\n ************")
        if my_hash:
            if hash_limit > my_hash:
                if offset is None or limit is None: return User.select().where(User.alias_hash <= hash_limit, User.alias_hash > my_hash).order_by(User.alias).dicts()[:]
                return User.select(User.name,User.alias,User.password).where(User.alias_hash <= hash_limit, User.alias_hash > my_hash).order_by(User.alias).offset(offset).limit(limit).dicts()[:]

            if offset is None or limit is None: return User.select().where((User.alias_hash <= hash_limit) | (User.alias_hash > my_hash)).order_by(User.alias).dicts()[:]
            return User.select(User.name,User.alias,User.password).where((User.alias_hash <= hash_limit) | (User.alias_hash > my_hash)).order_by(User.alias).offset(offset).limit(limit).dicts()[:]

        if offset is None or limit is None: return User.select().where(User.alias_hash <= hash_limit).order_by(User.alias).dicts()[:]
        return User.select(User.name,User.alias,User.password).where(User.alias_hash <= hash_limit).order_by(User.alias).offset(offset).limit(limit).dicts()[:]
    except Exception as e: 
            print(e)
            return []

def GetTweetRange(hash_limit, offset = None, limit = None, my_hash = None):
    try:
        print("****HASHES****\n")
        print(hash_limit)
        print(my_hash)
        print("\n ************")
        if my_hash:
            if hash_limit > my_hash:
                if offset is None or limit is None: return Tweet.select().join(User).where(User.alias_hash <= hash_limit, User.alias_hash > my_hash).order_by(Tweet.date.desc()).dicts()[:]
                return Tweet.select(Tweet.text, Tweet.date, User.alias) \
                            .join(User).where(User.alias_hash <= hash_limit, User.alias_hash > my_hash) \
                            .order_by(Tweet.date.desc()).offset(offset).limit(limit).dicts()[:]

            if offset is None or limit is None: return Tweet.select().join(User).where((User.alias_hash <= hash_limit) | (User.alias_hash > my_hash)).order_by(Tweet.date.desc()).dicts()[:]
            return Tweet.select(Tweet.text, Tweet.date, User.alias).join(User).where((User.alias_hash <= hash_limit) | (User.alias_hash > my_hash)).order_by(Tweet.date.desc()).offset(offset).limit(limit).dicts()[:]
    
        if offset is None or limit is None: return Tweet.select().join(User).where(User.alias_hash <= hash_limit).order_by(Tweet.date.desc()).dicts()[:]
        return Tweet.select(Tweet.text, Tweet.date, User.alias).join(User).where(User.alias_hash <= hash_limit).order_by(Tweet.date.desc()).offset(offset).limit(limit).dicts()[:]
    except Exception as e: 
            print(e)
            return []


def GetRetweetRange(hash_limit, offset = None, limit = None, my_hash = None):
    try:
        print("****HASHES****\n")
        print(hash_limit)
        print(my_hash)
        print("\n ************")
    
        if my_hash:
            if hash_limit > my_hash:
                if offset is None or limit is None: return ReTweet.select().join(User).where(User.alias_hash <= hash_limit, User.alias_hash > my_hash).order_by(ReTweet.date_retweet.desc()).dicts()[:]
                return ReTweet.select(ReTweet.nick, ReTweet.date_tweet, ReTweet.date_retweet, User.alias).join(User).where(User.alias_hash <= hash_limit, User.alias_hash > my_hash).order_by(ReTweet.date_retweet.desc()).offset(offset).limit(limit).dicts()[:]
            
            if offset is None or limit is None: return ReTweet.select().join(User).where((User.alias_hash <= hash_limit) | (User.alias_hash > my_hash)).order_by(ReTweet.date_retweet.desc()).dicts()[:]
            return ReTweet.select(ReTweet.nick, ReTweet.date_tweet, ReTweet.date_retweet, User.alias).join(User).where((User.alias_hash <= hash_limit) | (User.alias_hash > my_hash)).order_by(ReTweet.date_retweet.desc()).offset(offset).limit(limit).dicts()[:]
    
        if offset is None or limit is None: return ReTweet.select().join(User).where(User.alias_hash <= hash_limit).order_by(ReTweet.date_retweet.desc()).dicts()[:]
        return ReTweet.select(ReTweet.nick, ReTweet.date_tweet, ReTweet.date_retweet, User.alias).join(User).where(User.alias_hash <= hash_limit).order_by(ReTweet.date_retweet.desc()).offset(offset).limit(limit).dicts()[:]
    except Exception as e: 
            print(e)
            return []


def GetFollowRange(hash_limit, offset = None, limit = None, my_hash = None):
    try:
        print("****HASHES****\n")
        print(hash_limit)
        print(my_hash)
        print("\n ************")
        if my_hash:
            if hash_limit > my_hash:
                if offset is None or limit is None: return Follow.select().join(User).where(User.alias_hash <= hash_limit, User.alias_hash > my_hash).order_by(User.alias.desc()).dicts()[:]
                return Follow.select(Follow.followed, User.alias).join(User).where(User.alias_hash <= hash_limit, User.alias_hash > my_hash).order_by(User.alias).offset(offset).limit(limit).dicts()[:]

            if offset is None or limit is None: return Follow.select().join(User).where((User.alias_hash <= hash_limit) | (User.alias_hash > my_hash)).order_by(User.alias.desc()).dicts()[:]
            return Follow.select(Follow.followed, User.alias).join(User).where((User.alias_hash <= hash_limit) | (User.alias_hash > my_hash)).order_by(User.alias).offset(offset).limit(limit).dicts()[:]

        if offset is None or limit is None: return Follow.select().join(User).where(User.alias_hash <= hash_limit).order_by(User.alias.desc()).dicts()[:]
        return Follow.select(Follow.followed, User.alias).join(User).where(User.alias_hash <= hash_limit).order_by(User.alias).offset(offset).limit(limit).dicts()[:]
    except Exception as e: 
            print(e)
            return []


def GetTokenRange(hash_limit, offset = None, limit = None, my_hash = None):
    try:
        print("****HASHES****\n")
        print(hash_limit)
        print(my_hash)
        print("\n ************")
        if my_hash:
            if hash_limit > my_hash:
                if offset is None or limit is None: return Token.select().join(User).where(User.alias_hash <= hash_limit, User.alias_hash > my_hash).order_by(User.alias.desc()).dicts()[:]
                return Token.select(Token.token, User.alias).join(User).where(User.alias_hash <= hash_limit, User.alias_hash > my_hash).order_by(User.alias).offset(offset).limit(limit).dicts()[:]
            
            if offset is None or limit is None: return Token.select().join(User).where((User.alias_hash <= hash_limit) | (User.alias_hash > my_hash)).order_by(User.alias.desc()).dicts()[:]
            return Token.select(Token.token, User.alias).join(User).where((User.alias_hash <= hash_limit) | (User.alias_hash > my_hash)).order_by(User.alias).offset(offset).limit(limit).dicts()[:]

        if offset is None or limit is None: return Token.select().join(User).where(User.alias_hash <= hash_limit).order_by(User.alias.desc()).dicts()[:]
        return Token.select(Token.token, User.alias).join(User).where(User.alias_hash <= hash_limit).order_by(User.alias).offset(offset).limit(limit).dicts()[:]
    except Exception as e: 
        print(e)
        return []

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
        ReTweet.delete().join(User).where(User.alias_hash <= hash_limit).execute() 
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
        try:
            Follow.select().join(User).where(User.alias == nick1, Follow.followed == nick2).get().followed
            return True
        except: pass
        
        user = User.select().where(User.alias == nick1).get()
        Follow.create(follower =user, followed = nick2)
        return True
    except:
        return False 

def GetProfileRange(nick_1, offset, limit):
    print(nick_1)
    tweet = []
    retweet = []
    try:
        tweet = Tweet.select(Tweet.text, Tweet.date,User.name, User.alias).join(User).where(User.alias == nick_1).order_by(Tweet.date.desc()).offset(offset).limit(limit).dicts()[:]
        
    except: pass
    try:
        retweet = ReTweet.select(ReTweet.date_tweet, ReTweet.date_retweet, ReTweet.nick, User.alias, User.name).join(User).where(User.alias == nick_1).order_by(ReTweet.date_retweet.desc()).offset(offset).limit(limit).dicts()[:]
        
    except: pass
    
    return (tweet,retweet)


def GetFollowed(nick):
    try:
        return Follow.select().join(User).where(User.alias == nick)[:]
    except: return []

def CheckTweet(nick, date):
    try:    
        return Tweet.select().join(User).where(User.alias == nick, Tweet.date == date).get()
    except:
        return False