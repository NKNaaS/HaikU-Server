from peewee import SqliteDatabase, Model, Field, IntegerField, CharField, ForeignKeyField
from enum import Enum

import logging

logger = logging.getLogger('peewee')
logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler())

database = SqliteDatabase('test.db')


class BaseModel(Model):
    class Meta:
        database = database


class Season(Enum):
    SPRING = 0
    SUMMER = 1
    FALL = 2
    WINTER = 3


class SeasonField(Field):
    field_type = 'INT'

    def db_value(self, value: Season):
        return value.value

    def python_value(self, value):
        return Season(value)


class Kigo(BaseModel):
    kigo = CharField(unique=True)
    spring = IntegerField(default=0)
    summer = IntegerField(default=0)
    fall = IntegerField(default=0)
    winter = IntegerField(default=0)
    season = SeasonField()

    def save(self, *args, **kwargs):
        seasons = [self.spring, self.summer, self.fall, self.winter]
        self.season = Season(max(zip(seasons, range(len(seasons))))[1])
        return super(Kigo, self).save(*args, **kwargs)


class Image(BaseModel):
    image = CharField(unique=True)
    kigo = ForeignKeyField(Kigo, backref='images')


class Haiku(BaseModel):
    first = CharField()
    second = CharField()
    third = CharField()
    kigo = ForeignKeyField(Kigo)


def create_tables():
    if Kigo.table_exists():
        return

    with database:
        database.create_tables([Kigo, Image, Haiku])

    kaki = Kigo.create(kigo='柿', fall=1).save()
    Image.create(image='6qqV9MTuEemXsrj2sRfcWw', kigo=kaki).save()
