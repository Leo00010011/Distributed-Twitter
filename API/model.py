import peewee
from peewee import Model, SqliteDatabase, CharField, DateField, IntegerField, ForeignKeyField

main_db = SqliteDatabase('social_network.db')

# Modelo de Base de Datos

class User(Model):
    name = CharField(120)
    alias = CharField(16)
    password = CharField(32)

    class Meta:
        database = main_db

class Follow(Model):
    follower = ForeignKeyField(User)
    followed = ForeignKeyField(User)

    class Meta:
        database = main_db    

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

class Token(Model):
    user_id = ForeignKeyField(User)
    token = CharField(64)

    class Meta:
        database = main_db

# Ejecutar solo una primera vez para crear las tablas, luego comentar
#db.create_tables([User, Sigue, Tweet, ReTweet])