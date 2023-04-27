from model import User, Tweet, ReTweet, Follow, Token

# Consultas

def CreateUser(name, alias, password):
    pass

def CheckUserAlias(alias):
    raise NotImplementedError()

def GetUserName(name):
    raise NotImplementedError()

def CreateToken(user_id):
    raise NotImplementedError()

def CheckToken(user_id, token):
    raise NotImplementedError()

def RemoveToken(user_id, token):
    raise NotImplementedError()

def CreateTweet(user_id, text):
    if User.select().where(User.id == user_id).count() == 1:
        Tweet.create(user_id= user_id, text= text)
        return True
    else:
        return False

def CreateReTweet(user_id, tweet_id):
    raise NotImplementedError()



