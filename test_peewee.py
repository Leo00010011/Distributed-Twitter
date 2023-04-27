import peewee
from peewee import Model, SqliteDatabase, CharField, DateField, IntegerField, ForeignKeyField

db = SqliteDatabase('db_social_network.db')

class Usuario(Model):
    nombre = CharField(120)
    alias = CharField(8)

    class Meta:
        database = db

class Sigue(Model):
    seguidor = ForeignKeyField(Usuario)
    seguido = ForeignKeyField(Usuario)

    class Meta:
        database = db        

    def __repr__(self) -> str:
        return super().__repr__() + 'holas'     

class Tweet(Model):
    texto = CharField(80)
    usuario = ForeignKeyField(Usuario)
    
    class Meta:
        database = db

class ReTweet(Model):
    usuario = ForeignKeyField(Usuario)
    tweet = ForeignKeyField(Tweet)

    class Meta:
        database = db

db.connect()


#db.create_tables([Usuario, Tweet, ReTweet, Sigue])
print(Usuario.select(Usuario.id).where(Usuario.nombre == 'Alejandra'))
#q2 = (
#    Usuario.select(Usuario.nombre, Sigue.seguido)
#    .join(Sigue, on= (Usuario.id == Sigue.seguidor))
#    .join(Sigue,Usuario, on= (Sigue.seguido==Usuario.id))
#    )
#print(q2)
##print(Sigue.select().where(Sigue.seguidor == 2))
#for p in q2:
#    print()
