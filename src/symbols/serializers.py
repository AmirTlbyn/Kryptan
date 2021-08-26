from rest_framework_mongoengine.serializers import DocumentSerializer

from symbols.models import Symbol

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