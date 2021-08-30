#Django lib
from mongoengine import Document, fields

class TetherToman(Document):
    id = fields.SequenceField(primary_key=True)

    price = fields.FloatField(default=0)
