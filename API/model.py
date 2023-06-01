import peewee
import hashlib
from peewee import Model, SqliteDatabase, CharField, DateField, IntegerField, ForeignKeyField

main_db = SqliteDatabase('social_network.db')

# Modelo de Base de Datos

class User(Model):
    name = CharField(120)
    alias = CharField(16, unique=True)
    password = CharField(41)
    alias_hash = CharField(41)
    class Meta:
        database = main_db

class Follow(Model):
    follower = ForeignKeyField(User)
    followed = ForeignKeyField(User)

    class Meta:
        database = main_db 
        # indexes = (((follower, followed), True), )   

class Tweet(Model):
    text = CharField(256)
    user = ForeignKeyField(User)
    
    class Meta:
        database = main_db

class ReTweet(Model):
    user = ForeignKeyField(User)
    tweet = ForeignKeyField(Tweet)

    class Meta:
        database = main_db
        # indexes = (((user, tweet), True), ) 

class Token(Model):
    user_id = ForeignKeyField(User)
    token = CharField(64, unique=True)

    class Meta:
        database = main_db

# Ejecutar solo una primera vez para crear las tablas, luego comentar
# main_db.create_tables([User, Follow, Tweet, ReTweet, Token])

# x = User.select().offset(1)
# for i,u in enumerate(x):
#     print(u.name)
# print(i)


# print("Lexa_hash:" + str(hashlib.sha1(b'LachiD').hexdigest()))
# print("LachiD_hash:" + str(hash('LachiD')))
# print("Chino_hash:" + str(hash('Chino')))

# User.create(name= 'Alejandra', alias='Lexa', password= 'Lucky**13',alias_hash= hashlib.sha1(b'Lexa').hexdigest())
# User.create(name= 'Lazaro', alias='LachiD', password= 'lachiD', alias_hash = hashlib.sha1(b'LachiD').hexdigest())
# User.create(name= 'Leonardo', alias='Chino', password= 'LeoUlloa',alias_hash= hashlib.sha1(b'Chino').hexdigest())

# print('2b1b345dd3602f2643253a0a5c052a667e077255' >= 'a249c61954e68496e45683b0463f2b07a64dd835' )