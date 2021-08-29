#Django libs
from rest_framework.response import Response

#Internal libs
from toolkit.toolkit import existence_error, validate_error
from apps.symbols.models import Symbol
from apps.symbols.serializers import SymbolSerializer

#_________________________CREATE______________________________

def create_symbol_object (data: dict) -> (dict, Response):
    err = None

    symbol_serialized = SymbolSerializer(data=data)

    if not symbol_serialized.is_valid():
        err = validate_error(symbol_serialized)
        return {}, err

    symbol_serialized.save()

    return symbol_serialized.data, err