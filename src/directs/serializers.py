from rest_framework_mongoengine.serializers import DocumentSerializer

from directs.models import Message ,Messagebox

class MessageboxSerializer(DocumentSerializer):

    class Meta:
        model = Messagebox
        fields = "__all__"
        depth = 0

class MessageboxDeepSerializer(DocumentSerializer):

    class Meta:
        model = Messagebox
        fields = "__all__"
        depth = 1

class MessageboxTwoDeepSerializer(DocumentSerializer):

    class Meta:
        model = Messagebox
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
