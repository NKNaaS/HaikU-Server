from app import api
from marshmallow import Schema, fields, ValidationError


@api.schema('Haiku')
class Haiku(Schema):
    first = fields.Str()
    second = fields.Str()
    third = fields.Str()
