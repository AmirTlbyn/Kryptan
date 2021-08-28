#Django lib
from mongoengine import Document, fields


class Symbol(Document):
    id = fields.SequenceField(primary_key=True)
    name = fields.StringField(max_length = 200)
    name_fa = fields.StringField(max_length=200)
    symbol = fields.StringField(max_length= 100)

    logo_40 = fields.ReferenceField("Image")
    logo_24 = fields.ReferenceField("Image")


    description = fields.StringField()

    all_time_high = fields.FloatField()
    all_time_low = fields.FloatField()



"""

for coins api

    price_24_high
    price_24_low

    price_in_btc
    price_change_1h
    price_change_24h
    price_change_7d
    price_change_30d
    price_change_60d
    price_change_90d
    price_change_ytd

    price_in_btc_change_24h

    marketcap 
    fully_diluted_marketcap = marketcap * max_supply
    volume/mcat = volume_24h / marketcap

    volume_24h
    volume_7d
    volume_30d

    circulating_supply
    total_supply
    max_supply

    dominance


"""


