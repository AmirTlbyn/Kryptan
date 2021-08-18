from rest_framework_mongoengine.serializers import DocumentSerializer

from users.serializers import UserMiniSerializer

from directs.models import Message ,MessageBox, AutomaticMessage

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

