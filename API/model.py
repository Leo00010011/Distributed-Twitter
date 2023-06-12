import peewee
import hashlib
import datetime
from peewee import Model, SqliteDatabase, CharField, DateField, IntegerField, ForeignKeyField, DateTimeField

try:
    main_db = SqliteDatabase('/home/social_network.db')
    main_db.connect()
    main_db.close()
except:
    pass


# Modelo de Base de Datos

class User(Model):
    name = CharField(120)
    alias = CharField(16, unique=True)
    password = CharField(64)
    alias_hash = CharField(64)
    class Meta:
        database = main_db

class Follow(Model):
    follower = ForeignKeyField(User)
    followed =  CharField(16)

    class Meta:
        database = main_db 
        # indexes = (((follower, followed), True), )   

class Tweet(Model):
    text = CharField(256)
    user = ForeignKeyField(User)
    date = DateTimeField()
    class Meta:
        database = main_db

class ReTweet(Model):
    user = ForeignKeyField(User)
    nick = CharField(16)
    date_tweet = DateTimeField()
    date_retweet = DateTimeField()

    class Meta:
        database = main_db
        # indexes = (((user, tweet), True), ) 

class Token(Model):
    user_id = ForeignKeyField(User)
    token = CharField(64, unique=True)

    class Meta:
        database = main_db



# Ejecutar solo una primera vez para crear las tablas, luego comentar
main_db.create_tables([User, Follow, Tweet, ReTweet, Token])



# User.create(name= 'Alejandra', alias='Lexa', password= 'Lucky**13',alias_hash= hashlib.sha256(b'Lexa').hexdigest())
# User.create(name= 'Lazaro', alias='LachiD', password= 'lachiD', alias_hash = hashlib.sha256(b'LachiD').hexdigest())
# User.create(name= 'Leonardo', alias='Chino', password= 'LeoUlloa',alias_hash= hashlib.sha256(b'Chino').hexdigest())

