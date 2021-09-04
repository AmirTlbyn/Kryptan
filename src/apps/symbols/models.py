#Django lib
from mongoengine import Document, fields


class Symbol(Document):
    id = fields.SequenceField(primary_key=True)
    name = fields.StringField(max_length = 200)
    name_fa = fields.StringField(max_length=200)
    symbol = fields.StringField(max_length= 100)
    slug = fields.StringField(max_length=100)

    logo_40 = fields.ReferenceField("Image")
    logo_24 = fields.ReferenceField("Image")

    date_added = fields.FloatField()
    description = fields.StringField()

    mc_rank = fields.IntField()

class SymbolHistorical(Document):
    id = fields.SequenceField(primary_key=True)
    symbol = fields.ReferenceField("Symbol")

    all_time_high = fields.FloatField()
    all_time_high_date = fields.FloatField()

    all_time_low = fields.FloatField()
    all_time_low_date = fields.FloatField()


class SymbolQuote(Document):

    id = fields.SequenceField(primary_key=True)
    symbol = fields.ReferenceField("Symbol")
    
    price = fields.FloatField()
    price_24_high = fields.FloatField()
    price_24_low = fields.FloatField()

    price_in_btc = fields.FloatField()
    percent_change_1h = fields.FloatField()
    percent_change_24h = fields.FloatField()
    percent_change_7d = fields.FloatField()
    percent_change_30d = fields.FloatField()
    percent_change_60d = fields.FloatField()
    percent_change_90d = fields.FloatField()
    percent_change_ytd = fields.FloatField(null= True)

    percent_change_24h_in_btc = fields.FloatField()

    marketcap = fields.FloatField()
    

    fully_diluted_marketcap = fields.FloatField()

    volume_24h = fields.FloatField()
    volume_7d = fields.FloatField()
    volume_30d = fields.FloatField()

    circulating_supply = fields.IntField(null=True)
    total_supply = fields.IntField(null=True)
    max_supply = fields.IntField(null=True)

    dominance = fields.FloatField()




