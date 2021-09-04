#Django lib
from rest_framework_mongoengine.serializers import DocumentSerializer

#Internal lib
from apps.symbols.models import Symbol, SymbolQuote

class SymbolSerializer(DocumentSerializer):

    class Meta:
        model = Symbol
        fields = "__all__"
        depth = 0

class SymbolSearchSerialized(DocumentSerializer):

    class Meta:
        model = Symbol
        fielda = [
            "id",
            "name",
            "name_fa",
            "symbol",
            "logo_24",
        ]   
        depth = 1   

class SymbolDeepSerializer(DocumentSerializer):

    class Meta:
        model = Symbol
        fields = "__all__"
        depth = 1

class SymbolQuoteSerializer (DocumentSerializer):

    class Meta:
        model = SymbolQuote
        fields = "__all__"
        depth = 0