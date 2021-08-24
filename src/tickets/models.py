from mongoengine import Document, fields

from datetime import datetime, date

class TicketRoom(Document):

    id = fields.SequenceField(primary_key=True)
    SECTION_CHOICES = (
        ("f","Financial"),
        ("t","Technical"),
        ("s","suggestion"),
    )
    PRIORITY_CHOICES = (
        ("l","low"),
        ("m","medium"),
        ("h","high"),
    )

    STATUS_CHOICES = (
        ("i","In Progress"),
        ("a","Answerd"),
        ("e","end"),
    )
    section = fields.StringField(choices=SECTION_CHOICES,max_length=1)

    user = fields.ReferenceField("User")

    priority= fields.StringField(choices=PRIORITY_CHOICES,max_length=1)

    subject = fields.StringField(max_length=300)

    texts = fields.ListField(fields.ReferenceField("TicketText"))

    create_date = fields.FloatField(default=lambda: datetime.timestamp(datetime.now()))

    meta = {"ordering": ["-create_date"]}

class TicketText(Document):

    id = fields.SequenceField(primary_key=True)

    user = fields.ReferenceField("User")

    text = fields.StringField()

    image = fields.ReferenceField("Image")

    create_date = fields.FloatField(default=lambda: datetime.timestamp(datetime.now()))

    meta = {"ordering": ["-create_date"]}



