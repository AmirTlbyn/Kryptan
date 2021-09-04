#Python libs
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

#Internal libs
from Kryptan.celery import app
from toolkit.toolkit import response_creator, validate_error
from apps.symbols.models import Symbol
from apps.symbols.serializers import SymbolSerializer
import repositories.symbols as repo_symbol

@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(5*60, get_50_symbols_data_every_5min.s())

@app.task(bind=True)
def get_50_symbols_data_every_5min (self):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

    parameters = {
    'start':'1',
    'limit':'100',
    'convert':'USD',
    'aux': 'cmc_rank,max_supply,circulating_supply,total_supply,market_cap_by_total_supply,volume_7d,volume_30d,is_market_cap_included_in_calc'
    }

    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': 'b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c',
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        all_data = json.loads(response.text)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        raise Exception(e)
    
    data = all_data.get("data")

    for i in range(100):
        symbol_obj, err = repo_symbol.get_symbol_object_by_name(data[i].get("name"))
        if err is not None:
            ex_data = {
                "name": data[i].get("name"),
                "symbol": data[i].get("symbol"),
                "slug": data[i].get("slug"),
                "mc_rank":data[i].get("cmc_rank")
            }
            symbol_serialized,err = repo_symbol.create_symbol_object(data=ex_data)
            if err is not None:
                return err
        else:
            symbol_serialized,er = repo_symbol.update_symbol(
                symbol_obj,
                data={"mc_rank":data[i].get("cmc_rank")})
            if err is not None:
                return err
        quotes = data[i].get("quote")
        quote = quotes.get("USD")

        quote_obj, err = repo_symbol.get_quote_obj_by_symbol_id(symbol_serialized.get("id"))
        if err is not None:
            ex_data = {
                "symbol": symbol_serialized.get("id"),
                "percent_change_30d" : quote.get("percent_change_30d"),
                "percent_change_60d" : quote.get("percent_change_60d"),
                "percent_change_90d" : quote.get("percent_change_90d"),
                "dominance" : quote.get("market_cap_dominance"),
                "circulating_supply": data[i].get("circulating_supply"),
                "total_supply" : data[i].get("total_supply"),
                "max_supply" : data[i].get("max_supply"),
                "volume_7d" : quote.get("volume_7d"),
                "volume_30d" : quote.get("volume_30d"),
                "fully_diluted_marketcap": quote.get("fully_diluted_market_cap"),
            }
            quote_serialized, err = repo_symbol.create_quote_object(data=ex_data)
            if err is not None:
                return err

        else:
            ex_data = {
                "percent_change_30d" : quote.get("percent_change_30d"),
                "percent_change_60d" : quote.get("percent_change_60d"),
                "percent_change_90d" : quote.get("percent_change_90d"),
                "dominance" : quote.get("market_cap_dominance"),
                "circulating_supply": data[i].get("circulating_supply"),
                "total_supply" : data[i].get("total_supply"),
                "max_supply" : data[i].get("max_supply"),
                "volume_7d" : quote.get("volume_7d"),
                "volume_30d" : quote.get("volume_30d"),
                "fully_diluted_marketcap": quote.get("fully_diluted_market_cap"),
            }
            quote_serialized, err = repo_symbol.update_quote(quote_obj, data=ex_data)
            if err is not None:
                return err
            

        


        
        
        

    
    





  