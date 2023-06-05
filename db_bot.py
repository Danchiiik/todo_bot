from peewee import *
from decouple import config

db= PostgresqlDatabase(
    config('DB_NAME'),
    user=config('DB_USER'),
    password=config('DB_PASSWORD'),
    host=config('DB_HOST')
)

class ToDo(Model):
    user = CharField()
    task = CharField()
    
    class Meta:
        database = db
    

