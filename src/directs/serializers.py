from rest_framework_mongoengine.serializers import DocumentSerializer

from directs.models import Message ,MessageBox

class MessageBoxSerializer(DocumentSerializer):

    class Meta:
        model = MessageBox
        fields = "__all__"
        depth = 0

class MessageBoxDeepSerializer(DocumentSerializer):

    class Meta:
        model = MessageBox
        fields = "__all__"
        depth = 1

class MessageBoxTwoDeepSerializer(DocumentSerializer):

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

    class Meta:
        model = Message
        fields = "__all__"
        depth = 1
