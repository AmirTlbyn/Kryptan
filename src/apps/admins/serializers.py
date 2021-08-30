#Django lib
from rest_framework_mongoengine.serializers import DocumentSerializer

#Internal lib
from apps.admins.models import TetherToman

class TetherTomanSerializer(DocumentSerializer):

    class Meta:
        model = TetherToman
        fields = "__all__"
        depth = 0