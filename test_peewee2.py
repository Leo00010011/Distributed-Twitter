import peewee
from peewee import Model, SqliteDatabase, CharField, DateField, IntegerField

db = SqliteDatabase('db_social_network.db')

db.connect()
