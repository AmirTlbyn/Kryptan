#Django lib
from mongoengine import Document, fields

#Python lib
from datetime import datetime, date



class Image(Document):
    id = fields.SequenceField(primary_key=True)
    image = fields.StringField()
    description = fields.StringField()

class Idea(Document):
    
    SIGNAL_CHOICES = (
        ("N","None"),
        ("S","Short"),
        ("L","Long"),
    )


    IDEA_CHOICES = (
        ("1","Private"),
        ("2","Public"),
    )
    
    id = fields.SequenceField(primary_key=True)
    user = fields.ReferenceField("User")
    create_date = fields.FloatField(default=lambda : datetime.timestamp(datetime.now()))
    views = fields.IntField(default=1)
    screenshots = fields.ListField(fields.ReferenceField("Screenshot"))
    script = fields.StringField()
    tags = fields.ListField(fields.ReferenceField("Tag"))
    rate = fields.FloatField()
    rate_list = fields.ListField(fields.ReferenceField("Rate"))
    signal_method = fields.StringField(choices=SIGNAL_CHOICES,max_length=1, default="N")
    is_hide= fields.BooleanField(default=False)
    symbol = fields.ReferenceField("Symbol")
    
    idea_type = fields.StringField(choices=IDEA_CHOICES, default="2")
    is_editor_pick = fields.BooleanField(default=False)
    pick_date = fields.FloatField()


class Rate(Document):
    id = fields.SequenceField(primary_key=True)
    rate = fields.FloatField()
    user = fields.ReferenceField("User")
    create_date = fields.FloatField(default=lambda : datetime.timestamp(datetime.now()))


class Screenshot(Document):
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
    CHART_CHOICES = (
        ("C","Candlestick"),
        ("L","Line"),
        ("B","Bars"),
        ("A","Area"),
    )
    id = fields.SequenceField(primary_key=True)
    user = fields.ReferenceField("User")
    image = fields.StringField()
    chart_model = fields.StringField(choices=CHART_CHOICES,default="C",max_length=1)
    timeframe = fields.StringField(choices=TIME_CHOICES)
    pair = fields.StringField()


class Tag(Document):
    id = fields.SequenceField(primary_key=True)
    tag = fields.StringField()

class View(Document):
    id = fields.SequenceField(primary_key=True)
    idea = fields.ReferenceField("Idea")
    user = fields.ReferenceField("User")
    ip = fields.StringField()
    last_view = fields.FloatField(default=lambda: datetime.timestamp(datetime.now()))


    




