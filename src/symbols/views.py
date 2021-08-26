from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from toolkit.toolkit import existence_error, response_creator, validate_error
from toolkit.image import upload_image

from users.authentication import TokenAuthentication

from symbols.models import Symbol
from symbols.serializers import SymbolSerializer, SymbolSearchSerialized, SymbolDeepSerializer

from mongoengine.queryset.visitor import Q


class Search (APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        text = request.data.get("text")

        query = Q()

        query |= Q(
            name__icontains = text
        )

        query |= Q(
            symbol__icontains = text
        )

        query |= Q(
            name_fa__icontains = text
        )

        symbol_objs = Symbol.objects.filter(query)

        symbols_serialized = SymbolSearchSerializer(symbol_objs, many=True)

        return response_creator(data={"symbols":symbols_serialized.data})

class ShowSymbol (APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        symbol_id = request.GET.get("symbol_id")

        symbol_obj = Symbol.objects.filter(id = symbol_id).first()

        if symbol_obj is None:
            existence_error("Symbol")

        symbol_serialized = SymbolDeepSerializer(symbol_obj)

        return response_creator(data=symbol_serialized.data)


