from django.db import models
from mongoengine import Document, ImproperlyConfigured, fields
from datetime import datetime, date



class Image(Document):
    id = fields.SequenceField(primary_key=True)
    link = fields.StringField()
    image = fields.ImageField()
    description = fields.StringField()

class Idea(Document):
    CHART_CHOICES = (
        ("C","Candlestick"),
        ("L","Line"),
        ("B","Bars"),
        ("A","Area"),
    )
    SIGNAL_CHOICES = (
        ("S","Short"),
        ("L","Long"),
    )
    TIME_CHOICES = (
        ("s","30sec"),
        ("1m","1min"),
        ("3m","3min"),
        ("5m","5min"),
        ("15m","15min"),
        ("30m","30min"),
        ("45m","45min"),
        ("1h","1hour"),
        ("2h","2hour"),
        ("3h","3hour"),
        ("4h","4hour"),
        ("1d","1day"),
        ("1w","1week"),
        ("1mo","1month"),
    )
    id = fields.SequenceField(primary_key=True)
    create_date = fields.FloatField(default=lambda : datetime.timestamp(datetime.now()))
    views = fields.IntField(default=1)
    images = fields.ListField(fields.ReferenceField("Image"))
    script = fields.StringField()
    tags = fields.ListField(fields.StringField())
    rate = fields.FloatField()
    rate_list = fields.ListField(fields.ReferenceField("Rate"))
    signal_method = fields.StringField(choices=SIGNAL_CHOICES,max_length=1)
    chart_model = fields.StringField(choices=CHART_CHOICES,default="C",max_length=1)
    chart_time = fields.StringField(choices=TIME_CHOICES)
    pair = fields.StringField()


class Rate(Document):
    id = fields.SequenceField(primary_key=True)
    rate = fields.FloatField()
    user = fields.ReferenceField("User")
    rate_date = fields.FloatField(default=lambda : datetime.timestamp(datetime.now()))

    




