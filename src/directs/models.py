from django.db import models
from mongoengine import Document, ImproperlyConfigured, fields
from datetime import datetime, date

class MessageBox(Document):
    id = fields.SequenceField(primary_key=True)
    user = fields.ReferenceField("User")
    automatic_messages = fields.ListField(fields.ReferenceField("AutomaticMessages"))
    automatic_msg_read = fields.IntField(default=0)
    automatic_msg_unread = fields.IntField(default=0)


class ChatRoom(Document):

    id = fields.SequenceField(primary_key=True)
    users = fields.ListField(fields.ReferenceField("User"))
    create_date = fields.FloatField(default=lambda: datetime.timestamp(datetime.now()))
    messages = fields.ListField(fields.ReferenceField("Message"))


    meta = {"ordering":["-create_date"]}

class Message(Document):
    id = fields.SequenceField(primary_key=True)
    #sender user
    user = fields.ReferenceField("User")
    create_date = fields.FloatField(default=lambda: datetime.timestamp(datetime.now()))
    is_read = fields.BooleanField(default=False)
    image = fields.ReferenceField("Image")
    title = fields.StringField()
    text = fields.StringField()

    meta = {"ordering": ["-create_date"]}

class AutomaticMessage(Document):

    id = fields.SequenceField(primary_key=True)

    title = fields.StringField(default="پیام خودکار")

    text = fields.StringField()
    
    create_date = fields.FloatField(default=lambda : datetime.timestamp(datetime.now()))

    is_read = fields.BooleanField(default=False)

    meta = {"ordering": ["-create_date"]}