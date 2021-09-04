#Django libs
from rest_framework.response import Response

#Internal libs
from toolkit.toolkit import existence_error, validate_error
from apps.symbols.models import Symbol, SymbolQuote
from apps.symbols.serializers import SymbolSerializer, SymbolQuoteSerializer

#_________________________CREATE______________________________

def create_symbol_object (data: dict) -> (dict, Response):
    err = None

    symbol_serialized = SymbolSerializer(data=data)

    if not symbol_serialized.is_valid():
        err = validate_error(symbol_serialized)
        return {}, err

    symbol_serialized.save()

    return symbol_serialized.data, err

def create_quote_object (data: dict) -> (dict, Response):
    err = None

    quote_serialized = SymbolQuoteSerializer(data=data)

    if not quote_serialized.is_valid():
        err = validate_error(quote_serialized)

        return {}, err

    quote_serialized.save()

    return quote_serialized.data, err

    

#_________________________GET______________________________

def get_symbol_object_by_name (name: str) -> (object, Response):
    err = None

    symbol_obj = Symbol.objects.filter(name=name).first()
    if symbol_obj is None:
        err = existence_error("Symbol")
        return None, err

    return symbol_obj, err

def get_symbol_data_by_obj (symbol_obj) -> dict:
    symbol_serialized = SymbolSerializer(symbol_obj)

    return symbol_serialized.data

def get_quote_obj_by_symbol_id (symbol_id: int) -> (object, Response):
    err = None

    quote_obj = SymbolQuote.objects.filter(symbol = symbol_id).first()

    if quote_obj is None:
        err = existence_error("SymbolQuote")

        return None, err

    return quote_obj, err
def get_quote_data_by_obj (quote_obj) -> dict:
    quote_serialized = SymbolQuoteSerializer(quote_obj)

    return quote_serialized.data

#_________________________UPDATE______________________________

def update_symbol(symbol_obj, data) -> (dict, Response):
    err = None

    symbol_serialized = SymbolSerializer(
        symbol_obj,
        data=data,
        partial=True
    )
    if not symbol_serialized.is_valid():
        err = validate_error(symbol_serialized)

        return {}, err

    symbol_serialized.save()

    return symbol_serialized.data, err

def update_quote(quote_obj, data) -> (dict, Response):
    err = None

    quote_serialized = SymbolQuoteSerializer(
        quote_obj,
        data=data,
        partial=True
    )

    if not quote_serialized.is_valid():
        err = validate_error(quote_serialized)

        return {}, err

    quote_serialized.save()
    return quote_serialized.data, err