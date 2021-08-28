#Django lib
from rest_framework_mongoengine.serializers import DocumentSerializer

#Internal libs
from apps.users.serializers import UserMiniSerializer
from apps.directs.models import (
    Message,
    MessageBox,
    AutomaticMessage,
    ChatRoom,
)

class MessageBoxSerializer(DocumentSerializer):

    class Meta:
        model = MessageBox
        fields = "__all__"
        depth = 0

class MessageBoxDeepSerializer(DocumentSerializer):
    
    user = UserMiniSerializer()

    class Meta:
        model = MessageBox
        fields = "__all__"
        depth = 1

class MessageBoxTwoDeepSerializer(DocumentSerializer):
    user = UserMiniSerializer()
    class Meta:
        model = MessageBox
        fields = "__all__"
        depth = 2

class MessageSerializer(DocumentSerializer):

    class Meta:
        model = Message
        fields = "__all__"
        depth = 0

class MessageDeepSerializer(DocumentSerializer):
    user = UserMiniSerializer()
    class Meta:
        model = Message
        fields = "__all__"
        depth = 1

class AutomaticMessageSerializer(DocumentSerializer):

    class Meta:
        model = AutomaticMessage
        fields = "__all__"
        depth = 0

class ChatRoomSerializer(DocumentSerializer):

    class Meta:
        model = ChatRoom
        fields = "__all__"
        depth = 0

class ChatRoomDeepSerializer(DocumentSerializer):

    users = UserMiniSerializer(many=True)

    class Meta:
        model = ChatRoom
        fields = "__all__"
        depth = 1
