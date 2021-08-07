from django.db import models
from mongoengine import Document, ImproperlyConfigured, fields
from datetime import datetime, date

class Messagebox(Document):
    id = fields.SequenceField(primary_key=True)
    user = fields.ReferenceField("User")
    messages = fields.ListField(fields.ReferenceField("Message"))
    read = fields.IntField()
    unread = fields.IntField()

class Message(Document):
    id = fields.SequenceField(primary_key=True)
    #sender user
    user = fields.ReferenceField("User")
    create_date = fields.FloatField(default=lambda: datetime.timestamp(datetime.now()))
    is_read = fields.BooleanField(default=False)
    image = fields.ReferenceField("Image")
    title = fields.StringField()
    text = fields.StringField()