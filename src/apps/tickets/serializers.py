#Django lib
from rest_framework_mongoengine.serializers import DocumentSerializer

#Internal libs
from apps.tickets.models import TicketRoom,TicketText
from apps.users.serializers import UserMiniSerializer


class TicketRoomSerializer(DocumentSerializer):

    class Meta:
        model = TicketRoom
        fields = "__all__"
        depth = 0

class TicketRoomDeepSerializer(DocumentSerializer):
    user = UserMiniSerializer()
    
    class Meta:
        model = TicketRoom 
        fields = "__all__"
        depth = 1

class TicketTextSerializer(DocumentSerializer):

    class Meta:
        model = TicketText
        fields = "__all__"
        depth = 0

