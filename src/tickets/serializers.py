from rest_framework_mongoengine.serializers import DocumentSerializer
from tickets.models import TicketRoom,TicketText


class TicketRoomSerializer(DocumentSerializer):

    class Meta:
        model = TicketRoom
        fields = "__all__"
        depth = 0

class TicketRoomDeepSerializer(DocumentSerializer):

    class Meta:
        model = TicketRoom 
        fields = "__all__"
        depth = 1

class TicketTextSerializer(DocumentSerializer):

    class Meta:
        model = TicketText
        fields = "__all__"
        depth = 0

